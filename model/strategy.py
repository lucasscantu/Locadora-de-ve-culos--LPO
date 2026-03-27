from abc import ABC, abstractmethod


class CalculoLocacaoStrategy(ABC):
    @abstractmethod
    def calcular_diarias(self, veiculo, dias: int) -> float:
        """Assinatura do contrato de estratégia"""
        pass


class CalculoPadraoStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo, dias: int) -> float:
        # A taxa do seguro é somada ao total cobrado pelas diárias
        return (veiculo.taxa_diaria * dias) + veiculo.valor_seguro


class CalculoVIPStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo, dias: int) -> float:
        # Clientes VIP ganham 20% de desconto no custo das diárias
        valor_base = veiculo.taxa_diaria * dias
        total_vip = valor_base * 0.80
        return total_vip + veiculo.valor_seguro
