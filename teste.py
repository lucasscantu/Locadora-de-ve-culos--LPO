from datetime import date
from model.veiculo import Categoria
from model.veiculo_factory import VeiculoFactory
from model.locacao import Locacao
from model.strategy import CalculoPadraoStrategy, CalculoVIPStrategy
from model.decoradores import GPSDecorator, SeguroTerceirosDecorator
from model.ExcecoesPersonalizadas import (
    PlacaInvalidaError,
    DataInvalidaError,
    TipoVeiculoInvalidoError,
)


def separador(titulo):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print('='*50)


# ─── TESTES FACTORY ───────────────────────────────

def teste_criacao_via_factory():
    separador("TESTE 1 – Criação via Factory")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150, categoria=Categoria.ECONOMICO)
    print(f"[OK] Carro criado: placa={carro.placa}, taxa_diaria={carro.taxa_diaria}, seguro={carro.valor_seguro}")
    mh = VeiculoFactory.criar_veiculo("motorhome", "XYZ9999", taxa_diaria=300, categoria=Categoria.EXECUTIVO)
    print(f"[OK] Motorhome criado: placa={mh.placa}, taxa_diaria={mh.taxa_diaria}, seguro={mh.valor_seguro}")
    carro2 = VeiculoFactory.criar_veiculo("Carro", "DEF5678", taxa_diaria=200)
    print(f"[OK] Factory aceita tipo com capitalização diferente: {carro2.placa}")


def teste_tipo_invalido_na_fabrica():
    separador("TESTE 2 – Tipo inválido na Factory")
    try:
        VeiculoFactory.criar_veiculo("bicicleta", "ABC1234", taxa_diaria=50)
        print("[FALHOU] Deveria ter lançado TipoVeiculoInvalidoError")
    except TipoVeiculoInvalidoError as e:
        print(f"[OK] TipoVeiculoInvalidoError capturado: {e}")


# ─── TESTES STRATEGY ──────────────────────────────

def teste_strategy_padrao():
    separador("TESTE 3 – Strategy: Cálculo Padrão")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(
        veiculo=carro,
        data_inicio=date(2026, 3, 10),
        data_fim=date(2026, 3, 15),   # 5 dias
        estrategia=CalculoPadraoStrategy()
    )
    valor = locacao.calcular_valor_locacao()
    esperado = (5 * 150) + 50  # 800
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] Padrão: 5 dias x R$150 + seguro R$50 = R${valor:.2f}")


def teste_strategy_vip():
    separador("TESTE 4 – Strategy: Cálculo VIP (20% desconto nas diárias)")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(
        veiculo=carro,
        data_inicio=date(2026, 3, 10),
        data_fim=date(2026, 3, 15),   # 5 dias
        estrategia=CalculoVIPStrategy()
    )
    valor = locacao.calcular_valor_locacao()
    esperado = (5 * 150 * 0.80) + 50  # 650
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] VIP: 5 dias x R$150 x 80% + seguro R$50 = R${valor:.2f}")


def teste_strategy_troca_dinamica():
    separador("TESTE 5 – Strategy: Troca dinâmica de estratégia")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 4))
    valor_padrao = locacao.calcular_valor_locacao()
    print(f"[OK] Valor padrão: R${valor_padrao:.2f}")

    # Troca a estratégia em tempo de execução
    locacao.estrategia = CalculoVIPStrategy()
    valor_vip = locacao.calcular_valor_locacao()
    print(f"[OK] Após troca para VIP: R${valor_vip:.2f}")
    assert valor_vip < valor_padrao, "VIP deveria ser menor que o padrão"
    print("[OK] Valor VIP é menor que o padrão, como esperado")


def teste_devolucao_mesmo_dia():
    separador("TESTE 6 – Devolução no mesmo dia (mínimo 1 diária)")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 5), data_fim=date(2026, 3, 5))
    valor = locacao.calcular_valor_locacao()
    esperado = (1 * 150) + 50  # 200
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] Devolução no mesmo dia -> 1 diária: R${valor:.2f}")


# ─── TESTES STATE ─────────────────────────────────

def teste_state_fluxo_completo():
    separador("TESTE 7 – State: Fluxo completo de estados")
    carro = VeiculoFactory.criar_veiculo("carro", "HJI3K45", taxa_diaria=100)

    print("\n[1] Alugar carro disponível -> deve funcionar")
    carro.tentar_alugar()

    print("\n[2] Tentar alugar carro já alugado -> deve bloquear")
    carro.tentar_alugar()

    print("\n[3] Tentar mandar pra manutenção com cliente -> deve bloquear")
    carro.reter_na_frota_pra_conserto()

    print("\n[4] Devolver carro -> deve retornar ao pátio")
    carro.tentar_devolver()

    print("\n[5] Mandar para manutenção -> deve funcionar")
    carro.reter_na_frota_pra_conserto()

    print("\n[6] Tentar alugar em manutenção -> deve bloquear")
    carro.tentar_alugar()

    print("\n[7] Liberar da manutenção (devolver) -> disponível novamente")
    carro.tentar_devolver()

    print("\n[8] Alugar após manutenção -> deve funcionar")
    carro.tentar_alugar()
    print("[OK] Fluxo completo de states executado com sucesso!")


