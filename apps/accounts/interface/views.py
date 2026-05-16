from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views import View

from apps.accounts.application.use_cases import RegistrarUsuario, RegistrarUsuarioInput
from apps.accounts.infrastructure.repositories import UsuarioRepository
from apps.accounts.interface.forms import FormRegistro


class RegistroView(View):
    def get(self, request):
        return render(request, 'accounts/registro.html', {'form': FormRegistro()})

    def post(self, request):
        form = FormRegistro(request.POST)
        if not form.is_valid():
            return render(request, 'accounts/registro.html', {'form': form})
        dados = form.cleaned_data
        caso_de_uso = RegistrarUsuario(UsuarioRepository())
        try:
            caso_de_uso.executar(RegistrarUsuarioInput(
                email=dados['email'],
                nome=dados['nome'],
                senha=dados['senha'],
            ))
        except ValueError as erro:
            form.add_error(None, str(erro))
            return render(request, 'accounts/registro.html', {'form': form})
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html', {'proximo': request.GET.get('next', '/')})

    def post(self, request):
        email = request.POST.get('email', '')
        senha = request.POST.get('senha', '')
        usuario = authenticate(request, username=email, password=senha)
        if usuario is None:
            return render(request, 'accounts/login.html', {
                'erro': 'Email ou senha invalidos',
                'proximo': request.POST.get('proximo', '/'),
            })
        login(request, usuario)
        return redirect(request.POST.get('proximo', '/'))


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('home')
