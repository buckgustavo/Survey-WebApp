import pytest

from apps.accounts.infrastructure.models import Usuario
from apps.surveys.application.use_cases import (
    AbrirPesquisa,
    CriarPesquisa,
    CriarPesquisaInput,
    FecharPesquisa,
    QuestaoInput,
    ResponderPesquisa,
    ResponderPesquisaInput,
)
from apps.surveys.domain.entities import StatusPesquisa
from apps.surveys.infrastructure.repositories import PesquisaRepository, RespostaRepository


@pytest.fixture
def coordenador(db):
    return Usuario.objects.create_user(
        email='coord@ex.com', nome='Coord', password='s', eh_coordenador=True
    )


@pytest.fixture
def respondente(db):
    return Usuario.objects.create_user(
        email='resp@ex.com', nome='Resp', password='s'
    )


@pytest.fixture
def pesquisa_rascunho(coordenador):
    repo = PesquisaRepository()
    return repo.criar(
        titulo='Pesquisa Teste',
        coordenador_id=coordenador.pk,
        questoes=[{'texto': 'Q1', 'opcoes': ['A', 'B']}],
    )


@pytest.mark.django_db
class TestCriarPesquisa:
    def test_cria_com_sucesso(self, coordenador):
        caso = CriarPesquisa(PesquisaRepository())
        pesquisa = caso.executar(CriarPesquisaInput(
            titulo='Nova',
            coordenador_id=coordenador.pk,
            questoes=[QuestaoInput(texto='Qual?', opcoes=['Sim', 'Nao'])],
        ))
        assert pesquisa.titulo == 'Nova'
        assert pesquisa.status == StatusPesquisa.RASCUNHO
        assert len(pesquisa.questoes) == 1
        assert len(pesquisa.questoes[0].opcoes) == 2

    def test_falha_sem_titulo(self, coordenador):
        caso = CriarPesquisa(PesquisaRepository())
        with pytest.raises(ValueError, match='Titulo obrigatorio'):
            caso.executar(CriarPesquisaInput(
                titulo='', coordenador_id=coordenador.pk,
                questoes=[QuestaoInput(texto='Q', opcoes=['A'])],
            ))

    def test_falha_mais_de_10_questoes(self, coordenador):
        caso = CriarPesquisa(PesquisaRepository())
        with pytest.raises(ValueError, match='entre 1 e 10'):
            caso.executar(CriarPesquisaInput(
                titulo='T', coordenador_id=coordenador.pk,
                questoes=[QuestaoInput(texto=f'Q{i}', opcoes=['A']) for i in range(11)],
            ))

    def test_falha_mais_de_5_opcoes(self, coordenador):
        caso = CriarPesquisa(PesquisaRepository())
        with pytest.raises(ValueError, match='entre 1 e 5 opcoes'):
            caso.executar(CriarPesquisaInput(
                titulo='T', coordenador_id=coordenador.pk,
                questoes=[QuestaoInput(texto='Q', opcoes=['A', 'B', 'C', 'D', 'E', 'F'])],
            ))


@pytest.mark.django_db
class TestAbrirFecharPesquisa:
    def test_abre_rascunho(self, pesquisa_rascunho, coordenador):
        caso = AbrirPesquisa(PesquisaRepository())
        resultado = caso.executar(pesquisa_rascunho.id, coordenador.pk, eh_coordenador=True)
        assert resultado.status == StatusPesquisa.ABERTA

    def test_fecha_aberta(self, pesquisa_rascunho, coordenador):
        repo = PesquisaRepository()
        repo.atualizar_status(pesquisa_rascunho.id, StatusPesquisa.ABERTA)
        caso = FecharPesquisa(repo)
        resultado = caso.executar(pesquisa_rascunho.id, coordenador.pk, eh_coordenador=True)
        assert resultado.status == StatusPesquisa.FECHADA

    def test_falha_abrir_sem_permissao(self, pesquisa_rascunho, respondente):
        caso = AbrirPesquisa(PesquisaRepository())
        with pytest.raises(PermissionError):
            caso.executar(pesquisa_rascunho.id, respondente.pk, eh_coordenador=False)


@pytest.mark.django_db
class TestResponderPesquisa:
    def test_responde_com_sucesso(self, pesquisa_rascunho, coordenador, respondente):
        repo = PesquisaRepository()
        repo.atualizar_status(pesquisa_rascunho.id, StatusPesquisa.ABERTA)
        pesquisa = repo.buscar_por_id(pesquisa_rascunho.id)
        questao = pesquisa.questoes[0]
        opcao = questao.opcoes[0]
        caso = ResponderPesquisa(repo, RespostaRepository())
        resposta = caso.executar(ResponderPesquisaInput(
            pesquisa_id=pesquisa.id,
            respondente_id=respondente.pk,
            respostas={questao.id: opcao.id},
        ))
        assert resposta.pesquisa_id == pesquisa.id

    def test_impede_dupla_resposta(self, pesquisa_rascunho, coordenador, respondente):
        repo = PesquisaRepository()
        repo.atualizar_status(pesquisa_rascunho.id, StatusPesquisa.ABERTA)
        pesquisa = repo.buscar_por_id(pesquisa_rascunho.id)
        questao = pesquisa.questoes[0]
        opcao = questao.opcoes[0]
        caso = ResponderPesquisa(repo, RespostaRepository())
        dados = ResponderPesquisaInput(
            pesquisa_id=pesquisa.id,
            respondente_id=respondente.pk,
            respostas={questao.id: opcao.id},
        )
        caso.executar(dados)
        with pytest.raises(ValueError, match='ja respondeu'):
            caso.executar(dados)

    def test_falha_questao_sem_resposta(self, pesquisa_rascunho, coordenador, respondente):
        repo = PesquisaRepository()
        repo.atualizar_status(pesquisa_rascunho.id, StatusPesquisa.ABERTA)
        caso = ResponderPesquisa(repo, RespostaRepository())
        with pytest.raises(ValueError, match='Todas as questoes'):
            caso.executar(ResponderPesquisaInput(
                pesquisa_id=pesquisa_rascunho.id,
                respondente_id=respondente.pk,
                respostas={},
            ))
