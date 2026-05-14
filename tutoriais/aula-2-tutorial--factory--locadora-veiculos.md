# Aula 2 - Tutorial Padrão de Projeto Factory - Locadora de Veículos

**Curso:** Bacharelado em Ciência da Computação
**Disciplina:** Linguagem de Programação Orientada à Objetos (LPOO)
**Professora:** Vanessa Lago Machado

Neste tutorial, vamos refatorar o nosso sistema básico da Locadora de Veículos, resolvendo problemas de instanciação através do Padrão de Projeto Criacional **Factory Method**.

## Requisitos Iniciais
* O modelo inicial de `Veiculo`, `Carro` e `Motorhome`.
* A classe de registro central `Locacao`.

---

## Aplicando Factory Method (Padrão Criacional)

**Elementos do Padrão Factory Method:**
* **Propósito:** Oferecer uma interface genérica para criar objetos em uma superdefinição, mas permitir que as subclasses alterem o tipo exato de objetos que serão criados.
* **Motivação:** No código atual (`main.py`), a instanciação exige que o cliente conheça subclasses específicas como `Carro` e `Motorhome`. Isso acopla o cliente final à hierarquia inteira do domínio automotivo.
* **Estrutura:** Uma Classe Fábrica (Factory) que dita as opções de criação através de métodos (ex: `criar_veiculo()`), centralizando e abstraindo a chamada do construtor direto da memória.
* **Exemplo de Código:** A classe `VeiculoFactory` demonstrada logo abaixo.

---

### 1. Mostrando o Problema Atual
No código atual (`teste.py`), a instanciação de veículos exige que o cliente conheça explicitamente as subclasses `Carro` e `Motorhome`. Isso acopla o cliente final à hierarquia inteira do domínio. 

### 2. Criar a classe `VeiculoFactory`
A fábrica assumirá a decisão estrutural de qual objeto deve "nascer", de acordo com parâmetros ou strings enviadas a ela.

```python
class VeiculoFactory:
    @staticmethod
    def criar_veiculo(tipo: str, placa: str, categoria: Categoria, taxa_diaria: float = 0.0):
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado == "carro":
            return Carro(placa, taxa_diaria, categoria)
        elif tipo_normalizado == "motorhome":
            return Motorhome(placa, taxa_diaria, categoria)
        else:
            raise ValueError(f"Tipo de veículo inválido: {tipo}. Use 'carro' ou 'motorhome'.")
```

### 3. Refatorar o `teste.py`
Seu cliente fica totalmente isolado dos construtores pesados e classes concretas da filial "veículos".

```python
# ANTES:
# carro = Carro(placa="ABC1234", categoria=Categoria.ECONOMICO)
# motorhome = Motorhome(placa="XYZ9876", categoria=Categoria.EXECUTIVO)

# DEPOIS (usando Factory Method):
motorhome = VeiculoFactory.criar_veiculo("motorhome", "XYZ9A99", Categoria.EXECUTIVO, taxa_diaria=200.0)
carro = VeiculoFactory.criar_veiculo("carro", "ABC1D34", Categoria.ECONOMICO, taxa_diaria=150.0)

```

### 4. Testar funcionamento
Rode o seu script. O funcionamento e validações (como de Placa) comportam-se da exata mesma maneira.
