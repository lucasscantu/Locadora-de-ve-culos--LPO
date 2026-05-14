import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.veiculo import *
from dao.veiculo_dao import VeiculoDAO

dao = VeiculoDAO()

novo_carro = VeiculoFactory.criar_veiculo("carro", "ABC1D34", Categoria.ECONOMICO, 150.00)
sucesso, msg = dao.salvar(novo_carro)
print(msg)

lista_veiculos = dao.listar_todos()
print(f"Total de Veículos cadastrados: {len(lista_veiculos)}")
for obj in lista_veiculos:
    print(obj.placa)