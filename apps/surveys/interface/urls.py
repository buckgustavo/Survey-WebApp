from django.urls import path

from apps.surveys.interface.views import (
    AbrirPesquisaView,
    CriarPesquisaView,
    FecharPesquisaView,
    MinhaAreaView,
    PesquisaDetalheView,
    ResponderPesquisaView,
    ResultadosPesquisaView,
)

urlpatterns = [
    path('criar/', CriarPesquisaView.as_view(), name='pesquisa-criar'),
    path('minha-area/', MinhaAreaView.as_view(), name='minha-area'),
    path('<int:pk>/', PesquisaDetalheView.as_view(), name='pesquisa-detalhe'),
    path('<int:pk>/abrir/', AbrirPesquisaView.as_view(), name='pesquisa-abrir'),
    path('<int:pk>/fechar/', FecharPesquisaView.as_view(), name='pesquisa-fechar'),
    path('<int:pk>/responder/', ResponderPesquisaView.as_view(), name='pesquisa-responder'),
    path('<int:pk>/resultados/', ResultadosPesquisaView.as_view(), name='pesquisa-resultados'),
]
