from abc import ABC, abstractmethod

class VeiculoState(ABC):
    
    # Referência para manipular facilmente as transições
    def __init__(self, veiculo):
        self.veiculo = veiculo

    @property
    def veiculo(self):
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, valor):
        self.__veiculo = valor

    @abstractmethod
    def alugar(self): pass

    @abstractmethod
    def devolver(self): pass
    
    @abstractmethod
    def enviar_manutencao(self): pass


class DisponivelState(VeiculoState):
    def alugar(self):
        print(f"Sucesso! O veículo {self.veiculo.placa} agora está alugado para um cliente.")
        # Transição: O próprio estado invoca a migração do ponteiro na base:
        self.veiculo.estado_atual = AlugadoState(self.veiculo)
        
    def devolver(self):
        print("Erro: O veículo já consta no pátio e está aguardando clientes, não cabe devolução.")

    def enviar_manutencao(self):
        print(f"O veículo {self.veiculo.placa} foi retido no pátio da frota para reparos técnicos.")
        self.veiculo.estado_atual = ManutencaoState(self.veiculo)


class AlugadoState(VeiculoState):
    def alugar(self):
        # Bloqueio imediato para dupla locação:
        print(f"Reserva Negada. O veículo {self.veiculo.placa} já está sob locação ativa de outro cliente.")
        
    def devolver(self):
        print(f"Devolução registrada. O veículo {self.veiculo.placa} retorna ao pátio.")
        self.veiculo.estado_atual = DisponivelState(self.veiculo)

    def enviar_manutencao(self):
        print("Erro operacional: O carro está na rua com um cliente, impossível fazer manutenção agora.")


class ManutencaoState(VeiculoState):
    def alugar(self):
        print(f"Restrição Ativa: O veículo {self.veiculo.placa} não está apto à rodagem.")
        
    def devolver(self):
        # Em manutenção, após o conserto ou liberação técnica, ele retorna para os boxes:
        print("Fim do período de reparos. Lavagem concluída. O carro agora está disponibilizado.")
        self.veiculo.estado_atual = DisponivelState(self.veiculo)
        
    def enviar_manutencao(self):
        print("O veículo já se encontra nos estaleiros da oficina no momento.")
