from datetime import date
from model.veiculo import Categoria
from model.veiculo_factory import VeiculoFactory
from model.locacao import Locacao
from model.ExcecoesPersonalizadas import (
    PlacaInvalidaError,
    DataInvalidaError,
    TipoVeiculoInvalidoError,
)


def separador(titulo):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print('='*50)


def teste_criacao_via_factory():
    separador("TESTE 1 – Criação via Factory")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150, categoria=Categoria.ECONOMICO)
    print(f"[OK] Carro criado: placa={carro.placa}, taxa_diaria={carro.taxa_diaria}, seguro={carro.valor_seguro}")
    mh = VeiculoFactory.criar_veiculo("motorhome", "XYZ9999", taxa_diaria=300, categoria=Categoria.EXECUTIVO)
    print(f"[OK] Motorhome criado: placa={mh.placa}, taxa_diaria={mh.taxa_diaria}, seguro={mh.valor_seguro}")
    carro2 = VeiculoFactory.criar_veiculo("Carro", "DEF5678", taxa_diaria=200)
    print(f"[OK] Factory aceita tipo com capitalização diferente: {carro2.placa}")


def teste_calculo_multiplos_dias():
    separador("TESTE 2 – Cálculo com múltiplos dias")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 4))
    valor = locacao.calcular_valor_locacao()
    esperado = (3 * 150) + 50
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] 3 dias x R$150 + seguro R$50 = R${valor:.2f}")
    mh = VeiculoFactory.criar_veiculo("motorhome", "XYZ9999", taxa_diaria=300)
    locacao2 = Locacao(veiculo=mh, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 6))
    valor2 = locacao2.calcular_valor_locacao()
    esperado2 = (5 * 300) + 120
    assert valor2 == esperado2, f"Esperado {esperado2}, obtido {valor2}"
    print(f"[OK] 5 dias x R$300 + seguro R$120 = R${valor2:.2f}")


def teste_devolucao_mesmo_dia():
    separador("TESTE 3 – Devolução no mesmo dia (mínimo 1 diária)")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 5), data_fim=date(2026, 3, 5))
    valor = locacao.calcular_valor_locacao()
    esperado = (1 * 150) + 50
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] Devolução no mesmo dia -> 1 diária: R${valor:.2f}")


def teste_tipo_invalido_na_fabrica():
    separador("TESTE 4 – Tipo inválido na Factory")
    try:
        VeiculoFactory.criar_veiculo("bicicleta", "ABC1234", taxa_diaria=50)
        print("[FALHOU] Deveria ter lançado TipoVeiculoInvalidoError")
    except TipoVeiculoInvalidoError as e:
        print(f"[OK] TipoVeiculoInvalidoError capturado: {e}")


def teste_placa_invalida():
    separador("TESTE 5 – Validações de placa inválida")
    casos = [
        ("AB12345", "menos de 3 letras no inicio"),
        ("ABCD234", "4 letras no inicio"),
        ("ABC123",  "apenas 6 caracteres"),
        ("ABC12345","8 caracteres"),
    ]
    for placa, descricao in casos:
        try:
            VeiculoFactory.criar_veiculo("carro", placa, taxa_diaria=100)
            print(f"[FALHOU] Placa '{placa}' deveria ser invalida ({descricao})")
        except PlacaInvalidaError as e:
            print(f"[OK] PlacaInvalidaError para '{placa}' ({descricao}): {e}")


def teste_data_invalida():
    separador("TESTE 6 – Data fim anterior à data início")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    try:
        locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 10), data_fim=date(2026, 3, 5))
        locacao.calcular_valor_locacao()
        print("[FALHOU] Deveria ter lançado DataInvalidaError")
    except DataInvalidaError as e:
        print(f"[OK] DataInvalidaError capturado: {e}")


def teste_sem_datas():
    separador("TESTE 7 – Calcular locação sem informar datas")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    locacao = Locacao(veiculo=carro, data_inicio=None, data_fim=None)
    try:
        locacao.calcular_valor_locacao()
        print("[FALHOU] Deveria ter lançado DataInvalidaError")
    except DataInvalidaError as e:
        print(f"[OK] DataInvalidaError capturado: {e}")


if __name__ == "__main__":
    teste_criacao_via_factory()
    teste_calculo_multiplos_dias()
    teste_devolucao_mesmo_dia()
    teste_tipo_invalido_na_fabrica()
    teste_placa_invalida()
    teste_data_invalida()
    teste_sem_datas()
    print("\n" + "="*50)
    print("  TODOS OS TESTES CONCLUÍDOS")
    print("="*50)
