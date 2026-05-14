import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from model.veiculo import Veiculo, VeiculoFactory, Categoria
from model.locacao import Locacao, StatusLocacao
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class LocacaoDAO(GenericDAO):
    """
    DAO responsável pela persistência das locações em PostgreSQL.

    Esquema esperado da tabela tb_locacoes:
        loc_id           SERIAL PRIMARY KEY,
        vei_placa        VARCHAR(7) NOT NULL REFERENCES tb_veiculos(vei_placa),
        loc_data_inicio  DATE NOT NULL,
        loc_data_fim     DATE,
        loc_status       VARCHAR(20) NOT NULL DEFAULT 'reservado',
        loc_valor_total  NUMERIC(10,2)

    O script schema.sql na pasta dao/ pode ser executado uma vez para criar a tabela.
    """

    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    # ------------------------------------------------------------------
    # CRUD básico (GenericDAO)
    # ------------------------------------------------------------------
    def salvar(self, locacao: Locacao):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """INSERT INTO tb_locacoes
                       (vei_placa, loc_data_inicio, loc_data_fim, loc_status, loc_valor_total)
                       VALUES (%s, %s, %s, %s, %s)
                       RETURNING loc_id"""
            cursor.execute(query, (
                locacao.veiculo.placa,
                locacao.data_inicio,
                locacao.data_fim,
                locacao.status.value,
                locacao.valor_total
            ))
            novo_id = cursor.fetchone()[0]
            locacao.id = novo_id
            self.conexao.commit()
            return True, f"Locação cadastrada com sucesso (ID {novo_id})"

        except Exception as e:
            print(f"Erro ao inserir locação: {e}")
            self.conexao.rollback()
            return False, f"Erro ao inserir locação: {e}"

        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """SELECT l.loc_id, l.vei_placa, l.loc_data_inicio, l.loc_data_fim,
                              l.loc_status, l.loc_valor_total,
                              v.vei_tipo, v.vei_categoria, v.vei_taxa_diaria
                       FROM tb_locacoes l
                       INNER JOIN tb_veiculos v ON v.vei_placa = l.vei_placa
                       ORDER BY l.loc_id DESC"""
            cursor.execute(query)
            linhas = cursor.fetchall()
            return [self._linha_para_locacao(linha) for linha in linhas]

        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    def remover(self, id_objeto):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = "DELETE FROM tb_locacoes WHERE loc_id = %s"
            cursor.execute(query, (id_objeto,))
            self.conexao.commit()
            if cursor.rowcount == 0:
                return False, f"Locação ID {id_objeto} não encontrada"
            return True, "Locação removida com sucesso"

        except Exception as e:
            print(f"Erro ao remover locação ID {id_objeto}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao remover locação: {e}"

        finally:
            if cursor:
                cursor.close()

    def atualizar(self, locacao: Locacao):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        if locacao.id is None:
            return False, "ID da locação é obrigatório para atualização."

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """UPDATE tb_locacoes
                       SET vei_placa = %s,
                           loc_data_inicio = %s,
                           loc_data_fim = %s,
                           loc_status = %s,
                           loc_valor_total = %s
                       WHERE loc_id = %s"""
            cursor.execute(query, (
                locacao.veiculo.placa,
                locacao.data_inicio,
                locacao.data_fim,
                locacao.status.value,
                locacao.valor_total,
                locacao.id
            ))
            self.conexao.commit()
            return True, "Locação atualizada com sucesso"

        except Exception as e:
            print(f"Erro ao atualizar locação ID {locacao.id}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar locação: {e}"

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------------
    def buscar_por_id(self, id_locacao: int):
        if not self.conexao:
            return None

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """SELECT l.loc_id, l.vei_placa, l.loc_data_inicio, l.loc_data_fim,
                              l.loc_status, l.loc_valor_total,
                              v.vei_tipo, v.vei_categoria, v.vei_taxa_diaria
                       FROM tb_locacoes l
                       INNER JOIN tb_veiculos v ON v.vei_placa = l.vei_placa
                       WHERE l.loc_id = %s"""
            cursor.execute(query, (id_locacao,))
            linha = cursor.fetchone()
            if linha:
                return self._linha_para_locacao(linha)
            return None

        except Exception as e:
            print(f"Erro ao buscar locação ID {id_locacao}: {e}")
            return None

        finally:
            if cursor:
                cursor.close()

    def buscar_veiculos_disponiveis(self, data_inicio: date, data_fim: date, categoria: Categoria = None):
        """
        Retorna a lista de veículos disponíveis no período informado.

        Um veículo é considerado indisponível quando já possui uma locação
        com status 'reservado' ou 'locado' cuja faixa de datas intersecta
        com a faixa [data_inicio, data_fim].

        Critério de sobreposição: existe sobreposição entre [A1, A2] e [B1, B2]
        quando A1 <= B2 E B1 <= A2 (considerando data_fim NULL como "em aberto").

        Se a categoria for informada, filtra também pela categoria do veículo.
        """
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()

            params = [data_fim, data_inicio]

            query = """
                SELECT v.vei_tipo, v.vei_placa, v.vei_categoria, v.vei_taxa_diaria
                FROM tb_veiculos v
                WHERE v.vei_placa NOT IN (
                    SELECT l.vei_placa
                    FROM tb_locacoes l
                    WHERE l.loc_status IN ('reservado', 'locado')
                      AND l.loc_data_inicio <= %s
                      AND COALESCE(l.loc_data_fim, %s) >= %s
                )
            """
            # Para o COALESCE, se data_fim é NULL, considera-se a própria data_inicio
            # da nova locação - assim qualquer locação aberta bloqueia o veículo.
            params = [data_fim, data_inicio, data_inicio]

            if categoria is not None:
                query += " AND v.vei_categoria = %s"
                params.append(categoria.value)

            query += " ORDER BY v.vei_placa"

            cursor.execute(query, params)
            linhas = cursor.fetchall()

            veiculos = []
            for cada_linha in linhas:
                obj = VeiculoFactory.criar_veiculo(
                    cada_linha[0],
                    cada_linha[1],
                    Categoria(cada_linha[2]),
                    float(cada_linha[3])
                )
                veiculos.append(obj)
            return veiculos

        except Exception as e:
            print(f"Erro ao buscar veículos disponíveis: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    # ------------------------------------------------------------------
    # Conversão de linha do BD em objeto Locacao
    # ------------------------------------------------------------------
    def _linha_para_locacao(self, linha):
        """
        Converte uma tupla retornada pelo BD em um objeto Locacao.
        Espera a ordem:
        (loc_id, vei_placa, loc_data_inicio, loc_data_fim, loc_status,
         loc_valor_total, vei_tipo, vei_categoria, vei_taxa_diaria)
        """
        (loc_id, vei_placa, data_inicio, data_fim, status_str,
         valor_total, vei_tipo, vei_categoria, vei_taxa) = linha

        veiculo = VeiculoFactory.criar_veiculo(
            vei_tipo, vei_placa, Categoria(vei_categoria), float(vei_taxa)
        )

        locacao = Locacao(
            veiculo=veiculo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=StatusLocacao(status_str),
            id_locacao=loc_id,
            valor_total=float(valor_total) if valor_total is not None else None
        )
        return locacao
