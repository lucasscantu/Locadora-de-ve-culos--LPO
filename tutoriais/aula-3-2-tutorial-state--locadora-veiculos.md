# Aula 3 - Tutorial - Padrão de Projeto State - Projeto Locadora de Veículos

**Curso:** Bacharelado em Ciência da Computação
**Disciplina:** Linguagem de Programação Orientada à Objetos (LPOO)
**Professora:** Vanessa Lago Machado

Neste tutorial, daremos continuidade à refatoração do nosso sistema da Locadora de Veículos, aplicando o Padrão de Projeto Comportamental **State** para transitar entre estados de disponibilidade da frota de forma estruturada e coerente.

---

## Aplicando State (Padrão Comportamental)

**Elementos do Padrão State:**
* **Propósito:** Permitir que um objeto altere suas reações e bloqueios lógico internamente quando a sua representação de Estado se altera significativamente.
* **Motivação:** Como evitar que se alugue um carro já alugado? Usar um método com dezenas de `if self.estado == "ALUGADO"` e `elif self.estado == "MANUTENÇÃO"` gera forte acoplamento (o famoso código *espaguete*).
* **Estrutura:** O Contexto (o nosso Veículo) terá um atributo que guarda não uma *string*, mas uma referência para instâncias de Classes-Estado, que herdarão de uma matriz comum (Interface State) assinando a responsabilidade sobre como reagir às transações.

---

### Passo 1: Definir a base dos Estados (O Contrato)
Crie um novo arquivo chamado `estados_veiculo.py` no diretório `model`. Nele definiremos todas as reações cabíveis ou interações possíveis aplicáveis sobre um Veículo no decorrer do pátio da Locadora.

```python
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
```

### Passo 2: Criar as subclasses de Estado Concreto
Ainda em `estados_veiculo.py`, cada Estado que o veículo pode assumir vira uma classe, que cuida sozinha das regras proibitivas daquele cenário.

```python
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
```

### Passo 3: Injetar e Delegar ações a partir do Contexto (`veiculo.py`)
No arquivo da matriz `Veiculo`, adicionaremos o controle inicial do seu novo Estado, retirando as restrições da responsabilidade de si para entregá-las para os dependentes do padrão *State*. Modifique as importações superiores injetando também uma chamada retroativa inicialização:

```python
# No topo do veiculo.py:
from .estados_veiculo import DisponivelState

# ... Dentro da Classe Veiculo que já criamos ...
class Veiculo(ABC):
    def __init__(self, placa: str, taxa_diaria: float, categoria: Categoria = Categoria.ECONOMICO):
        self.placa = placa
        self.categoria = categoria
        self.taxa_diaria = taxa_diaria
        # Todo veículo "começa a vida" estando recém-comprado e disponível.
        self.estado_atual = DisponivelState(self)
        
    @property
    def estado_atual(self):
        return self._estado_atual

    @estado_atual.setter
    def estado_atual(self, novo_estado):
        # Usado pelas classes de estado para mudar o ponteiro do carro
        self._estado_atual = novo_estado
        
    # DELEGAÇÃO:
    def tentar_alugar(self):
        self.estado_atual.alugar()
        
    def tentar_devolver(self):
        self.estado_atual.devolver()
        
    def reter_na_frota_pra_conserto(self):
        self.estado_atual.enviar_manutencao()
```

### Passo 4: Praticando no `teste.py`
Seu modelo ficou blindado à burla de sistemas baseados num amontoado de `Ifs`. Observe a flexibilidade delegativa a partir do sistema local num script de execução base:

```python
print("\n--- TESTANDO O PADRÃO STATE RESTRITIVO ---")
carro_estado = VeiculoFactory.criar_veiculo("carro", "HJI3K45", Categoria.ECONOMICO, taxa_diaria=100.0)

# 1. Tentar alugar um carro de frota normal
carro_estado.tentar_alugar() # OK - Transitará

# 2. Tentar locar novamente para outro!
carro_estado.tentar_alugar() # Erro Interativo ("Já está alugado!")

# 3. Tentar mandar pra manutenção com cleinte
carro_estado.reter_na_frota_pra_conserto() # Bloqueado

# 4. Devolver 
carro_estado.tentar_devolver() # Ok (Retorna)

# 5. Colocar em checkups da empresa
carro_estado.reter_na_frota_pra_conserto() # Ok 
carro_estado.tentar_alugar() # Falha! Está em Manutenção.
```

