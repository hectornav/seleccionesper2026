from django.contrib import admin
from .models import Partido, Candidato, Propuesta, PreguntaQuiz, OpcionQuiz, Visita


class PropuestaInline(admin.TabularInline):
    model = Propuesta
    extra = 1


class OpcionInline(admin.TabularInline):
    model = OpcionQuiz
    extra = 2


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'siglas', 'ideologia', 'color_primario']
    search_fields = ['nombre', 'siglas']


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'partido', 'posicion_politica', 'region', 'es_destacado']
    list_filter = ['posicion_politica', 'partido', 'es_destacado']
    search_fields = ['nombre', 'partido__nombre']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [PropuestaInline]
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'slug', 'partido', 'foto', 'foto_url', 'edad', 'region', 'profesion', 'lema')
        }),
        ('Posición Política', {
            'fields': ('posicion_politica', 'biografia', 'experiencia', 'es_destacado', 'orden')
        }),
        ('Scores para Quiz', {
            'fields': ('score_economia', 'score_seguridad', 'score_medio_ambiente', 'score_educacion', 'score_salud'),
            'classes': ('collapse',),
        }),
    )


@admin.register(PreguntaQuiz)
class PreguntaQuizAdmin(admin.ModelAdmin):
    list_display = ['texto', 'tema', 'orden']
    list_filter = ['tema']
    inlines = [OpcionInline]


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['ip', 'pais', 'ciudad', 'fecha', 'path']
    list_filter = ['pais', 'ciudad', 'fecha']
    readonly_fields = ['ip', 'pais', 'ciudad', 'region', 'fecha', 'path', 'user_agent']
    search_fields = ['ip', 'pais', 'ciudad']

    def has_add_permission(self, request):
        return False # No queremos añadir visitas manualmente
