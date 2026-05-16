from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatusPesquisa(str, Enum):
    RASCUNHO = 'rascunho'
    ABERTA = 'aberta'
    FECHADA = 'fechada'


@dataclass(frozen=True)
class OpcaoEntidade:
    id: int | None
    texto: str
    ordem: int


@dataclass(frozen=True)
class QuestaoEntidade:
    id: int | None
    texto: str
    ordem: int
    opcoes: tuple[OpcaoEntidade, ...]


@dataclass(frozen=True)
class PesquisaEntidade:
    id: int | None
    titulo: str
    status: StatusPesquisa
    criado_por_id: int
    criado_em: datetime | None
    questoes: tuple[QuestaoEntidade, ...]


@dataclass(frozen=True)
class RespostaItemEntidade:
    questao_id: int
    opcao_id: int


@dataclass(frozen=True)
class RespostaEntidade:
    id: int | None
    pesquisa_id: int
    respondente_id: int
    itens: tuple[RespostaItemEntidade, ...]
    enviado_em: datetime | None


@dataclass(frozen=True)
class ResultadoOpcao:
    opcao_id: int
    texto_opcao: str
    contagem: int


@dataclass(frozen=True)
class ResultadoQuestao:
    questao_id: int
    texto_questao: str
    resultados: tuple[ResultadoOpcao, ...]


@dataclass(frozen=True)
class ResultadoPesquisa:
    pesquisa_id: int
    titulo: str
    total_respondentes: int
    questoes: tuple[ResultadoQuestao, ...]
