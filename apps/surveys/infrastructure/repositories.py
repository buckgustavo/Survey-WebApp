from django.db import transaction
from django.db.models import Count

from apps.surveys.domain.entities import (
    OpcaoEntidade,
    PesquisaEntidade,
    QuestaoEntidade,
    RespostaEntidade,
    RespostaItemEntidade,
    ResultadoOpcao,
    ResultadoPesquisa,
    ResultadoQuestao,
    StatusPesquisa,
)
from apps.surveys.infrastructure.models import (
    Opcao,
    Pesquisa,
    Questao,
    RespostaItem,
    RespostaRespondente,
)


class PesquisaRepository:
    def criar(self, titulo: str, coordenador_id: int, questoes: list[dict]) -> PesquisaEntidade:
        with transaction.atomic():
            pesquisa = Pesquisa.objects.create(titulo=titulo, criado_por_id=coordenador_id)
            for i, q in enumerate(questoes, 1):
                questao = Questao.objects.create(pesquisa=pesquisa, texto=q['texto'], ordem=i)
                for j, op in enumerate(q['opcoes'], 1):
                    Opcao.objects.create(questao=questao, texto=op, ordem=j)
        return self._para_entidade(pesquisa)

    def buscar_por_id(self, pesquisa_id: int) -> PesquisaEntidade | None:
        try:
            pesquisa = Pesquisa.objects.prefetch_related('questoes__opcoes').get(pk=pesquisa_id)
            return self._para_entidade(pesquisa)
        except Pesquisa.DoesNotExist:
            return None

    def listar_por_status(self, status: StatusPesquisa) -> list[PesquisaEntidade]:
        pesquisas = Pesquisa.objects.prefetch_related('questoes__opcoes').filter(status=status)
        return [self._para_entidade(p) for p in pesquisas]

    def atualizar_status(self, pesquisa_id: int, status: StatusPesquisa) -> PesquisaEntidade:
        Pesquisa.objects.filter(pk=pesquisa_id).update(status=status)
        return self.buscar_por_id(pesquisa_id)

    def obter_resultado(self, pesquisa_id: int) -> ResultadoPesquisa:
        pesquisa = Pesquisa.objects.prefetch_related('questoes__opcoes').get(pk=pesquisa_id)
        total = RespostaRespondente.objects.filter(pesquisa_id=pesquisa_id).count()
        questoes_resultado = []
        for questao in pesquisa.questoes.all():
            contagens = (
                RespostaItem.objects
                .filter(questao=questao)
                .values('opcao_id')
                .annotate(total=Count('id'))
            )
            mapa = {c['opcao_id']: c['total'] for c in contagens}
            opcoes_resultado = tuple(
                ResultadoOpcao(opcao_id=op.pk, texto_opcao=op.texto, contagem=mapa.get(op.pk, 0))
                for op in questao.opcoes.all()
            )
            questoes_resultado.append(ResultadoQuestao(
                questao_id=questao.pk,
                texto_questao=questao.texto,
                resultados=opcoes_resultado,
            ))
        return ResultadoPesquisa(
            pesquisa_id=pesquisa_id,
            titulo=pesquisa.titulo,
            total_respondentes=total,
            questoes=tuple(questoes_resultado),
        )

    def _para_entidade(self, model: Pesquisa) -> PesquisaEntidade:
        questoes = tuple(
            QuestaoEntidade(
                id=q.pk,
                texto=q.texto,
                ordem=q.ordem,
                opcoes=tuple(
                    OpcaoEntidade(id=op.pk, texto=op.texto, ordem=op.ordem)
                    for op in q.opcoes.all()
                ),
            )
            for q in model.questoes.all()
        )
        return PesquisaEntidade(
            id=model.pk,
            titulo=model.titulo,
            status=StatusPesquisa(model.status),
            criado_por_id=model.criado_por_id,
            criado_em=model.criado_em,
            questoes=questoes,
        )


class RespostaRepository:
    def ja_respondeu(self, pesquisa_id: int, respondente_id: int) -> bool:
        return RespostaRespondente.objects.filter(
            pesquisa_id=pesquisa_id, respondente_id=respondente_id
        ).exists()

    def salvar(self, pesquisa_id: int, respondente_id: int, itens: list[RespostaItemEntidade]) -> RespostaEntidade:
        with transaction.atomic():
            resposta = RespostaRespondente.objects.create(
                pesquisa_id=pesquisa_id,
                respondente_id=respondente_id,
            )
            RespostaItem.objects.bulk_create([
                RespostaItem(resposta=resposta, questao_id=item.questao_id, opcao_id=item.opcao_id)
                for item in itens
            ])
        return RespostaEntidade(
            id=resposta.pk,
            pesquisa_id=pesquisa_id,
            respondente_id=respondente_id,
            itens=tuple(itens),
            enviado_em=resposta.enviado_em,
        )
