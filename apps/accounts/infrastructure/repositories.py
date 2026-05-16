from apps.accounts.domain.entities import UsuarioEntidade
from apps.accounts.infrastructure.models import Usuario


class UsuarioRepository:
    def buscar_por_email(self, email: str) -> UsuarioEntidade | None:
        try:
            usuario = Usuario.objects.get(email=email)
            return self._para_entidade(usuario)
        except Usuario.DoesNotExist:
            return None

    def criar(self, email: str, nome: str, senha: str) -> UsuarioEntidade:
        usuario = Usuario.objects.create_user(email=email, nome=nome, password=senha)
        return self._para_entidade(usuario)

    def _para_entidade(self, model: Usuario) -> UsuarioEntidade:
        return UsuarioEntidade(
            id=model.pk,
            email=model.email,
            nome=model.nome,
            eh_coordenador=model.eh_coordenador,
        )
