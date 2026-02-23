from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Partido, Candidato, Propuesta, PreguntaQuiz, OpcionQuiz, Visita, ResultadoQuiz, Encuesta


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

@admin.register(ResultadoQuiz)
class ResultadoQuizAdmin(admin.ModelAdmin):
    list_display = ['ip', 'fecha', 'candidato_top']
    list_filter = ['fecha', 'candidato_top']
    readonly_fields = ['ip', 'fecha', 'candidato_top', 'respuestas_json']

    def has_add_permission(self, request):
        return False


@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ['encuestadora', 'siglas', 'fecha_terreno', 'fecha_publicacion', 'activo', 'link_fuente']
    list_filter = ['activo', 'encuestadora']
    search_fields = ['encuestadora', 'nota']
    date_hierarchy = 'fecha_terreno'
    list_editable = ['activo']
    readonly_fields = ['link_fuente_lectura']

    def link_fuente(self, obj):
        if not obj.fuente_url:
            return '—'
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Ver fuente</a>',
            obj.fuente_url,
        )
    link_fuente.short_description = 'Fuente'

    def link_fuente_lectura(self, obj):
        if not obj or not obj.fuente_url:
            return '—'
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" class="button">Abrir fuente oficial</a>',
            obj.fuente_url,
        )
    link_fuente_lectura.short_description = 'Enlace a la fuente'

    fieldsets = (
        (None, {
            'fields': ('encuestadora', 'siglas', 'fecha_terreno', 'fecha_publicacion', 'activo', 'orden'),
        }),
        ('Fuente (donde obtuviste los datos)', {
            'fields': ('fuente_url', 'link_fuente_lectura'),
        }),
        ('Contenido', {
            'fields': ('resultados', 'nota'),
        }),
    )
