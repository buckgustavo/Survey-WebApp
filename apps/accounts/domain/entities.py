from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioEntidade:
    id: int | None
    email: str
    nome: str
    eh_coordenador: bool
