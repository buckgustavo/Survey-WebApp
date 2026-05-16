from django import forms


class FormRegistro(forms.Form):
    nome = forms.CharField(max_length=150, label='Nome completo')
    email = forms.EmailField(label='Email')
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha')
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label='Confirmar senha')

    def clean(self):
        dados = super().clean()
        if dados.get('senha') != dados.get('confirmar_senha'):
            raise forms.ValidationError('As senhas nao conferem')
        return dados
