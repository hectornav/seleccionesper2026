from django.contrib import admin
from .models import Voto


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('candidato', 'ip_address', 'session_key', 'fecha_voto')
    list_filter = ('candidato', 'fecha_voto')
    search_fields = ('ip_address', 'session_key', 'candidato__nombre')
    ordering = ('-fecha_voto',)
