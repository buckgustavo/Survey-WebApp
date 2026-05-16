from django.contrib import admin
from django.urls import path, include
from apps.surveys.interface.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('contas/', include('apps.accounts.interface.urls')),
    path('pesquisas/', include('apps.surveys.interface.urls')),
]
