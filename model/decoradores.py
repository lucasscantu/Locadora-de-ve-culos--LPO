from abc import ABC, abstractmethod

# Criamos uma base abstrata focada em receber qualquer coisa que represente uma locação
class LocacaoDecorator(ABC):
    def __init__(self, locacao_alvo):
        self.locacao_alvo = locacao_alvo

    @property
    def locacao_alvo(self):
        return self.__locacao_alvo

    @locacao_alvo.setter
    def locacao_alvo(self, valor):
        self.__locacao_alvo = valor

    @property
    def data_inicio(self):
        return self.locacao_alvo.data_inicio
        
    @property
    def data_fim(self):
        return self.locacao_alvo.data_fim

    @abstractmethod
    def calcular_valor_locacao(self) -> float:
        # Repassa o cálculo base provido pela instancia "envelopada" e joga na filha
        pass

class GPSDecorator(LocacaoDecorator):
    def __init__(self, locacao_alvo):
        super().__init__(locacao_alvo)
        self.taxa_fixa_gps = 35.0  # O GPS custa uma taxa plana única ao aluguel
        
    @property
    def taxa_fixa_gps(self):
        return self.__taxa_fixa_gps
        
    @taxa_fixa_gps.setter
    def taxa_fixa_gps(self, valor):
        self.__taxa_fixa_gps = valor

    def calcular_valor_locacao(self) -> float:
        # Retorna o cálculo do alvo original "somado" com a taxa do nosso cenário atual
        return self.locacao_alvo.calcular_valor_locacao() + self.taxa_fixa_gps


class SeguroTerceirosDecorator(LocacaoDecorator):
    def __init__(self, locacao_alvo):
        super().__init__(locacao_alvo)
        self.taxa_diaria_seguro = 15.0  # Este seguro varia conforme a duração também!
        
    @property
    def taxa_diaria_seguro(self):
        return self.__taxa_diaria_seguro
        
    @taxa_diaria_seguro.setter
    def taxa_diaria_seguro(self, valor):
        self.__taxa_diaria_seguro = valor

    def calcular_valor_locacao(self) -> float:
        dias = (self.locacao_alvo.data_fim - self.locacao_alvo.data_inicio).days
        if dias <= 0: dias = 1
            
        valor_original_envelopado = self.locacao_alvo.calcular_valor_locacao()
        return float(valor_original_envelopado + (dias * self.taxa_diaria_seguro))
