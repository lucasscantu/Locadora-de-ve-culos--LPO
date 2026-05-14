from abc import ABC, abstractmethod
from .veiculo import Veiculo

class CalculoLocacaoStrategy(ABC):
    @abstractmethod
    def calcular_diarias(self, veiculo: Veiculo, dias: int) -> float:
        pass

class CalculoPadraoStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo, dias):
        valor_diarias = veiculo.taxa_diaria * dias
        
        return (valor_diarias + veiculo.valor_seguro)
    
class CalculoVIPStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo, dias):
        # Clientes VIP ganham 20% de desconto no custo das diárias 
        valor_diarias = (veiculo.taxa_diaria * dias) * 0.8
        
        return (valor_diarias + veiculo.valor_seguro)