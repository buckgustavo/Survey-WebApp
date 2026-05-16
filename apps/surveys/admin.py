from django.contrib import admin

from apps.surveys.infrastructure.models import Opcao, Pesquisa, Questao, RespostaRespondente


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 2


class QuestaoInline(admin.StackedInline):
    model = Questao
    extra = 1


@admin.register(Pesquisa)
class PesquisaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'criado_por', 'criado_em')
    list_filter = ('status',)
    inlines = [QuestaoInline]


@admin.register(RespostaRespondente)
class RespostaRespondeteAdmin(admin.ModelAdmin):
    list_display = ('pesquisa', 'respondente', 'enviado_em')
