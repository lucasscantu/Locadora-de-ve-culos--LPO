# Aula 3 - Tutorial - Aplicações de Padrões de Projetos - Projeto Locadora de Veículos

**Curso:** Bacharelado em Ciência da Computação
**Disciplina:** Linguagem de Programação Orientada à Objetos (LPOO)
**Professora:** Vanessa Lago Machado

Neste tutorial, daremos continuidade à refatoração do nosso sistema da Locadora de Veículos, aplicando o Padrão de Projeto Comportamental **Strategy** para resolver a rigidez das lógicas de negócio.

---

## Aplicando Strategy (Padrão Comportamental)

**Elementos do Padrão Strategy:**
* **Propósito:** Definir e encapsular uma família de algoritmos que possam ser intercambiáveis em tempo de execução pelo sistema.
* **Motivação:** A classe `Locacao` necessita lidar com variações e exceções de cálculos tarifários, o que cria acoplamentos e blocos gigantescos de condicionais (`If/Else` aninhados).
* **Estrutura:** A classe de Contexto central (Locação) assina uma interface base (A Estratégia) que funciona como um contrato. Instâncias das estratégias filhas (`CalculoVIPStrategy`) assumem a execução real da ação.
* **Exemplo de Código:** O roteiro de desenvolvimento mostrado neste tutorial passo a passo.

---

### 1. Mostrando o problema em `calcular_valor_locacao`
Como calcular tarifas especiais para finais de semana ou condições VIP sem sujar o nosso método com amontoados de `if` ou `switch`? Vamos aplicar a estratégia.

### 2. Criar classe abstrata `Strategy`
Essa interface ditará a assinatura de toda a matemática aplicável às locações da nossa frota.

```python
from abc import ABC, abstractmethod

class CalculoLocacaoStrategy(ABC):
    @abstractmethod
    def calcular_diarias(self, veiculo: 'Veiculo', dias: int) -> float:
        """Assinatura do contrato de estratégia"""
        pass
```

### 3. Criar Estratégias Concretas
Vamos criar duas classes com táticas distintas, uma aplicando o padrão cobrado e outra aplicando a tarifa de cliente VIP.

```python
class CalculoPadraoStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo: Veiculo, dias: int) -> float:
        # A taxa do seguro é somada ao total cobrado pelas diárias
        return (veiculo.taxa_diaria * dias) + veiculo.valor_seguro

class CalculoVIPStrategy(CalculoLocacaoStrategy):
    def calcular_diarias(self, veiculo: Veiculo, dias: int) -> float:
        # Clientes VIP ganham 20% de desconto no custo das diárias 
        valor_base = veiculo.taxa_diaria * dias
        total_vip = valor_base * 0.80
        return total_vip + veiculo.valor_seguro
```

### 4. Injetar a estratégia na classe `Locacao`
Modifique a classe Locação para que ela receba e seja parametrizada com a Injeção de Dependências de uma "Estratégia de Aluguel". O método delegará a execução para a interface.

```python
class Locacao:
    # Parâmetro opcional de estratégia recebido no construtor
    def __init__(self, data_inicio, data_fim, veiculo, estrategia=CalculoPadraoStrategy()):
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.veiculo = veiculo
        self.estrategia = estrategia
    
    # Podemos mudar a estratégia dinamicamente usando o setter se precisar
    # Exemplo: locacao.estrategia = CalculoVIPStrategy()
    @property
    def estrategia(self):
        return self.__estrategia
    
    @estrategia.setter
    def estrategia(self, estrategia: CalculoLocacaoStrategy):
        self.__estrategia = estrategia
        
    def calcular_valor_locacao(self) -> float:
        dias = (self.data_fim - self.data_inicio).days
        if dias <= 0:
            dias = 1
            
        # O Padrão Strategy atuando aqui!
        return self._estrategia.calcular_diarias(self.veiculo, dias)
```

### 5. Testar comportamento
No `teste.py`, efetue simulações de aluguéis usando suas novas classes parametrizadas em tempo de execução para os comportamentos divergentes.

```python
from datetime import date

# (Assumindo que o veículo foi instanciado previamente via VeiculoFactory)
# carro = VeiculoFactory.criar_veiculo("carro", "AAA1A11", Categoria.EXECUTIVO)

data_in = date(2026, 3, 10)
data_out = date(2026, 3, 15)

# Locação com o Cálculo Padrão
locacao_normal = Locacao(data_in, data_out, carro, CalculoPadraoStrategy())
print(f"Valor Padrão: {locacao_normal.calcular_valor_locacao()}")

# Locação usando a Estratégia de Cálculo VIP
locacao_vip = Locacao(data_in, data_out, carro, CalculoVIPStrategy())
print(f"Valor Cliente VIP: {locacao_vip.calcular_valor_locacao()}")
```
Parabéns! Seu design garante agora grande resiliência de negócios. Em cenários reais, sua classe Locação estaria inviolável e blindada contra complexidade.
