from datetime import date
from .veiculo import Veiculo
from .strategy import CalculoLocacaoStrategy, CalculoPadraoStrategy
from .ExcecoesPersonalizadas import DataInvalidaError


class Locacao:
    def __init__(self, veiculo: Veiculo, data_inicio: date, data_fim: date,
                 estrategia: CalculoLocacaoStrategy = None):
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        # Se não informar estratégia, usa o cálculo padrão
        self.estrategia = estrategia if estrategia is not None else CalculoPadraoStrategy()

    @property
    def veiculo(self):
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, obj):
        if obj is not None:
            self.__veiculo = obj
        else:
            raise Exception("Objeto Veículo obrigatório!!!")

    @property
    def data_inicio(self):
        return self.__data_inicio

    @data_inicio.setter
    def data_inicio(self, valor):
        if valor is not None and not isinstance(valor, date):
            raise DataInvalidaError("data_inicio deve ser um objeto do tipo date.")
        self.__data_inicio = valor

    @property
    def data_fim(self):
        return self.__data_fim

    @data_fim.setter
    def data_fim(self, valor):
        if valor is not None and not isinstance(valor, date):
            raise DataInvalidaError("data_fim deve ser um objeto do tipo date.")
        self.__data_fim = valor

    @property
    def estrategia(self):
        return self.__estrategia

    @estrategia.setter
    def estrategia(self, estrategia: CalculoLocacaoStrategy):
        self.__estrategia = estrategia

    def calcular_valor_locacao(self) -> float:
        if self.__data_inicio is None or self.__data_fim is None:
            raise DataInvalidaError("data_inicio e data_fim são obrigatórios para calcular o valor da locação.")

        if self.__data_fim < self.__data_inicio:
            raise DataInvalidaError("data_fim não pode ser anterior à data_inicio.")

        dias = (self.__data_fim - self.__data_inicio).days

        # Devolução no mesmo dia = 1 diária
        if dias <= 0:
            dias = 1

        # O Padrão Strategy atuando aqui!
        return self.__estrategia.calcular_diarias(self.__veiculo, dias)
