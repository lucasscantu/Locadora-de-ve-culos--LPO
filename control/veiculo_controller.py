from dao.veiculo_dao import VeiculoDAO
from model.veiculo import *

class VeiculoController:
    def __init__(self):
        self.veiculo_dao = VeiculoDAO()
        
    def salvar_veiculo(self, placa: str, tipo_str: str, categoria_str: str, taxa_str: str):
        if not placa or not tipo_str or not categoria_str or not taxa_str:
            return False, "Preencha todos os campos"
        
        try:
            taxa_num = float(taxa_str.replace(',', '.'))
            if taxa_num <= 0:
                return False, "A taxa diária deve ser um valor positivo"
            
            veiculo_existente = self.veiculo_dao.buscar_por_placa(placa)
            if veiculo_existente:
                return False, f"Veiculo com placa {placa} já está cadastrado"
            
            categoria_enum = Categoria[categoria_str.upper()]
            
            # utilizar o factory para criar o objeto
            novo_veiculo = VeiculoFactory.criar_veiculo(tipo_str.strip().lower(), placa.upper(), 
                                                        categoria_enum, taxa_num)
        
            # salvar no BD
            sucesso, msg = self.veiculo_dao.salvar(novo_veiculo)
            
            return sucesso, msg

        except KeyError:
            return False, "Categoria inválida. Use ECONOMICO ou EXECUTIVO"
        except ValueError as e2:
            return False, f"Valor númerico inválido. Erro: {e2}"
        except Exception as e3:
            return False, f"Erro inesperado: {e3}"

    def listar_veiculos(self):
        try:
            return self.veiculo_dao.listar_todos()

        except Exception as e:
            print(f"Erro ao listar veículos: {e}")
            return None            
    
    def buscar_por_placa(self, placa: str):
        try:
            return self.veiculo_dao.buscar_por_placa(placa.strip().upper())

        except Exception as e:
            print(f"Erro ao buscar veículo: {e}")
            return None   
        
    def remover_veiculo(self, placa: str):
        if not placa:
            return False, "Placa não informada"
        try:
            return self.veiculo_dao.remover(placa.strip().upper())
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def atualizar_veiculo(self, placa: str, tipo_str: str, categoria_str: str, taxa_str: str):
        if not placa or not tipo_str or not categoria_str or not taxa_str:
            return False, "Preencha todos os campos"
        
        try:
            taxa_num = float(taxa_str.replace(',', '.'))
            if taxa_num <= 0:
                return False, "A taxa diária deve ser um valor positivo"
            
            veiculo_existente = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo_existente:
                return False, f"Veiculo com placa {placa} não foi encontrado"
            
            categoria_enum = Categoria[categoria_str.upper()]
            
            # utilizar o factory para criar o objeto com os novos dados
            veiculo_atualizado = VeiculoFactory.criar_veiculo(tipo_str.strip().lower(), placa.upper(), 
                                                        categoria_enum, taxa_num)
        
            # atualizar no BD
            sucesso, msg = self.veiculo_dao.atualizar(veiculo_atualizado)
            
            return sucesso, msg

        except KeyError:
            return False, "Categoria inválida. Use ECONOMICO, EXECUTIVO ou LUXO"
        except ValueError as e2:
            return False, f"Valor numérico inválido. Erro: {e2}"
        except Exception as e3:
            return False, f"Erro inesperado: {e3}"   