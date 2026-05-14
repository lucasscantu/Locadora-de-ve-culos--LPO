from datetime import date, datetime

from dao.locacao_dao import LocacaoDAO
from dao.veiculo_dao import VeiculoDAO
from model.locacao import Locacao, StatusLocacao
from model.veiculo import Categoria
from model.ExcecoesPersonalizadas import DataInvalidaError


class LocacaoController:
    """
    Controller responsável por intermediar a comunicação entre a camada
    de visão (Tkinter) e a camada de persistência (DAO), aplicando as
    regras de negócio da locação.
    """

    FORMATO_DATA = "%Y-%m-%d"

    def __init__(self):
        self.locacao_dao = LocacaoDAO()
        self.veiculo_dao = VeiculoDAO()

    # ------------------------------------------------------------------
    # Utilidade: parsing de data string -> date
    # ------------------------------------------------------------------
    @classmethod
    def _parse_data(cls, valor, obrigatoria=True, nome_campo="data"):
        """Converte uma string YYYY-MM-DD em date. Retorna None se vazio e não obrigatório."""
        if valor is None or (isinstance(valor, str) and valor.strip() == ""):
            if obrigatoria:
                raise DataInvalidaError(f"Campo '{nome_campo}' é obrigatório.")
            return None
        if isinstance(valor, date):
            return valor
        try:
            return datetime.strptime(valor.strip(), cls.FORMATO_DATA).date()
        except ValueError:
            raise DataInvalidaError(
                f"Formato de {nome_campo} inválido. Use AAAA-MM-DD (ex: 2026-05-17)."
            )

    # ------------------------------------------------------------------
    # CRUD básico
    # ------------------------------------------------------------------
    def listar_locacoes(self):
        try:
            return self.locacao_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []

    def buscar_por_id(self, id_locacao):
        try:
            return self.locacao_dao.buscar_por_id(int(id_locacao))
        except Exception as e:
            print(f"Erro ao buscar locação: {e}")
            return None

    def remover_locacao(self, id_locacao):
        if id_locacao is None:
            return False, "ID da locação não informado."
        try:
            return self.locacao_dao.remover(int(id_locacao))
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    # ------------------------------------------------------------------
    # Criar locação (usado pelas duas telas)
    # ------------------------------------------------------------------
    def salvar_locacao(self,
                       placa: str,
                       data_inicio_str: str,
                       data_fim_str: str,
                       status_str: str = "reservado",
                       valor_total=None,
                       modo_admin: bool = False):
        """
        Cria e persiste uma nova locação.

        Em modo USUÁRIO (modo_admin=False):
          - O status é sempre "reservado" (regra de negócio).
          - data_inicio deve ser >= hoje.
          - O veículo precisa estar disponível no período.

        Em modo ADMIN (modo_admin=True):
          - Pode informar qualquer status válido.
          - Datas passadas são permitidas (registro histórico).
          - A única regra obrigatória é: data_inicio <= data_fim.
        """
        if not placa:
            return False, "Selecione um veículo.", None

        try:
            data_inicio = self._parse_data(data_inicio_str, obrigatoria=True,
                                           nome_campo="data de início")
            data_fim = self._parse_data(data_fim_str, obrigatoria=False,
                                        nome_campo="data de fim")

            if data_fim is not None and data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim.", None

            if not modo_admin:
                # Validações específicas da tela do usuário
                if data_inicio < date.today():
                    return False, "Data de início não pode ser anterior à data de hoje.", None
                status = StatusLocacao.RESERVADO
            else:
                status = StatusLocacao(status_str.lower()) if status_str else StatusLocacao.RESERVADO

            veiculo = self.veiculo_dao.buscar_por_placa(placa.strip().upper())
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado.", None

            # Em modo usuário sempre validamos disponibilidade
            # Em modo admin assumimos que o admin sabe o que está fazendo (registro histórico)
            if not modo_admin:
                disponiveis = self.locacao_dao.buscar_veiculos_disponiveis(
                    data_inicio, data_fim if data_fim else data_inicio, None
                )
                placas_disponiveis = [v.placa for v in disponiveis]
                if veiculo.placa not in placas_disponiveis:
                    return False, "Veículo não está disponível no período informado.", None

            valor_num = None
            if valor_total is not None and str(valor_total).strip() != "":
                try:
                    valor_num = float(str(valor_total).replace(',', '.'))
                except ValueError:
                    return False, "Valor total inválido.", None

            nova_locacao = Locacao(
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                valor_total=valor_num
            )

            sucesso, msg = self.locacao_dao.salvar(nova_locacao)
            return sucesso, msg, nova_locacao

        except DataInvalidaError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Erro inesperado: {e}", None

    # ------------------------------------------------------------------
    # Atualizar (usado pela tela admin)
    # ------------------------------------------------------------------
    def atualizar_locacao(self,
                          id_locacao,
                          placa: str,
                          data_inicio_str: str,
                          data_fim_str: str,
                          status_str: str,
                          valor_total=None):
        """Atualiza uma locação existente (acesso restrito do administrador)."""
        if id_locacao is None:
            return False, "ID da locação é obrigatório."

        try:
            locacao_existente = self.locacao_dao.buscar_por_id(int(id_locacao))
            if not locacao_existente:
                return False, f"Locação ID {id_locacao} não encontrada."

            data_inicio = self._parse_data(data_inicio_str, obrigatoria=True,
                                           nome_campo="data de início")
            data_fim = self._parse_data(data_fim_str, obrigatoria=False,
                                        nome_campo="data de fim")

            if data_fim is not None and data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            veiculo = self.veiculo_dao.buscar_por_placa(placa.strip().upper())
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado."

            try:
                novo_status = StatusLocacao(status_str.lower()) if status_str else locacao_existente.status
            except ValueError:
                return False, f"Status inválido: {status_str}"

            valor_num = None
            if valor_total is not None and str(valor_total).strip() != "":
                try:
                    valor_num = float(str(valor_total).replace(',', '.'))
                except ValueError:
                    return False, "Valor total inválido."

            locacao_atualizada = Locacao(
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=novo_status,
                id_locacao=int(id_locacao),
                valor_total=valor_num
            )

            return self.locacao_dao.atualizar(locacao_atualizada)

        except DataInvalidaError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    # ------------------------------------------------------------------
    # Ações operacionais da tela do USUÁRIO
    # ------------------------------------------------------------------
    def locar(self, id_locacao):
        """
        Muda o status de 'reservado' para 'locado'.
        Se a data de início da locação for diferente da data de hoje,
        atualiza data_inicio para a data atual.
        """
        locacao = self.locacao_dao.buscar_por_id(int(id_locacao))
        if not locacao:
            return False, "Locação não encontrada.", None

        if locacao.status != StatusLocacao.RESERVADO:
            return False, "Apenas locações com status 'reservado' podem ser locadas.", None

        hoje = date.today()
        if locacao.data_inicio != hoje:
            # Garante consistência entre datas (caso data_fim seja anterior a hoje)
            if locacao.data_fim is not None and locacao.data_fim < hoje:
                return False, ("Não é possível retirar o veículo hoje: a data de fim "
                              "prevista da reserva já passou."), None
            locacao.data_inicio = hoje

        locacao.status = StatusLocacao.LOCADO

        sucesso, msg = self.locacao_dao.atualizar(locacao)
        if sucesso:
            return True, "Veículo locado com sucesso.", locacao
        return False, msg, None

    def devolver(self, id_locacao):
        """
        Devolução: muda o status para 'devolvido', data_fim = hoje,
        calcula valor final e retorna info da devolução.
        """
        locacao = self.locacao_dao.buscar_por_id(int(id_locacao))
        if not locacao:
            return False, "Locação não encontrada.", None

        if locacao.status != StatusLocacao.LOCADO:
            return False, "Só é possível devolver locações com status 'locado'.", None

        hoje = date.today()
        if locacao.data_inicio >= hoje:
            return False, ("Não é possível devolver: a data de início "
                           "deve ser anterior à data atual."), None

        locacao.data_fim = hoje
        valor_final = locacao.calcular_valor_locacao()
        locacao.valor_total = valor_final
        locacao.status = StatusLocacao.DEVOLVIDO

        sucesso, msg = self.locacao_dao.atualizar(locacao)
        if sucesso:
            info = {
                "data_inicio": locacao.data_inicio,
                "data_devolucao": locacao.data_fim,
                "numero_diarias": locacao.numero_diarias(),
                "valor_total": valor_final
            }
            return True, "Devolução registrada com sucesso.", info
        return False, msg, None

    def cancelar(self, id_locacao):
        """Cancela uma locação. Permitido apenas para status 'reservado'."""
        locacao = self.locacao_dao.buscar_por_id(int(id_locacao))
        if not locacao:
            return False, "Locação não encontrada."

        if locacao.status != StatusLocacao.RESERVADO:
            return False, "Apenas locações com status 'reservado' podem ser canceladas."

        locacao.status = StatusLocacao.CANCELADO
        return self.locacao_dao.atualizar(locacao)

    # ------------------------------------------------------------------
    # Veículos disponíveis (para os formulários de criação)
    # ------------------------------------------------------------------
    def buscar_veiculos_disponiveis(self, data_inicio_str, data_fim_str, categoria_str=None):
        """
        Wrapper para o DAO que faz parsing das datas e categoria.
        Retorna (lista_de_veiculos, mensagem_erro_ou_None).
        """
        try:
            data_inicio = self._parse_data(data_inicio_str, obrigatoria=True,
                                           nome_campo="data de início")
            data_fim = self._parse_data(data_fim_str, obrigatoria=False,
                                        nome_campo="data de fim")
            if data_fim is None:
                data_fim = data_inicio
            if data_inicio > data_fim:
                return [], "Data de início deve ser anterior ou igual à data de fim."

            categoria = None
            if categoria_str and categoria_str.strip():
                try:
                    categoria = Categoria[categoria_str.upper()]
                except KeyError:
                    return [], f"Categoria inválida: {categoria_str}"

            veiculos = self.locacao_dao.buscar_veiculos_disponiveis(data_inicio, data_fim, categoria)
            return veiculos, None

        except DataInvalidaError as e:
            return [], str(e)
        except Exception as e:
            return [], f"Erro inesperado: {e}"
