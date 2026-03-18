"""
Importa datos de hoja de vida del JNE desde candidatos_jne.json
y los asocia a los candidatos existentes en la base de datos.
"""
import json
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand
from candidatos.models import Candidato


def normalize(name):
    """Normaliza un nombre para comparación: sin tildes, minúsculas, sin espacios extra."""
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    return ' '.join(name.lower().split())


class Command(BaseCommand):
    help = 'Importa datos de hoja de vida del JNE (candidatos_jne.json) a los candidatos existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            default='candidatos_jne.json',
            help='Ruta al archivo JSON del JNE (default: candidatos_jne.json)',
        )

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        if not archivo.exists():
            self.stderr.write(self.style.ERROR(f'Archivo no encontrado: {archivo}'))
            return

        with open(archivo, encoding='utf-8') as f:
            data = json.load(f)

        # Construir lookup: nombre normalizado -> datos JNE
        jne_lookup = {}
        for partido in data:
            for candidato_jne in partido.get('plancha', []):
                nombre_norm = normalize(candidato_jne['nombre_completo'])
                jne_lookup[nombre_norm] = {
                    'candidato': candidato_jne,
                    'partido_jne': {
                        'nombre': partido['organizacion_politica'],
                        'logo_url': partido.get('logo_url', ''),
                    },
                }

        candidatos_db = Candidato.objects.select_related('partido').all()
        matched = 0
        not_matched = []

        for candidato in candidatos_db:
            nombre_norm = normalize(candidato.nombre)
            match = jne_lookup.get(nombre_norm)

            if not match:
                # Intentar match parcial (apellidos)
                for key, val in jne_lookup.items():
                    # Comparar si los apellidos coinciden
                    parts_db = nombre_norm.split()
                    parts_jne = key.split()
                    if len(parts_db) >= 2 and len(parts_jne) >= 2:
                        # Match por al menos 2 palabras en común
                        common = set(parts_db) & set(parts_jne)
                        if len(common) >= 3 or (len(common) >= 2 and len(parts_db) <= 3):
                            match = val
                            break

            if match:
                hoja_vida = match['candidato'].get('hoja_vida', {})
                # Agregar info del partido y estado del candidato JNE
                hoja_vida['_partido_jne'] = match['partido_jne']
                hoja_vida['_estado_candidato'] = match['candidato'].get('estado_candidato', '')
                hoja_vida['_foto_jne'] = match['candidato'].get('foto_url', '')
                hoja_vida['_cargo_jne'] = match['candidato'].get('cargo', '')
                hoja_vida['_dni'] = match['candidato'].get('dni', '')

                candidato.hoja_vida_jne = hoja_vida
                candidato.save(update_fields=['hoja_vida_jne'])
                matched += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {candidato.nombre} ← {match["candidato"]["nombre_completo"]}'
                ))
            else:
                not_matched.append(candidato.nombre)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Importados: {matched} candidatos'))
        if not_matched:
            self.stdout.write(self.style.WARNING(f'Sin match ({len(not_matched)}):'))
            for name in not_matched:
                self.stdout.write(self.style.WARNING(f'  ✗ {name}'))
