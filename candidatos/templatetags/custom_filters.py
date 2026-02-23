from django import template

register = template.Library()

@register.filter
def format_issue(issue):
    mapping = {
        'asamblea_constituyente': 'Asamblea Constituyente',
        'privatizacion_empresas_estado': 'Privatización de Empresas del Estado',
        'libre_comercio_tlc': 'Libre Comercio / TLC',
        'pena_muerte': 'Pena de Muerte',
        'relaciones_venezuela_cuba': 'Relaciones con Venezuela/Cuba',
        'matrimonio_igualitario': 'Matrimonio Igualitario',
        'medio_ambiente_prioridad_absoluta': 'Medio Ambiente como Prioridad',
        'derechos_animales': 'Derechos de los Animales',
    }
    return mapping.get(issue, issue.replace('_', ' ').title())

@register.filter
def issue_icon(issue):
    mapping = {
        'asamblea_constituyente': 'bi-bank2',
        'privatizacion_empresas_estado': 'bi-building',
        'libre_comercio_tlc': 'bi-globe-americas',
        'pena_muerte': 'bi-exclamation-octagon',
        'relaciones_venezuela_cuba': 'bi-flag',
        'matrimonio_igualitario': 'bi-heart',
        'medio_ambiente_prioridad_absoluta': 'bi-tree',
        'derechos_animales': 'bi-emoji-heart-eyes',
    }
    return mapping.get(issue, 'bi-question-circle')
