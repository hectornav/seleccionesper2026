"""
Importa candidatos congresales desde el reporte ONPE (reporte_if.xlsx).
"""
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from candidatos.models import CandidatoCongresal, Partido


def normalize(name):
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    return ' '.join(name.lower().split())


class Command(BaseCommand):
    help = 'Importa candidatos congresales desde reporte_if.xlsx (ONPE)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            default='reporte_if.xlsx',
            help='Ruta al archivo Excel de ONPE (default: reporte_if.xlsx)',
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Borrar todos los registros existentes antes de importar',
        )

    def handle(self, *args, **options):
        try:
            import openpyxl
        except ImportError:
            self.stderr.write(self.style.ERROR('Necesitas openpyxl: pip install openpyxl'))
            return

        archivo = Path(options['archivo'])
        if not archivo.exists():
            self.stderr.write(self.style.ERROR(f'Archivo no encontrado: {archivo}'))
            return

        if options['limpiar']:
            deleted, _ = CandidatoCongresal.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Eliminados {deleted} registros existentes'))

        # Build partido lookup
        partido_lookup = {}
        for p in Partido.objects.all():
            partido_lookup[normalize(p.nombre)] = p
            partido_lookup[normalize(p.siglas)] = p

        wb = openpyxl.load_workbook(archivo, read_only=True)
        ws = wb.active

        rows = list(ws.iter_rows(min_row=6, values_only=True))
        wb.close()

        batch = []
        skipped = 0

        for row in rows:
            if row[0] is None:
                continue

            nombre = (row[4] or '').strip()
            if not nombre:
                skipped += 1
                continue

            org_politica = (row[2] or '').strip()

            # Try to match partido
            partido = partido_lookup.get(normalize(org_politica))

            # Parse ingresos/gastos
            ingresos = None
            gastos = None
            try:
                if row[15] and row[15] != '-':
                    ingresos = Decimal(str(row[15]))
            except (InvalidOperation, ValueError):
                pass
            try:
                if row[16] and row[16] != '-':
                    gastos = Decimal(str(row[16]))
            except (InvalidOperation, ValueError):
                pass

            edad = None
            if row[6]:
                try:
                    edad = int(row[6])
                except (ValueError, TypeError):
                    pass

            batch.append(CandidatoCongresal(
                dni=(str(row[3] or '')).strip(),
                nombre=nombre,
                genero=(row[5] or '').strip().upper(),
                edad=edad,
                cargo=(row[7] or '').strip().upper(),
                organizacion_politica=org_politica,
                partido=partido,
                departamento=(row[9] or '').strip(),
                provincia=(row[10] or '').strip(),
                distrito=(row[11] or '').strip(),
                entrega=(row[12] or '').strip(),
                estado=(row[13] or 'NO PRESENTO').strip(),
                fecha_presentacion=(str(row[14] or '')).strip() if row[14] and row[14] != '-' else '',
                ingresos=ingresos,
                gastos=gastos,
            ))

        # Bulk create
        created = CandidatoCongresal.objects.bulk_create(batch, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f'Importados: {len(created)} candidatos congresales'))
        if skipped:
            self.stdout.write(self.style.WARNING(f'Omitidos (sin nombre): {skipped}'))

        # Summary
        from django.db.models import Count
        resumen = CandidatoCongresal.objects.values('cargo').annotate(total=Count('id'))
        for r in resumen:
            self.stdout.write(f"  {r['cargo']}: {r['total']}")
