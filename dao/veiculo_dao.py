import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.veiculo import *
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO

class VeiculoDAO(GenericDAO):
    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()
        
    def salvar(self, objeto_veiculo:Veiculo):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")
        
        try:
            cursor = self.conexao.cursor()
            query = """INSERT INTO tb_veiculos 
            (vei_placa, vei_categoria, vei_taxa_diaria, vei_estado_atual, vei_tipo) 
            VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (objeto_veiculo.placa,
                                   objeto_veiculo.categoria.value,
                                   objeto_veiculo.taxa_diaria,
                                   objeto_veiculo.estado_atual.__class__.__name__,
                                   objeto_veiculo.__class__.__name__))
            self.conexao.commit()
            return True, "Veículo cadastrado com sucesso"
                                
        except Exception as e:
            print(f"Erro ao inserir veículo: {objeto_veiculo.placa}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao inserir veículo: {objeto_veiculo.placa}: {e}"
        
        finally:
            if cursor:
                cursor.close()
                
    def listar_todos(self):
        if not self.conexao:
            return []
        
        try:
            cursor = self.conexao.cursor()
            query = """SELECT vei_tipo, vei_placa, vei_categoria, vei_taxa_diaria
            FROM tb_veiculos
            """
            cursor.execute(query)
            linhas = cursor.fetchall()
            veiculos = []
            for cada_linha in linhas:
                # Converte a string vinda do BD ("ECONOMICO"/"EXECUTIVO") para o enum Categoria,
                # garantindo que o atributo .categoria seja sempre uma instância de Categoria
                # (necessário em telas que usam veiculo.categoria.name).
                categoria_enum = Categoria(cada_linha[2])
                obj = VeiculoFactory.criar_veiculo(cada_linha[0], cada_linha[1], categoria_enum, float(cada_linha[3]))
                veiculos.append(obj)
            
            return veiculos
                                
        except Exception as e:
            print(f"Erro ao buscar veículos: {e}")
            return []
        
        finally:
            if cursor:
                cursor.close()
        
        
    
    def remover(self, id_objeto: str):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        
        try:
            cursor = self.conexao.cursor()
            query = "DELETE FROM tb_veiculos WHERE vei_placa = %s"
            cursor.execute(query, (id_objeto,))
            self.conexao.commit()
            return True, "Veículo removido com sucesso"
            
        except Exception as e:
            print(f"Erro ao remover veículo: {id_objeto}. Erro: {e}")
            self.conexao.rollback()
            return False, f"Erro ao remover veículo: {id_objeto}: {e}"
        
        finally:
            if cursor:
                cursor.close()
    
    def atualizar(self, objeto: Veiculo):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        
        try:
            cursor = self.conexao.cursor()
            query = """UPDATE tb_veiculos 
                    SET vei_categoria = %s, vei_taxa_diaria = %s, vei_estado_atual = %s, vei_tipo = %s 
                    WHERE vei_placa = %s"""
            cursor.execute(query, (objeto.categoria.value,
                                   objeto.taxa_diaria,
                                   objeto.estado_atual.__class__.__name__,
                                   objeto.__class__.__name__,
                                   objeto.placa))
            self.conexao.commit()
            return True, "Veículo atualizado com sucesso"
            
        except Exception as e:
            print(f"Erro ao atualizar veículo: {objeto.placa}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar veículo: {objeto.placa}: {e}"
        
        finally:
            if cursor:
                cursor.close()
    
    def buscar_por_placa(self, placa: str):
        if not self.conexao:
            return []
        
        try:
            cursor = self.conexao.cursor()
            query = """select vei_tipo, vei_placa, vei_categoria, vei_taxa_diaria
                    FROM tb_veiculos
                    WHERE vei_placa = %s"""
            cursor.execute(query, (placa,))
            linha = cursor.fetchone()
            
            if linha: 
                # Converte a string vinda do BD para o enum Categoria, mantendo a consistência
                # do modelo em toda a aplicação.
                categoria_enum = Categoria(linha[2])
                return VeiculoFactory.criar_veiculo(linha[0], linha[1], categoria_enum, float(linha[3]))
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar veículo: {placa}. Erro: {e}")
        
        finally:
            if cursor:
                cursor.close()