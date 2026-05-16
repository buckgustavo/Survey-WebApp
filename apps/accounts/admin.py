from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.infrastructure.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'nome', 'eh_coordenador', 'is_active')
    list_filter = ('eh_coordenador', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('nome',)}),
        ('Permissoes', {'fields': ('eh_coordenador', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'eh_coordenador'),
        }),
    )
    search_fields = ('email', 'nome')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
