import pytest

from apps.accounts.application.use_cases import RegistrarUsuario, RegistrarUsuarioInput
from apps.accounts.infrastructure.repositories import UsuarioRepository


@pytest.mark.django_db
class TestRegistrarUsuario:
    def test_registra_usuario_com_sucesso(self):
        caso = RegistrarUsuario(UsuarioRepository())
        usuario = caso.executar(RegistrarUsuarioInput(
            email='teste@exemplo.com', nome='Teste', senha='senha123'
        ))
        assert usuario.email == 'teste@exemplo.com'
        assert usuario.nome == 'Teste'
        assert not usuario.eh_coordenador

    def test_falha_email_duplicado(self):
        caso = RegistrarUsuario(UsuarioRepository())
        dados = RegistrarUsuarioInput(email='dup@exemplo.com', nome='Dup', senha='senha123')
        caso.executar(dados)
        with pytest.raises(ValueError, match='Email ja cadastrado'):
            caso.executar(dados)
