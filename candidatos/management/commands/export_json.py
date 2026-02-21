import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from candidatos.models import Candidato, Partido

class Command(BaseCommand):
    help = 'Exporta la BD a la nueva estructura organizada (partidos.json y una carpeta con jsons individuales)'

    def handle(self, *args, **options):
        base_dir = os.path.join(os.getcwd(), 'datoscandidatos')
        candidatos_dir = os.path.join(base_dir, 'candidatos')
        os.makedirs(candidatos_dir, exist_ok=True)

        # 1. Exportar Partidos
        self.stdout.write('Exportando partidos...')
        partidos_list = []
        for p in Partido.objects.all():
            partidos_list.append({
                'nombre': p.nombre,
                'siglas': p.siglas,
                'ideologia': p.ideologia,
                'color_primario': p.color_primario,
                'color_secundario': p.color_secundario,
            })
        
        with open(os.path.join(base_dir, 'partidos.json'), 'w', encoding='utf-8') as f:
            json.dump(partidos_list, f, ensure_ascii=False, indent=2)

        # 2. Exportar Candidatos Individuales
        self.stdout.write('Exportando candidatos...')
        for c in Candidato.objects.select_related('partido').prefetch_related('propuestas'):
            propuestas_data = []
            for prop in c.propuestas.all():
                propuestas_data.append({
                    'tema': prop.tema,
                    'titulo': prop.titulo,
                    'descripcion': prop.descripcion,
                    'icono': prop.icono
                })

            candidato_data = {
                'nombre': c.nombre,
                'slug': c.slug,
                'partido_nombre': c.partido.nombre,
                'foto_url': c.foto_url,
                'edad': c.edad,
                'region': c.region,
                'profesion': c.profesion,
                'posicion_politica': c.posicion_politica,
                'lema': c.lema,
                'biografia': c.biografia,
                'experiencia': c.experiencia,
                'antecedentes': c.antecedentes,
                'es_destacado': c.es_destacado,
                'verificado': c.verificado,
                'orden': c.orden,
                'link_plan_gobierno': c.link_plan_gobierno,
                'resumen_propuestas': c.resumen_propuestas,
                'propuestas_destacadas': c.propuestas_destacadas,
                'posicionamiento_issues': c.posicionamiento_issues,
                'fuente_datos': c.fuente_datos,
                'scores': {
                    'score_economia': c.score_economia,
                    'score_seguridad': c.score_seguridad,
                    'score_medio_ambiente': c.score_medio_ambiente,
                    'score_educacion': c.score_educacion,
                    'score_salud': c.score_salud,
                },
                'propuestas': propuestas_data
            }

            filename = f"{slugify(c.nombre)}.json"
            with open(os.path.join(candidatos_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(candidato_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'✅ Exportación exitosa a {base_dir}'))
