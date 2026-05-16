from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from apps.surveys.application.use_cases import (
    AbrirPesquisa,
    CriarPesquisa,
    CriarPesquisaInput,
    FecharPesquisa,
    ObterResultados,
    QuestaoInput,
    ResponderPesquisa,
    ResponderPesquisaInput,
)
from apps.surveys.domain.entities import StatusPesquisa
from apps.surveys.infrastructure.repositories import PesquisaRepository, RespostaRepository


def _requer_coordenador(request):
    return request.user.is_authenticated and request.user.eh_coordenador


class HomeView(View):
    def get(self, request):
        repo = PesquisaRepository()
        abertas = repo.listar_por_status(StatusPesquisa.ABERTA)
        fechadas = repo.listar_por_status(StatusPesquisa.FECHADA)
        rascunhos = []
        if _requer_coordenador(request):
            rascunhos = repo.listar_por_status(StatusPesquisa.RASCUNHO)
        return render(request, 'home.html', {
            'abertas': abertas,
            'fechadas': fechadas,
            'rascunhos': rascunhos,
        })


class CriarPesquisaView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not _requer_coordenador(request):
            messages.error(request, 'Acesso restrito a coordenadores')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'surveys/criar.html')

    def post(self, request):
        titulo = request.POST.get('titulo', '').strip()
        questoes = []
        i = 1
        while True:
            texto_q = request.POST.get(f'questao_{i}_texto', '').strip()
            if not texto_q:
                break
            opcoes = []
            j = 1
            while True:
                texto_op = request.POST.get(f'questao_{i}_opcao_{j}', '').strip()
                if not texto_op:
                    break
                opcoes.append(texto_op)
                j += 1
            questoes.append(QuestaoInput(texto=texto_q, opcoes=opcoes))
            i += 1

        caso_de_uso = CriarPesquisa(PesquisaRepository())
        try:
            caso_de_uso.executar(CriarPesquisaInput(
                titulo=titulo,
                coordenador_id=request.user.pk,
                questoes=questoes,
            ))
            messages.success(request, 'Pesquisa criada com sucesso')
            return redirect('home')
        except (ValueError, Exception) as erro:
            return render(request, 'surveys/criar.html', {'erro': str(erro), 'titulo': titulo})


class AbrirPesquisaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        caso_de_uso = AbrirPesquisa(PesquisaRepository())
        try:
            caso_de_uso.executar(pk, request.user.pk, request.user.eh_coordenador)
            messages.success(request, 'Pesquisa aberta para respostas')
        except (ValueError, PermissionError) as erro:
            messages.error(request, str(erro))
        return redirect('home')


class FecharPesquisaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        caso_de_uso = FecharPesquisa(PesquisaRepository())
        try:
            caso_de_uso.executar(pk, request.user.pk, request.user.eh_coordenador)
            messages.success(request, 'Pesquisa encerrada')
        except (ValueError, PermissionError) as erro:
            messages.error(request, str(erro))
        next_url = request.POST.get('next', 'home')
        return redirect(next_url if next_url != 'home' else 'home')


class ResponderPesquisaView(LoginRequiredMixin, View):
    def get(self, request, pk):
        repo = PesquisaRepository()
        pesquisa = repo.buscar_por_id(pk)
        if pesquisa is None or pesquisa.status != StatusPesquisa.ABERTA:
            messages.error(request, 'Pesquisa nao disponivel')
            return redirect('home')
        resposta_repo = RespostaRepository()
        if resposta_repo.ja_respondeu(pk, request.user.pk):
            messages.info(request, 'Voce ja respondeu esta pesquisa')
            return redirect('home')
        return render(request, 'surveys/responder.html', {'pesquisa': pesquisa})

    def post(self, request, pk):
        repo = PesquisaRepository()
        pesquisa = repo.buscar_por_id(pk)
        if pesquisa is None:
            messages.error(request, 'Pesquisa nao encontrada')
            return redirect('home')
        respostas = {}
        for questao in pesquisa.questoes:
            valor = request.POST.get(f'questao_{questao.id}')
            if valor:
                try:
                    respostas[questao.id] = int(valor)
                except (ValueError, TypeError):
                    pass

        caso_de_uso = ResponderPesquisa(repo, RespostaRepository())
        try:
            caso_de_uso.executar(ResponderPesquisaInput(
                pesquisa_id=pk,
                respondente_id=request.user.pk,
                respostas=respostas,
            ))
            messages.success(request, 'Resposta enviada com sucesso')
            return redirect('home')
        except ValueError as erro:
            return render(request, 'surveys/responder.html', {
                'pesquisa': pesquisa,
                'erro': str(erro),
                'respostas_anteriores': {str(k): v for k, v in respostas.items()},
            })


class ResultadosPesquisaView(View):
    def get(self, request, pk):
        repo = PesquisaRepository()
        pesquisa = repo.buscar_por_id(pk)
        if pesquisa is None or pesquisa.status != StatusPesquisa.FECHADA:
            messages.error(request, 'Resultado nao disponivel')
            return redirect('home')
        caso_de_uso = ObterResultados(repo)
        resultado = caso_de_uso.executar(pk)
        return render(request, 'surveys/resultados.html', {'resultado': resultado})


class PesquisaDetalheView(View):
    def get(self, request, pk):
        repo = PesquisaRepository()
        pesquisa = repo.buscar_por_id(pk)
        if pesquisa is None:
            messages.error(request, 'Pesquisa nao encontrada')
            return redirect('home')
        ja_respondeu = False
        if request.user.is_authenticated and not request.user.eh_coordenador:
            ja_respondeu = RespostaRepository().ja_respondeu(pk, request.user.pk)
        return render(request, 'surveys/detalhe.html', {
            'pesquisa': pesquisa,
            'ja_respondeu': ja_respondeu,
        })


class MinhaAreaView(LoginRequiredMixin, View):
    def get(self, request):
        from apps.surveys.infrastructure.models import RespostaRespondente, Pesquisa
        from apps.surveys.domain.entities import StatusPesquisa as SP

        respondidas_ids = set(
            RespostaRespondente.objects
            .filter(respondente=request.user)
            .values_list('pesquisa_id', flat=True)
        )

        abertas = PesquisaRepository().listar_por_status(SP.ABERTA)
        pendentes = [p for p in abertas if p.id not in respondidas_ids]
        concluidas = [p for p in abertas if p.id in respondidas_ids]

        fechadas = PesquisaRepository().listar_por_status(SP.FECHADA)
        concluidas_fechadas = [p for p in fechadas if p.id in respondidas_ids]

        return render(request, 'surveys/minha_area.html', {
            'pendentes': pendentes,
            'concluidas': concluidas,
            'concluidas_fechadas': concluidas_fechadas,
            'total_respondidas': len(respondidas_ids),
        })
