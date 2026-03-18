from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Partido, Candidato, CandidatoCongresal, Propuesta, PreguntaQuiz, OpcionQuiz, Visita, ResultadoQuiz, Encuesta, Sugerencia


class PropuestaInline(admin.TabularInline):
    model = Propuesta
    extra = 1


class OpcionInline(admin.TabularInline):
    model = OpcionQuiz
    extra = 2


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ['siglas', 'nombre', 'transparencia_porcentaje', 'transparencia_onpe_total_candidatos']
    search_fields = ['nombre', 'siglas']

    fieldsets = (
        (None, {
            'fields': ('nombre', 'siglas', 'color_primario', 'color_secundario', 'logo', 'ideologia')
        }),
        ('Estadísticas Transparencia Financiera (ONPE)', {
            'fields': ('transparencia_onpe_total_candidatos', 'transparencia_onpe_presentaron', 'transparencia_porcentaje', 'transparencia_ultima_actualizacion'),
            'classes': ('collapse',),
            'description': 'Datos agregados a partir del cruce con los reportes financieros de la ONPE.'
        })
    )
    readonly_fields = ('transparencia_porcentaje',)


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'partido', 'rol_plancha', 'posicion_politica', 'region', 'es_destacado', 'fallecido', 'info_financiera_estado']
    list_filter = ['rol_plancha', 'posicion_politica', 'partido', 'es_destacado', 'fallecido', 'info_financiera_estado']
    search_fields = ['nombre', 'partido__nombre']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [PropuestaInline]
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'slug', 'partido', 'rol_plancha', 'foto', 'foto_url', 'edad', 'region', 'profesion', 'lema', 'fallecido', 'fecha_fallecimiento')
        }),
        ('Posición Política', {
            'fields': ('posicion_politica', 'biografia', 'experiencia', 'es_destacado', 'orden')
        }),
        ('Transparencia Financiera (ONPE)', {
            'fields': ('info_financiera_estado', 'info_financiera_ingresos', 'info_financiera_gastos', 'info_financiera_fecha'),
            'classes': ('collapse',),
            'description': 'Información extraída del reporte de ingresos y gastos de campaña del Portal Claridad.'
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


@admin.register(CandidatoCongresal)
class CandidatoCongressalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cargo', 'organizacion_politica', 'departamento', 'estado', 'ingresos', 'gastos']
    list_filter = ['cargo', 'estado', 'departamento', 'organizacion_politica']
    search_fields = ['nombre', 'dni', 'organizacion_politica']
    list_per_page = 50
    readonly_fields = ['dni', 'nombre', 'genero', 'edad', 'cargo', 'organizacion_politica', 'departamento', 'provincia', 'distrito', 'estado', 'fecha_presentacion', 'ingresos', 'gastos', 'entrega']

    def has_add_permission(self, request):
        return False


@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'mensaje_corto', 'fecha']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['tipo', 'mensaje', 'fecha']
    date_hierarchy = 'fecha'

    def mensaje_corto(self, obj):
        return obj.mensaje[:100] + ('...' if len(obj.mensaje) > 100 else '')
    mensaje_corto.short_description = 'Mensaje'

    def has_add_permission(self, request):
        return False
