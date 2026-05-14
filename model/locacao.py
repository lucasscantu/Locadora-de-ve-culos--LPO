from datetime import date, datetime
from enum import Enum
from .veiculo import Veiculo
from .ExcecoesPersonalizadas import DataInvalidaError
from .LocacaoStrategy import *


class StatusLocacao(Enum):
    """
    Enumeração que controla o ciclo de vida de uma locação.

    - RESERVADO: estado inicial, toda locação é criada com este status.
    - LOCADO:    o veículo foi efetivamente retirado pelo cliente.
    - DEVOLVIDO: o veículo foi devolvido (locação encerrada).
    - CANCELADO: a reserva foi cancelada antes da retirada.
    """
    RESERVADO = "reservado"
    LOCADO = "locado"
    DEVOLVIDO = "devolvido"
    CANCELADO = "cancelado"


class Locacao:

    def __init__(self,
                 veiculo: Veiculo,
                 data_inicio: date = None,
                 data_fim: date = None,
                 estrategia: CalculoLocacaoStrategy = None,
                 status: StatusLocacao = StatusLocacao.RESERVADO,
                 id_locacao: int = None,
                 valor_total: float = None):
        # Inicializa atributos privados antes dos setters para evitar AttributeError
        self.__data_inicio = None
        self.__data_fim = None

        # Permite valor padrão da data de início como hoje
        if data_inicio is None:
            data_inicio = datetime.now().date()

        # Estratégia padrão é a CalculoPadraoStrategy
        if estrategia is None:
            estrategia = CalculoPadraoStrategy()

        self.id = id_locacao
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estrategia = estrategia
        self.status = status
        self.valor_total = valor_total
        # Mantido por compatibilidade com código já existente
        self.devolvido = (status == StatusLocacao.DEVOLVIDO)

    @property
    def veiculo(self):
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, obj: Veiculo):
        if obj is not None:
            self.__veiculo = obj
        else:
            raise Exception("Objeto Veículo obrigatório!!!")

    @property
    def data_inicio(self):
        return self.__data_inicio

    @data_inicio.setter
    def data_inicio(self, data_inicio: date):
        if data_inicio is None:
            raise DataInvalidaError("Data de início é obrigatória!")
        if self.__data_fim is not None and data_inicio > self.__data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        self.__data_inicio = data_inicio

    @property
    def data_fim(self):
        return self.__data_fim

    @data_fim.setter
    def data_fim(self, data_fim: date):
        if data_fim is not None and self.__data_inicio is not None and self.__data_inicio > data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        self.__data_fim = data_fim

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, novo_status):
        # Aceita tanto a Enum quanto a string correspondente
        if isinstance(novo_status, StatusLocacao):
            self.__status = novo_status
        elif isinstance(novo_status, str):
            try:
                self.__status = StatusLocacao(novo_status.lower())
            except ValueError:
                raise ValueError(f"Status inválido: {novo_status}")
        else:
            raise ValueError("Status deve ser uma instância de StatusLocacao ou string.")
        # Sincroniza a flag legada
        self.devolvido = (self.__status == StatusLocacao.DEVOLVIDO)

    def calcular_valor_locacao(self) -> float:
        """
        Calcula o valor da locação utilizando a estratégia configurada.
        Se data_fim não estiver definida, utiliza a data atual.
        """
        data_referencia = self.data_fim if self.data_fim is not None else date.today()

        dias = (data_referencia - self.data_inicio).days
        if dias <= 0:
            dias = 1

        valor_total = self.estrategia.calcular_diarias(self.veiculo, dias)
        return float(valor_total)

    def numero_diarias(self) -> int:
        """Retorna o número de diárias (mínimo 1) usando data_fim ou hoje."""
        data_referencia = self.data_fim if self.data_fim is not None else date.today()
        dias = (data_referencia - self.data_inicio).days
        return dias if dias > 0 else 1
