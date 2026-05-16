from dataclasses import dataclass

from apps.accounts.domain.entities import UsuarioEntidade
from apps.accounts.infrastructure.repositories import UsuarioRepository


@dataclass
class RegistrarUsuarioInput:
    email: str
    nome: str
    senha: str


class RegistrarUsuario:
    def __init__(self, repositorio: UsuarioRepository):
        self._repositorio = repositorio

    def executar(self, dados: RegistrarUsuarioInput) -> UsuarioEntidade:
        existente = self._repositorio.buscar_por_email(dados.email)
        if existente:
            raise ValueError('Email ja cadastrado')
        return self._repositorio.criar(dados.email, dados.nome, dados.senha)
