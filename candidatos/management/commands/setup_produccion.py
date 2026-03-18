"""
Comando único para preparar producción.
Ejecuta todo lo necesario usando candidatos_jne.json:
  1. Asigna rol_plancha (presidente, vp1, vp2) a todos los candidatos
  2. Importa hoja_vida_jne
  3. Importa plan_gobierno + resumen_propuestas + propuestas_destacadas + link_plan_gobierno
  4. Crea candidatos faltantes (VPs que no existen en la BD)

Uso: python manage.py setup_produccion
"""
import json
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from candidatos.models import Candidato, Partido


CARGO_TO_ROL = {
    'PRESIDENTE DE LA REPÚBLICA': 'presidente',
    'PRIMER VICEPRESIDENTE DE LA REPÚBLICA': 'vp1',
    'SEGUNDO VICEPRESIDENTE DE LA REPÚBLICA': 'vp2',
}


def normalize(name):
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    return ' '.join(name.lower().split())


def match_candidato(nombre_norm, candidatos_lookup):
    """Intenta matchear por nombre normalizado, luego por mejor coincidencia parcial."""
    if nombre_norm in candidatos_lookup:
        return candidatos_lookup[nombre_norm]
    # Match parcial: buscar el MEJOR match, no el primero
    parts = set(nombre_norm.split())
    best_match = None
    best_score = 0
    for key, cand in candidatos_lookup.items():
        key_parts = set(key.split())
        common = len(parts & key_parts)
        # Calcular score como proporción de palabras que coinciden
        max_words = min(len(parts), len(key_parts))
        if max_words == 0:
            continue
        ratio = common / max_words
        if common >= 2 and ratio >= 0.5 and common > best_score:
            best_score = common
            best_match = cand
    return best_match


def match_partido(org_politica, partidos_lookup):
    """Matchea partido por nombre."""
    STOPWORDS = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'en', 'por', 'para',
                 'partido', 'politico', 'alianza', 'electoral', 'a'}
    norm_org = normalize(org_politica)
    org_words = set(norm_org.split()) - STOPWORDS

    best_match = None
    best_score = 0
    for key, partido in partidos_lookup.items():
        p_words = set(key.split()) - STOPWORDS
        common = len(org_words & p_words)
        if common > best_score:
            best_score = common
            best_match = partido
    return best_match if best_score >= 2 else None


