"""
Importa datos de plan_gobierno del JNE (candidatos_jne.json)
y los asocia a los candidatos presidenciales existentes.
Actualiza: link_plan_gobierno, resumen_propuestas, hoja_vida_jne['plan_gobierno'],
y crea Propuestas por dimensión.
"""
import json
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand
from candidatos.models import Candidato, Partido, Propuesta


def normalize(name):
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    return ' '.join(name.lower().split())


# Map plan_gobierno dimensions to Propuesta temas
DIMENSION_MAP = {
    'dimension_social': {
        'label': 'Dimensión Social',
        'temas': ['salud', 'educacion', 'seguridad_ciudadana', 'genero_inclusion', 'pensiones_adulto_mayor'],
    },
    'dimension_economica': {
        'label': 'Dimensión Económica',
        'temas': ['economia_empleo', 'mypes_emprendimiento', 'infraestructura_agua_saneamiento'],
    },
    'dimension_ambiental': {
        'label': 'Dimensión Ambiental',
        'temas': ['medio_ambiente'],
    },
    'dimension_institucional': {
        'label': 'Dimensión Institucional',
        'temas': ['anticorrupcion', 'reforma_estado'],
    },
}


def clean_text(text):
    """Limpia caracteres raros del texto JNE."""
    if not text:
        return ''
    # Replace ¿\t with bullet points
    text = text.replace('¿\t', '• ')
    text = text.replace('\t', ' ')
    # Remove leading numbers like "1 " at the start
    lines = text.strip().split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return '\n'.join(cleaned)


def build_resumen(plan_gobierno):
    """Genera un resumen de propuestas a partir de las 4 dimensiones."""
    parts = []
    for dim_key, dim_info in DIMENSION_MAP.items():
        items = plan_gobierno.get(dim_key, [])
        if not items:
            continue
        objectives = []
        for item in items[:3]:  # Max 3 per dimension for resumen
            obj = item.get('objetivo', '')
            if obj:
                # Extract first sentence/line as summary
                first_line = clean_text(obj).split('\n')[0]
                # Remove leading "1 Objetivos estratégicos:" etc
                for prefix in ['Objetivos estratégicos:', 'Objetivo general:', 'Objetivo:']:
                    if prefix.lower() in first_line.lower():
                        idx = first_line.lower().index(prefix.lower()) + len(prefix)
                        first_line = first_line[idx:].strip()
                        break
                if first_line and len(first_line) > 10:
                    objectives.append(first_line[:150])
        if objectives:
            parts.append(f"{dim_info['label']}: {'; '.join(objectives[:2])}")
    return ' | '.join(parts)[:600] if parts else ''


class Command(BaseCommand):
    help = 'Importa plan_gobierno del JNE a candidatos presidenciales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            default='candidatos_jne.json',
            help='Ruta al archivo JSON del JNE (default: candidatos_jne.json)',
        )
        parser.add_argument(
            '--crear-propuestas',
            action='store_true',
            help='Crear/actualizar objetos Propuesta por dimensión',
        )

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        if not archivo.exists():
            self.stderr.write(f'Archivo no encontrado: {archivo}')
            return

        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)

        STOPWORDS = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'en', 'por', 'para',
                     'partido', 'politico', 'alianza', 'electoral', 'a'}

        # Build lookup: all partidos with their presidents
        all_partidos = list(Partido.objects.all())
        presidents_by_partido = {}
        for c in Candidato.objects.filter(rol_plancha='presidente').select_related('partido'):
            presidents_by_partido[c.partido_id] = c

        matched = 0
        updated_propuestas = 0

        for party_data in data:
            org = party_data.get('organizacion_politica', '')
            plan = party_data.get('plan_gobierno', {})
            if not plan:
                continue

            norm_org = normalize(org)
            org_words = set(norm_org.split()) - STOPWORDS

            # Find president by matching partido name across ALL partidos
            presidente = None
            best_score = 0
            for p in all_partidos:
                if p.id not in presidents_by_partido:
                    continue
                p_words = set(normalize(p.nombre).split()) - STOPWORDS
                common = len(org_words & p_words)
                if common > best_score:
                    best_score = common
                    presidente = presidents_by_partido[p.id]

            if not presidente or best_score < 2:
                self.stdout.write(self.style.WARNING(f'  ✗ No match: {org} (best_score={best_score})'))
                continue

            # Update link_plan_gobierno
            pdf_url = plan.get('pdf_completo_url') or plan.get('pdf_resumen_url', '')
            if pdf_url and not presidente.link_plan_gobierno:
                presidente.link_plan_gobierno = pdf_url

            # Store plan_gobierno in hoja_vida_jne
            hv = presidente.hoja_vida_jne or {}
            hv['plan_gobierno'] = plan
            presidente.hoja_vida_jne = hv

            # Generate resumen if current one is short/generic
            resumen = build_resumen(plan)
            if resumen and (not presidente.resumen_propuestas or len(presidente.resumen_propuestas) < 100):
                presidente.resumen_propuestas = resumen

            # Generate propuestas_destacadas from objectives
            destacadas = []
            for dim_key in ['dimension_social', 'dimension_economica', 'dimension_ambiental', 'dimension_institucional']:
                for item in plan.get(dim_key, [])[:2]:
                    meta = item.get('meta', '')
                    if meta:
                        cleaned = clean_text(meta)
                        # Get first bullet point
                        for line in cleaned.split('\n'):
                            line = line.strip()
                            if line.startswith('•'):
                                line = line[1:].strip()
                            if len(line) > 15 and not line.lower().startswith('principales'):
                                destacadas.append(line[:120])
                                break
                    if len(destacadas) >= 5:
                        break
                if len(destacadas) >= 5:
                    break

            if destacadas and (not presidente.propuestas_destacadas or len(presidente.propuestas_destacadas) < 3):
                presidente.propuestas_destacadas = destacadas[:5]

            presidente.save()
            matched += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ {presidente.nombre} ({presidente.partido.siglas}) — plan importado'))

            # Create Propuesta objects if requested
            if options.get('crear_propuestas'):
                for dim_key, dim_info in DIMENSION_MAP.items():
                    items = plan.get(dim_key, [])
                    if not items:
                        continue

                    # Assign tema based on dimension
                    temas = dim_info['temas']

                    for i, item in enumerate(items):
                        tema = temas[i % len(temas)]
                        objetivo = clean_text(item.get('objetivo', ''))
                        problema = clean_text(item.get('problema', ''))
                        meta = clean_text(item.get('meta', ''))

                        if not objetivo:
                            continue

                        titulo = f"{dim_info['label']}: {objetivo.split(chr(10))[0][:200]}"
                        descripcion = ''
                        if problema:
                            descripcion += f"**Problemática:**\n{problema}\n\n"
                        descripcion += f"**Objetivo:**\n{objetivo}\n\n"
                        if meta:
                            descripcion += f"**Metas:**\n{meta}"

                        # Check if similar propuesta exists
                        existing = Propuesta.objects.filter(
                            candidato=presidente,
                            tema=tema,
                            titulo__icontains=titulo[:50],
                        ).first()

                        if not existing:
                            Propuesta.objects.create(
                                candidato=presidente,
                                tema=tema,
                                titulo=titulo[:300],
                                descripcion=descripcion,
                                prioridad='alta' if i == 0 else 'media',
                            )
                            updated_propuestas += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nResultado: {matched}/{len(data)} candidatos actualizados'
        ))
        if options.get('crear_propuestas'):
            self.stdout.write(self.style.SUCCESS(
                f'Propuestas creadas: {updated_propuestas}'
            ))
