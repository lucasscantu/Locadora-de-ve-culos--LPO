from .veiculo import Veiculo, Carro, Motorhome, Categoria
from .ExcecoesPersonalizadas import TipoVeiculoInvalidoError


class VeiculoFactory:
    @staticmethod
    def criar_veiculo(tipo: str, placa: str, taxa_diaria: float, categoria: Categoria = Categoria.ECONOMICO) -> Veiculo:
        tipo_lower = tipo.strip().lower()

        if tipo_lower == "carro":
            return Carro(placa=placa, taxa_diaria=taxa_diaria, categoria=categoria)
        elif tipo_lower == "motorhome":
            return Motorhome(placa=placa, taxa_diaria=taxa_diaria, categoria=categoria)
        else:
            raise TipoVeiculoInvalidoError(
                f"Tipo de veículo inválido: '{tipo}'. Use 'carro' ou 'motorhome'."
            )
