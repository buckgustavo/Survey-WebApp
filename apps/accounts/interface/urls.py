from django.urls import path

from apps.accounts.interface.views import LoginView, LogoutView, RegistroView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('entrar/', LoginView.as_view(), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
]
