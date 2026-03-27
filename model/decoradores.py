from abc import ABC, abstractmethod


class LocacaoDecorator(ABC):
    def __init__(self, locacao_alvo):
        self.locacao_alvo = locacao_alvo

    @property
    def locacao_alvo(self):
        return self.__locacao_alvo

    @locacao_alvo.setter
    def locacao_alvo(self, valor):
        self.__locacao_alvo = valor

    @abstractmethod
    def calcular_valor_locacao(self) -> float:
        pass

    def _obter_locacao_base(self):
        """Percorre a cadeia de decoradores até encontrar a Locacao base com as datas."""
        alvo = self.locacao_alvo
        while isinstance(alvo, LocacaoDecorator):
            alvo = alvo.locacao_alvo
        return alvo


class GPSDecorator(LocacaoDecorator):
    def __init__(self, locacao_alvo):
        super().__init__(locacao_alvo)
        self.taxa_fixa_gps = 35.0

    @property
    def taxa_fixa_gps(self):
        return self.__taxa_fixa_gps

    @taxa_fixa_gps.setter
    def taxa_fixa_gps(self, valor):
        self.__taxa_fixa_gps = valor

    def calcular_valor_locacao(self) -> float:
        return self.locacao_alvo.calcular_valor_locacao() + self.taxa_fixa_gps


class SeguroTerceirosDecorator(LocacaoDecorator):
    def __init__(self, locacao_alvo):
        super().__init__(locacao_alvo)
        self.taxa_diaria_seguro = 15.0

    @property
    def taxa_diaria_seguro(self):
        return self.__taxa_diaria_seguro

    @taxa_diaria_seguro.setter
    def taxa_diaria_seguro(self, valor):
        self.__taxa_diaria_seguro = valor

    def calcular_valor_locacao(self) -> float:
        # Percorre a cadeia até a Locacao base para obter as datas
        base = self._obter_locacao_base()
        dias = (base.data_fim - base.data_inicio).days
        if dias <= 0:
            dias = 1
        valor_original_envelopado = self.locacao_alvo.calcular_valor_locacao()
        return float(valor_original_envelopado + (dias * self.taxa_diaria_seguro))
