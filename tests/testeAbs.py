import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.LocacaoStrategy import *
from model.veiculo import *

carro = VeiculoFactory.criar_veiculo("carro", "ABC1D23", Categoria.ECONOMICO, 200)
locacao = CalculoVIPStrategy()
valor = locacao.calcular_diarias(carro, 3)

print(f"Valor das diárias: {valor}")