def teste_state_devolucao_sem_locacao():
    separador("TESTE 8 – State: Devolver carro que está disponível")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    carro.tentar_devolver()  # deve exibir mensagem de erro
    print("[OK] Mensagem de bloqueio exibida corretamente")


def teste_state_manutencao_dupla():
    separador("TESTE 9 – State: Mandar para manutenção duas vezes")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    carro.reter_na_frota_pra_conserto()
    carro.reter_na_frota_pra_conserto()  # deve exibir mensagem de bloqueio
    print("[OK] Mensagem de bloqueio exibida corretamente")


# ─── TESTES DE VALIDAÇÃO ──────────────────────────

def teste_placa_invalida():
    separador("TESTE 14 – Validações de placa inválida")
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
    separador("TESTE 15 – Data fim anterior à data início")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    try:
        locacao = Locacao(veiculo=carro, data_inicio=date(2026, 3, 10), data_fim=date(2026, 3, 5))
        locacao.calcular_valor_locacao()
        print("[FALHOU] Deveria ter lançado DataInvalidaError")
    except DataInvalidaError as e:
        print(f"[OK] DataInvalidaError capturado: {e}")


def teste_sem_datas():
    separador("TESTE 16 – Calcular locação sem informar datas")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=100)
    locacao = Locacao(veiculo=carro, data_inicio=None, data_fim=None)
    try:
        locacao.calcular_valor_locacao()
        print("[FALHOU] Deveria ter lançado DataInvalidaError")
    except DataInvalidaError as e:
        print(f"[OK] DataInvalidaError capturado: {e}")


# ─── TESTES DECORATOR ────────────────────────────

def teste_decorator_gps():
    separador("TESTE 10 – Decorator: GPS")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao_base = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 5))  # 4 dias

    valor_base = locacao_base.calcular_valor_locacao()
    esperado_base = (4 * 150) + 50  # 650
    assert valor_base == esperado_base, f"Esperado {esperado_base}, obtido {valor_base}"
    print(f"[OK] Valor base: R${valor_base:.2f}")

    locacao_com_gps = GPSDecorator(locacao_base)
    valor_gps = locacao_com_gps.calcular_valor_locacao()
    esperado_gps = esperado_base + 35.0  # 685
    assert valor_gps == esperado_gps, f"Esperado {esperado_gps}, obtido {valor_gps}"
    print(f"[OK] Base + GPS (R$35): R${valor_gps:.2f}")


def teste_decorator_seguro_terceiros():
    separador("TESTE 11 – Decorator: Seguro de Terceiros")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao_base = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 5))  # 4 dias

    locacao_com_seguro = SeguroTerceirosDecorator(locacao_base)
    valor = locacao_com_seguro.calcular_valor_locacao()
    esperado = (4 * 150) + 50 + (4 * 15.0)  # 650 + 60 = 710
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] Base + Seguro Terceiros (R$15/dia x 4): R${valor:.2f}")


def teste_decorator_empilhado():
    separador("TESTE 12 – Decorator: Empilhamento (Base + GPS + Seguro Terceiros)")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao_base = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 5))  # 4 dias

    locacao_com_gps = GPSDecorator(locacao_base)
    locacao_completa = SeguroTerceirosDecorator(locacao_com_gps)

    valor = locacao_completa.calcular_valor_locacao()
    # base=650 + gps=35 + seguro_terceiros=(4*15=60) = 745
    esperado = (4 * 150) + 50 + 35.0 + (4 * 15.0)
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] Base + GPS + Seguro Terceiros = R${valor:.2f}")


def teste_decorator_com_strategy_vip():
    separador("TESTE 13 – Decorator + Strategy VIP empilhados")
    carro = VeiculoFactory.criar_veiculo("carro", "ABC1234", taxa_diaria=150)
    locacao_vip = Locacao(
        veiculo=carro,
        data_inicio=date(2026, 3, 1),
        data_fim=date(2026, 3, 5),
        estrategia=CalculoVIPStrategy()
    )
    locacao_vip_com_gps = GPSDecorator(locacao_vip)
    valor = locacao_vip_com_gps.calcular_valor_locacao()
    # vip = (4*150*0.80)+50 = 530 + gps = 35 → 565
    esperado = (4 * 150 * 0.80) + 50 + 35.0
    assert valor == esperado, f"Esperado {esperado}, obtido {valor}"
    print(f"[OK] VIP + GPS = R${valor:.2f}")


# ─── EXECUÇÃO ─────────────────────────────────────

if __name__ == "__main__":
    teste_criacao_via_factory()
    teste_tipo_invalido_na_fabrica()
    teste_strategy_padrao()
    teste_strategy_vip()
    teste_strategy_troca_dinamica()
    teste_devolucao_mesmo_dia()
    teste_state_fluxo_completo()
    teste_state_devolucao_sem_locacao()
    teste_state_manutencao_dupla()
    teste_placa_invalida()
    teste_data_invalida()
    teste_sem_datas()

    teste_decorator_gps()
    teste_decorator_seguro_terceiros()
    teste_decorator_empilhado()
    teste_decorator_com_strategy_vip()

    print("\n" + "="*50)
    print("  TODOS OS TESTES CONCLUÍDOS")
    print("="*50)
