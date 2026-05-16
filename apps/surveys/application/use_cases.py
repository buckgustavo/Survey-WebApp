from dataclasses import dataclass

from apps.surveys.domain.entities import (
    PesquisaEntidade,
    RespostaEntidade,
    RespostaItemEntidade,
    ResultadoPesquisa,
    StatusPesquisa,
)
from apps.surveys.infrastructure.repositories import PesquisaRepository, RespostaRepository


@dataclass
class QuestaoInput:
    texto: str
    opcoes: list[str]


@dataclass
class CriarPesquisaInput:
    titulo: str
    coordenador_id: int
    questoes: list[QuestaoInput]


class CriarPesquisa:
    def __init__(self, repositorio: PesquisaRepository):
        self._repositorio = repositorio

    def executar(self, dados: CriarPesquisaInput) -> PesquisaEntidade:
        if not dados.titulo.strip():
            raise ValueError('Titulo obrigatorio')
        if not (1 <= len(dados.questoes) <= 10):
            raise ValueError('A pesquisa deve ter entre 1 e 10 questoes')
        for q in dados.questoes:
            if not q.texto.strip():
                raise ValueError('Texto da questao obrigatorio')
            if not (1 <= len(q.opcoes) <= 5):
                raise ValueError('Cada questao deve ter entre 1 e 5 opcoes')
        questoes_dict = [{'texto': q.texto, 'opcoes': q.opcoes} for q in dados.questoes]
        return self._repositorio.criar(dados.titulo, dados.coordenador_id, questoes_dict)


class AbrirPesquisa:
    def __init__(self, repositorio: PesquisaRepository):
        self._repositorio = repositorio

    def executar(self, pesquisa_id: int, user_id: int, eh_coordenador: bool) -> PesquisaEntidade:
        pesquisa = self._repositorio.buscar_por_id(pesquisa_id)
        if pesquisa is None:
            raise ValueError('Pesquisa nao encontrada')
        if not eh_coordenador:
            raise PermissionError('Acesso negado')
        if pesquisa.status != StatusPesquisa.RASCUNHO:
            raise ValueError('Somente pesquisas em rascunho podem ser abertas')
        return self._repositorio.atualizar_status(pesquisa_id, StatusPesquisa.ABERTA)


class FecharPesquisa:
    def __init__(self, repositorio: PesquisaRepository):
        self._repositorio = repositorio

    def executar(self, pesquisa_id: int, user_id: int, eh_coordenador: bool) -> PesquisaEntidade:
        pesquisa = self._repositorio.buscar_por_id(pesquisa_id)
        if pesquisa is None:
            raise ValueError('Pesquisa nao encontrada')
        if not eh_coordenador and pesquisa.criado_por_id != user_id:
            raise PermissionError('Acesso negado')
        if pesquisa.status != StatusPesquisa.ABERTA:
            raise ValueError('Somente pesquisas abertas podem ser fechadas')
        return self._repositorio.atualizar_status(pesquisa_id, StatusPesquisa.FECHADA)


@dataclass
class ResponderPesquisaInput:
    pesquisa_id: int
    respondente_id: int
    respostas: dict[int, int]


class ResponderPesquisa:
    def __init__(self, pesquisa_repo: PesquisaRepository, resposta_repo: RespostaRepository):
        self._pesquisa_repo = pesquisa_repo
        self._resposta_repo = resposta_repo

    def executar(self, dados: ResponderPesquisaInput) -> RespostaEntidade:
        pesquisa = self._pesquisa_repo.buscar_por_id(dados.pesquisa_id)
        if pesquisa is None:
            raise ValueError('Pesquisa nao encontrada')
        if pesquisa.status != StatusPesquisa.ABERTA:
            raise ValueError('Esta pesquisa nao esta aberta para respostas')
        if self._resposta_repo.ja_respondeu(dados.pesquisa_id, dados.respondente_id):
            raise ValueError('Voce ja respondeu esta pesquisa')
        ids_questoes = {q.id for q in pesquisa.questoes}
        if set(dados.respostas.keys()) != ids_questoes:
            raise ValueError('Todas as questoes devem ser respondidas')
        ids_opcoes_validas = {
            op.id
            for q in pesquisa.questoes
            for op in q.opcoes
        }
        for opcao_id in dados.respostas.values():
            if opcao_id not in ids_opcoes_validas:
                raise ValueError('Opcao invalida selecionada')
        itens = [
            RespostaItemEntidade(questao_id=q_id, opcao_id=op_id)
            for q_id, op_id in dados.respostas.items()
        ]
        return self._resposta_repo.salvar(dados.pesquisa_id, dados.respondente_id, itens)


class ObterResultados:
    def __init__(self, repositorio: PesquisaRepository):
        self._repositorio = repositorio

    def executar(self, pesquisa_id: int) -> ResultadoPesquisa:
        return self._repositorio.obter_resultado(pesquisa_id)
