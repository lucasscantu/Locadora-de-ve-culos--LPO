import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from model.locacao import Locacao
from model.veiculo import VeiculoFactory, Categoria
from model.ExcecoesPersonalizadas import DataInvalidaError
from model.LocacaoStrategy import *
from model.decoradores import GPSDecorator, SeguroTerceirosDecorator

print("\n1. Testando tipos válidos na fábrica:")
try:
    motorhome = VeiculoFactory.criar_veiculo("motorhome", "XYZ9A99", Categoria.EXECUTIVO, taxa_diaria=200.0)
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1D34", Categoria.ECONOMICO, taxa_diaria=150.0)
    print("Veículos criados com sucesso via Factory")
except Exception as e:
    raise Exception(f"Erro ao criar veículos via Factory: {e}")

# Tratamento de tipo inválido na fábrica
print("\n2. Testando tipo inválido na fábrica:")
try:
    moto = VeiculoFactory.criar_veiculo("moto", "DEF2G56", Categoria.ECONOMICO, taxa_diaria=50.0)
    print("Erro: Deveria ter lançado ValueError para tipo inválido")
except ValueError as e:
    #raise Exception(f"Exceção capturada corretamente: {e}")
    print(f"Exceção capturada corretamente: {e}")

# Cálculo com múltiplos dias
print("\n3. Testando cálculo com múltiplos dias (3 dias):")
try:
    data_inicio = date(2026, 3, 1)
    data_fim = date(2026, 3, 4) # 3 dias de diferença
    # Cálculo esperado Carro: 3 * 150 (taxa_diaria) + 50 (seguro) = 500
    locacao_dias = Locacao(veiculo=carro, data_inicio=data_inicio, data_fim=data_fim, estrategia=CalculoVIPStrategy())
    valor = locacao_dias.calcular_valor_locacao()
    diferenca_datas = data_fim - data_inicio
    print(f"Cálculo para {diferenca_datas.days} dias: R$ {valor}")
except Exception as e:
    print(f"Erro no cálculo de múltiplos dias: {e}")

# Cálculo com devolução no mesmo dia
print("\n4. Testando cálculo com devolução no mesmo dia (mínimo 1 diária):")
try:
    locacao_mesmo_dia = Locacao(veiculo=motorhome, data_inicio=date.today(), data_fim=date.today())
    # Cálculo esperado Motorhome: 1 * 200 (taxa) + 120 (seguro) = 320
    valor = locacao_mesmo_dia.calcular_valor_locacao()
    print(f"Cálculo locação para o mesmo dia: R$ {valor}")
except Exception as e:
    print(f"Erro no cálculo de mesmo dia: {e}")

# Datas inválidas (início > fim e não permitir dias negativos)
print("\n5. Testando datas inválidas (Início maior que Fim):")
try:
    locacao_invalida = Locacao(veiculo=carro, data_inicio=date(2026, 3, 5), data_fim=date(2026, 3, 1))
    locacao_invalida.calcular_valor_locacao()
    print("Erro: Deveria ter lançado DataInvalidaError para datas inválidas")
except DataInvalidaError as e:
    print(f"Exceção capturada corretamente: {e}")

# Garantir que taxa diária e seguro sejam valores válidos
print("\n6. Testando validação de taxa diária e seguro:")
try:
    carro_invalido = VeiculoFactory.criar_veiculo("carro", "HJI3K45", Categoria.ECONOMICO, taxa_diaria=-50.0)
    locacao_taxa_invalida = Locacao(veiculo=carro_invalido, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 2))
    locacao_taxa_invalida.calcular_valor_locacao()
    print("Erro: Deveria ter lançado ValueError para taxa diária inválida")
except ValueError as e:
    print(f"Exceção capturada corretamente: {e}")

print("\n--- TUTORIAL 3.1: TESTANDO O PADRÃO STRATEGY ---")
data_in = date(2026, 3, 10)
data_out = date(2026, 3, 15)
locacao_normal = Locacao(veiculo=carro, data_inicio=data_in, data_fim=data_out)
print(f"Valor Padrão: R$ {locacao_normal.calcular_valor_locacao()}")

locacao_vip = Locacao(veiculo=carro, data_inicio=data_in, data_fim=data_out, estrategia=CalculoVIPStrategy())
print(f"Valor Cliente VIP: R$ {locacao_vip.calcular_valor_locacao()}")

print("\n--- TUTORIAL 3.2: TESTANDO O PADRÃO STATE RESTRITIVO ---")
carro_estado = VeiculoFactory.criar_veiculo("carro", "HJI3K45", Categoria.ECONOMICO, taxa_diaria=100.0)
carro_estado.tentar_alugar() # OK - Transitará
carro_estado.tentar_alugar() # Erro Interativo ("Já está alugado!")
carro_estado.reter_na_frota_pra_conserto() # Bloqueado
carro_estado.tentar_devolver() # Ok (Retorna)
carro_estado.reter_na_frota_pra_conserto() # Ok 
carro_estado.tentar_alugar() # Falha! Está em Manutenção.

print("\n--- TUTORIAL 3.3: TESTANDO O PADRÃO DECORATOR ---")
locacao_base = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 5))
print(f"Valor Base (somente Diária + Seguro Base): R$ {locacao_base.calcular_valor_locacao()}")

locacao_com_gps = GPSDecorator(locacao_base)
print(f"Valor somado do pacote + GPS: R$ {locacao_com_gps.calcular_valor_locacao()}")

locacao_vip_top = SeguroTerceirosDecorator(locacao_com_gps)
print(f"Valor pacote completão (Base + GPS + Seg.Terceiros): R$ {locacao_vip_top.calcular_valor_locacao()}")