def clean_text(text):
    if not text:
        return ''
    text = text.replace('¿\t', '• ').replace('\t', ' ')
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Setup completo para producción usando candidatos_jne.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            default='candidatos_jne.json',
            help='Ruta al archivo JSON del JNE',
        )
        parser.add_argument(
            '--crear-faltantes',
            action='store_true',
            help='Crear candidatos VP que no existan en la BD',
        )

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        if not archivo.exists():
            self.stderr.write(self.style.ERROR(f'Archivo no encontrado: {archivo}'))
            return

        with open(archivo, encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== SETUP PRODUCCIÓN ===\n'))

        # Build lookups
        candidatos_lookup = {}
        for c in Candidato.objects.select_related('partido').all():
            candidatos_lookup[normalize(c.nombre)] = c

        partidos_lookup = {}
        for p in Partido.objects.all():
            partidos_lookup[normalize(p.nombre)] = p
            partidos_lookup[normalize(p.siglas)] = p

        stats = {
            'rol_asignado': 0,
            'hoja_vida': 0,
            'plan_gobierno': 0,
            'creados': 0,
            'no_match': [],
        }

        for party_data in data:
            org = party_data.get('organizacion_politica', '')
            plan = party_data.get('plan_gobierno', {})
            partido = match_partido(org, {normalize(p.nombre): p for p in Partido.objects.all()})

            for cand_jne in party_data.get('plancha', []):
                nombre = cand_jne.get('nombre_completo', '')
                cargo_jne = cand_jne.get('cargo', '')
                rol = CARGO_TO_ROL.get(cargo_jne, '')
                nombre_norm = normalize(nombre)

                candidato = match_candidato(nombre_norm, candidatos_lookup)

                # Si no existe y se pidió crear
                if not candidato and options.get('crear_faltantes') and partido and rol:
                    slug = slugify(nombre)
                    base_slug = slug
                    counter = 1
                    while Candidato.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    # Extraer datos del JNE para campos required
                    hv = cand_jne.get('hoja_vida', {})
                    dp = hv.get('datos_personales', {})
                    edu_basica = hv.get('educacion_basica', {})

                    # Calcular edad desde nacimiento
                    edad = 0
                    fecha_nac = dp.get('fecha_nacimiento', '')
                    if fecha_nac:
                        try:
                            from datetime import date
                            parts = fecha_nac.split('/')
                            if len(parts) == 3:
                                nac = date(int(parts[2]), int(parts[1]), int(parts[0]))
                                today = date.today()
                                edad = today.year - nac.year - ((today.month, today.day) < (nac.month, nac.day))
                        except (ValueError, IndexError):
                            pass

                    # Profesión desde educación
                    profesion = ''
                    for edu in hv.get('educacion_universitaria', [])[:1]:
                        profesion = edu.get('carrera', edu.get('especialidad', ''))
                    if not profesion:
                        profesion = edu_basica.get('profesion', dp.get('profesion', 'No especificado'))

                    candidato = Candidato(
                        nombre=nombre.title(),
                        slug=slug,
                        partido=partido,
                        rol_plancha=rol,
                        edad=edad or 0,
                        region=dp.get('departamento_nacimiento', dp.get('lugar_nacimiento', 'Perú')),
                        profesion=profesion or 'No especificado',
                        biografia=f"Candidato/a a {cargo_jne.title()} por {org}",
                        experiencia='Ver hoja de vida JNE',
                    )
                    candidato.save()
                    candidatos_lookup[nombre_norm] = candidato
                    stats['creados'] += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  + CREADO: {candidato.nombre} ({rol}) [{partido.siglas}]'
                    ))

                if not candidato:
                    stats['no_match'].append(f'{nombre} ({cargo_jne}) [{org}]')
                    continue

                # 1. Asignar rol_plancha
                if rol and candidato.rol_plancha != rol:
                    candidato.rol_plancha = rol
                    stats['rol_asignado'] += 1

                # 2. Importar hoja_vida_jne
                hoja_vida = cand_jne.get('hoja_vida', {})
                if hoja_vida:
                    hoja_vida['_partido_jne'] = {
                        'nombre': org,
                        'logo_url': party_data.get('logo_url', ''),
                    }
                    hoja_vida['_estado_candidato'] = cand_jne.get('estado_candidato', '')
                    hoja_vida['_foto_jne'] = cand_jne.get('foto_url', '')
                    hoja_vida['_cargo_jne'] = cargo_jne
                    hoja_vida['_dni'] = cand_jne.get('dni', '')

                    # Merge plan_gobierno into hoja_vida if this is the president
                    if rol == 'presidente' and plan:
                        hoja_vida['plan_gobierno'] = plan

                    candidato.hoja_vida_jne = hoja_vida
                    stats['hoja_vida'] += 1

                # 3. Plan de gobierno (solo para presidentes)
                if rol == 'presidente' and plan:
                    pdf_url = plan.get('pdf_completo_url') or plan.get('pdf_resumen_url', '')
                    if pdf_url and not candidato.link_plan_gobierno:
                        candidato.link_plan_gobierno = pdf_url

                    # Generar resumen
                    resumen = self._build_resumen(plan)
                    if resumen and (not candidato.resumen_propuestas or len(candidato.resumen_propuestas) < 100):
                        candidato.resumen_propuestas = resumen

                    # Generar propuestas destacadas
                    destacadas = self._build_destacadas(plan)
                    if destacadas and (not candidato.propuestas_destacadas or len(candidato.propuestas_destacadas) < 3):
                        candidato.propuestas_destacadas = destacadas[:5]

                    stats['plan_gobierno'] += 1

                candidato.save()
                self.stdout.write(f'  ✓ {candidato.nombre} → rol={rol}, hv={bool(hoja_vida)}, plan={rol == "presidente" and bool(plan)}')

        # Resumen
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== RESUMEN ==='))
        self.stdout.write(self.style.SUCCESS(f'  Roles asignados: {stats["rol_asignado"]}'))
        self.stdout.write(self.style.SUCCESS(f'  Hoja de vida importadas: {stats["hoja_vida"]}'))
        self.stdout.write(self.style.SUCCESS(f'  Planes de gobierno: {stats["plan_gobierno"]}'))
        if stats['creados']:
            self.stdout.write(self.style.SUCCESS(f'  Candidatos creados: {stats["creados"]}'))
        if stats['no_match']:
            self.stdout.write(self.style.WARNING(f'\n  Sin match ({len(stats["no_match"])}):'))
            for nm in stats['no_match']:
                self.stdout.write(self.style.WARNING(f'    ✗ {nm}'))

        # Verificación final
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== VERIFICACIÓN ==='))
        from django.db.models import Count
        for r in Candidato.objects.values('rol_plancha').annotate(n=Count('id')).order_by('rol_plancha'):
            self.stdout.write(f"  {r['rol_plancha'] or '(sin rol)'}: {r['n']}")

    def _build_resumen(self, plan):
        DIMENSION_MAP = {
            'dimension_social': 'Social',
            'dimension_economica': 'Económica',
            'dimension_ambiental': 'Ambiental',
            'dimension_institucional': 'Institucional',
        }
        parts = []
        for dim_key, label in DIMENSION_MAP.items():
            items = plan.get(dim_key, [])
            if items:
                obj = clean_text(items[0].get('objetivo', '')).split('\n')[0]
                if obj and len(obj) > 10:
                    parts.append(f"{label}: {obj[:150]}")
        return ' | '.join(parts)[:600] if parts else ''

    def _build_destacadas(self, plan):
        destacadas = []
        for dim_key in ['dimension_social', 'dimension_economica', 'dimension_ambiental', 'dimension_institucional']:
            for item in plan.get(dim_key, [])[:2]:
                meta = item.get('meta', '')
                if meta:
                    for line in clean_text(meta).split('\n'):
                        line = line.strip()
                        if line.startswith('•'):
                            line = line[1:].strip()
                        if len(line) > 15:
                            destacadas.append(line[:120])
                            break
                if len(destacadas) >= 5:
                    break
            if len(destacadas) >= 5:
                break
        return destacadas
