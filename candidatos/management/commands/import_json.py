import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from candidatos.models import Candidato, Partido, Propuesta

class Command(BaseCommand):
    help = 'Importa y sincroniza la BD desde la nueva estructura (partidos.json y carpeta candidatos/).'

    def handle(self, *args, **kwargs):
        base_dir = os.path.join(os.getcwd(), 'datoscandidatos')
        partidos_path = os.path.join(base_dir, 'partidos.json')
        candidatos_dir = os.path.join(base_dir, 'candidatos')
        
        if not os.path.exists(partidos_path):
            self.stdout.write(self.style.ERROR(f'❌ No se encontró: {partidos_path}'))
            return

        # 1. Importar Partidos
        with open(partidos_path, 'r', encoding='utf-8') as f:
            partidos_data = json.load(f)
        
        for p_data in partidos_data:
            Partido.objects.update_or_create(
                nombre=p_data.get('nombre'),
                defaults={
                    'siglas': p_data.get('siglas', ''),
                    'ideologia': p_data.get('ideologia', ''),
                    'color_primario': p_data.get('color_primario', '#cccccc'),
                    'color_secundario': p_data.get('color_secundario', '#ffffff'),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(partidos_data)} partidos procesados.'))

        # 2. Importar Candidatos desde archivos individuales
        if not os.path.exists(candidatos_dir):
            self.stdout.write(self.style.ERROR(f'❌ No existe la carpeta: {candidatos_dir}'))
            return

        archivos = [f for f in os.listdir(candidatos_dir) if f.endswith('.json')]
        self.stdout.write(f'Procesando {len(archivos)} candidatos...')
        
        c_count = 0
        p_count = 0
        imported_ids = []

        for filename in archivos:
            filepath = os.path.join(candidatos_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                item = json.load(f)

            self.stdout.write(f"Procesando: {item.get('nombre', filename)}")

            # Buscar el partido por el nombre guardado en el json del candidato
            p_nombre = item.get('partido_nombre')
            if not p_nombre and 'partido' in item and isinstance(item['partido'], dict):
                p_nombre = item['partido'].get('nombre')
            
            partido = None
            if p_nombre:
                # 1. Búsqueda exacta
                partido = Partido.objects.filter(nombre=p_nombre).first()
                # 2. Búsqueda por siglas (si vienen en un objeto partido)
                if not partido and 'partido' in item and isinstance(item['partido'], dict):
                    siglas = item['partido'].get('siglas')
                    if siglas:
                        partido = Partido.objects.filter(siglas=siglas).first()
                # 3. Búsqueda flexible (contiene)
                if not partido:
                    partido = Partido.objects.filter(nombre__icontains=p_nombre).first()
            
            if not partido:
                # Autocrear partido para no perder el candidato
                p_final_nombre = p_nombre or "Independiente/Desconocido"
                partido, created = Partido.objects.get_or_create(
                    nombre=p_final_nombre,
                    defaults={'siglas': p_final_nombre[:10].upper()}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✅ Partido "{p_final_nombre}" autocreado.'))

            edad = item.get('edad')
            if edad is None:
                edad = 0 # Valor por defecto para campo no nulo

            scores = item.get('scores', {})
            slug = item.get('slug') or slugify(item['nombre'])
            
            # Check if candidate has meaningful data
            has_propuestas = len(item.get('propuestas', [])) > 0
            has_resumen = len(item.get('resumen_propuestas', '')) > 20
            
            if not has_propuestas and not has_resumen:
                def_score = 0
            else:
                def_score = 5
            
            candidato, _ = Candidato.objects.update_or_create(
                slug=slug,
                defaults={
                    'nombre': item['nombre'],
                    'partido': partido,
                    'foto_url': item.get('foto_url', ''),
                    'edad': edad,
                    'region': item.get('region', ''),
                    'profesion': item.get('profesion', ''),
                    'posicion_politica': item.get('posicion_politica', 'centro'),
                    'lema': item.get('lema', ''),
                    'biografia': item.get('biografia', ''),
                    'experiencia': item.get('experiencia', ''),
                    'antecedentes': item.get('antecedentes', ''),
                    'es_destacado': item.get('es_destacado', False),
                    'verificado': item.get('verificado', False),
                    'orden': item.get('orden', 0),
                    'link_plan_gobierno': item.get('link_plan_gobierno', ''),
                    'resumen_propuestas': item.get('resumen_propuestas', ''),
                    'propuestas_destacadas': item.get('propuestas_destacadas', []),
                    'posicionamiento_issues': item.get('posicionamiento_issues', {}),
                    'fuente_datos': item.get('fuente_datos', 'Plan de Gobierno JNE 2026'),
                    'score_economia': scores.get('score_economia', def_score),
                    'score_seguridad': scores.get('score_seguridad', def_score),
                    'score_medio_ambiente': scores.get('score_medio_ambiente', def_score),
                    'score_educacion': scores.get('score_educacion', def_score),
                    'score_salud': scores.get('score_salud', def_score),
                    'score_corrupcion': scores.get('score_corrupcion', def_score),
                    'score_descentralizacion': scores.get('score_descentralizacion', def_score),
                }
            )
            imported_ids.append(candidato.id)
            c_count += 1

            # Sincronizar Propuestas
            Propuesta.objects.filter(candidato=candidato).delete()
            for prop_data in item.get('propuestas', []):
                Propuesta.objects.create(
                    candidato=candidato,
                    tema=prop_data.get('tema', 'otros'),
                    titulo=prop_data.get('titulo', ''),
                    descripcion=prop_data.get('descripcion', ''),
                    icono=prop_data.get('icono', 'bi-star')
                )
                p_count += 1

        # Eliminar candidatos que no están en el nuevo set de archivos
        eliminados, _ = Candidato.objects.exclude(id__in=imported_ids).delete()
        if eliminados:
            self.stdout.write(self.style.WARNING(f'🗑️ {eliminados} candidatos antiguos eliminados de la BD.'))

        self.stdout.write(self.style.SUCCESS(
            f'🎉 Sincronización completa: {c_count} candidatos y {p_count} propuestas.'
        ))
