from django import forms


class FormCriarPesquisa(forms.Form):
    titulo = forms.CharField(max_length=200, label='Titulo da Pesquisa')
    num_questoes = forms.IntegerField(min_value=1, max_value=10, initial=1, label='Numero de questoes')
