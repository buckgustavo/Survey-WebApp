from django.conf import settings
from django.db import models

from apps.surveys.domain.entities import StatusPesquisa


class Pesquisa(models.Model):
    STATUS_CHOICES = [
        (StatusPesquisa.RASCUNHO, 'Rascunho'),
        (StatusPesquisa.ABERTA, 'Aberta'),
        (StatusPesquisa.FECHADA, 'Fechada'),
    ]

    titulo = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=StatusPesquisa.RASCUNHO)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pesquisas')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'pesquisa'
        verbose_name_plural = 'pesquisas'
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo


class Questao(models.Model):
    pesquisa = models.ForeignKey(Pesquisa, on_delete=models.CASCADE, related_name='questoes')
    texto = models.CharField(max_length=500)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.texto


class Opcao(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='opcoes')
    texto = models.CharField(max_length=300)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.texto


class RespostaRespondente(models.Model):
    pesquisa = models.ForeignKey(Pesquisa, on_delete=models.CASCADE, related_name='respostas')
    respondente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='respostas')
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('pesquisa', 'respondente')]

    def __str__(self):
        return f"{self.respondente} -> {self.pesquisa}"


class RespostaItem(models.Model):
    resposta = models.ForeignKey(RespostaRespondente, on_delete=models.CASCADE, related_name='itens')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE)

    class Meta:
        unique_together = [('resposta', 'questao')]
