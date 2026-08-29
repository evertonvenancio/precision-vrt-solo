class ErroAgronomia(Exception):
    """Erro base do módulo de agronomia."""
    pass


class TeorInvalido(ErroAgronomia):
    """Teor de nutriente fora do intervalo esperado."""
    pass


class CulturaNaoEncontrada(ErroAgronomia):
    """Cultura não encontrada nos dados de configuração."""
    pass


class MetodoNaoEncontrado(ErroAgronomia):
    """Metodologia não encontrada nos dados de configuração."""
    pass


class ParametrosInvalidos(ErroAgronomia):
    """Parâmetros inválidos para a análise."""
    pass


class BalancoInsuficiente(ErroAgronomia):
    """Balanço nutricional insuficiente para as necessidades da cultura."""
    pass