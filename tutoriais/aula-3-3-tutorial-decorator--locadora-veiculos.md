# Aula 3 - Tutorial - Padrão de Projeto Decorator - Projeto Locadora de Veículos

**Curso:** Bacharelado em Ciência da Computação
**Disciplina:** Linguagem de Programação Orientada à Objetos (LPOO)
**Professora:** Vanessa Lago Machado

Neste tutorial, daremos continuidade à refatoração do nosso sistema da Locadora de Veículos, aplicando o Padrão de Projeto Estrutural **Decorator** para adicionar novas funcionalidades tarifárias dinâmicas aos nossos objetos em tempo de execução.

---

## Aplicando Decorator (Padrão Estrutural)

**Elementos do Padrão Decorator:**
* **Propósito:** Permitir o acoplamento de novos comportamentos ("decorações") a um objeto base, envelopando-o, sem precisar criar uma vasta árvore de heranças (ex: criar classes como `LocacaoComGPS` ou `LocacaoComGPSeSeguroExtra`).
* **Motivação:** A nossa `Locacao` computa o total de um aluguel de veículo, mas com a chegada de adicionais flexíveis oferecidos no balcão (como GPS e Cadeira de Bebê), se formos codificar isso dentro da locação, o Princípio do Acoplamento / OCP (Aberto-Fechado) do SOLID será quebrado.
* **Estrutura:** O decorador implementa a mesma interface (assina o mesmo contrato) que a Locação base a qual ele decora. O Decorador detém a referência à Locação envelopada, e soma seus cálculos adicionais a ela.

---

### Passo 1: O Componente Base
Em Python, podemos contar com o conceito de *Duck Typing*, mas para clareza estrutural em POO, todos os nossos componentes de cobrança devem possuir em comum a assinatura do método `calcular_valor_locacao()`. Nossa classe original `Locacao` (no arquivo `model/locacao.py`) já possui esse método e será nosso componente principal.

### Passo 2: A Classe Base Decorator
Crie um novo arquivo chamado `decoradores.py` dentro do pacote `model` e implemente a base de um decorador de locação:

```python
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

    @abstractmethod
    def calcular_valor_locacao(self) -> float:
        # Repassa o cálculo base provido pela instancia "envelopada" e joga na filha
        pass
```

### Passo 3: Criar Decoradores Concretos (Adicionais da Locadora)
Ainda no arquivo `decoradores.py`, implementaremos as funcionalidades que podem ser "penduradas" numa locação, como um rastreador GPS e uma cobertura abrangente de terceiros:

```python
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
        # Note que se a base for nossa classe Locacao, podemos invocar outras defs do alvo
        # Como o decorator não sabe se a base tem "data_fim", pegamos dias por inferência
        # Ou se valendo da flexibilidade do Duck Typing do Python!
        
        # Em prol de um design enxuto de aula, consideraremos soma simples em diárias:
        dias = (self.locacao_alvo.data_fim - self.locacao_alvo.data_inicio).days
        if dias <= 0: dias = 1
            
        valor_original_envelopado = self.locacao_alvo.calcular_valor_locacao()
        return float(valor_original_envelopado + (dias * self.taxa_diaria_seguro))
```

### Passo 4: Praticando no `teste.py`
Podemos agora montar uma locação como se fosse um hambúrguer em camadas. Modifique seu arquivo `teste.py` (código cliente) para importar os decoradores recém construídos:

```python
from model.decoradores import GPSDecorator, SeguroTerceirosDecorator
# ... restantes das suas importações

print("\n--- TESTANDO O PADRÃO DECORATOR ---")
# 1. Base simples
locacao_base = Locacao(veiculo=carro, data_inicio=date(2026, 3, 1), data_fim=date(2026, 3, 5))
print(f"Valor Base (somente Diária + Seguro Base): R$ {locacao_base.calcular_valor_locacao()}")

# 2. Base + GPS
locacao_com_gps = GPSDecorator(locacao_base)
print(f"Valor somado do pacote + GPS: R$ {locacao_com_gps.calcular_valor_locacao()}")

# 3. Empurrar SeguroTerceiros Por Cima De Tudo (Envelopamento)
locacao_vip_top = SeguroTerceirosDecorator(locacao_com_gps)
print(f"Valor pacote completão (Base + GPS + Seg.Terceiros): R$ {locacao_vip_top.calcular_valor_locacao()}")

```

### Reflexão:
A classe base original `Locacao` continuou limpa e com apenas **UMA** responsabilidade (**S** do SOLID), enquanto todos os recálculos são geridos pelos decoradores externos que se sobrepõem transparentemente (Aberto para Extensão: **O** do SOLID).
