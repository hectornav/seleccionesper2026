"""
Carga 3 encuestas de referencia (IEP, Datum, CPI) con enlaces a las fuentes oficiales.
Puedes actualizar los porcentajes y añadir más encuestas desde /admin/ (modelo Encuesta).
Fuentes consultadas: sitios oficiales de cada encuestadora y publicaciones citadas (enero-febrero 2026).

Uso: python manage.py load_encuestas_ejemplo
     python manage.py load_encuestas_ejemplo --replace   # borra las actuales y vuelve a cargar estas 3
"""
from datetime import date
from django.core.management.base import BaseCommand
from candidatos.models import Encuesta


# Fuente: https://estudiosdeopinion.iep.org.pe/informe/enero-2026/
# Resultados publicados en La República (26/01/2026). Informe técnico y anexos en el enlace.
IEP_DATA = {
    'encuestadora': 'Instituto de Estudios Peruanos',
    'siglas': 'IEP',
    'fecha_terreno': date(2026, 1, 1),
    'fecha_publicacion': date(2026, 1, 26),
    'nota': 'Encuesta telefónica a celulares, nivel nacional. Informe de opinión enero 2026.',
    'resultados': [
        {'nombre': 'Rafael López Aliaga', 'porcentaje': 12.5},
        {'nombre': 'Keiko Fujimori', 'porcentaje': 7.8},
        {'nombre': 'Alfonso López Chau', 'porcentaje': 5.1},
        {'nombre': 'Carlos Álvarez', 'porcentaje': 4.8},
        {'nombre': 'César Acuña', 'porcentaje': 4.4},
        {'nombre': 'Mario Vizcarra', 'porcentaje': 3.2},
        {'nombre': 'Otros / B/V/N / No sabe', 'porcentaje': 62.2},
    ],
    'fuente_url': 'https://estudiosdeopinion.iep.org.pe/informe/enero-2026/',
    'orden': 0,
}

# Fuente: https://www.datum.com.pe/intencion-de-voto/
# Encuesta 16-20 enero 2026. Resultados por mes: Enero 2026.
DATUM_DATA = {
    'encuestadora': 'Datum Internacional',
    'siglas': 'Datum',
    'fecha_terreno': date(2026, 1, 20),
    'fecha_publicacion': date(2026, 1, 25),
    'nota': 'Nacional: 24 departamentos + Callao. Muestra 1,202 personas. Margen ±2.8%.',
    'resultados': [
        {'nombre': 'Rafael López Aliaga', 'porcentaje': 11.7},
        {'nombre': 'Keiko Fujimori', 'porcentaje': 8.0},
        {'nombre': 'Carlos Álvarez', 'porcentaje': 5.7},
        {'nombre': 'Alfonso López Chau', 'porcentaje': 4.6},
        {'nombre': 'Mario Vizcarra', 'porcentaje': 3.6},
        {'nombre': 'Ninguno / Blanco / Viciado', 'porcentaje': 25.9},
        {'nombre': 'No sabe', 'porcentaje': 18.4},
    ],
    'fuente_url': 'https://www.datum.com.pe/intencion-de-voto/',
    'orden': 1,
}

# Fuente: https://rpp.pe/politica/elecciones/intencion-de-voto-elecciones-presidenciales-peru-2026-encuesta-cpi-revela-liderazgo-de-rafael-lopez-aliaga-y-29-de-indecisos-noticia-1676700
# Encuesta CPI presentada por RPP. Febrero 2026.
CPI_DATA = {
    'encuestadora': 'CPI (Comunicación y Proyectos Integrales)',
    'siglas': 'CPI',
    'fecha_terreno': date(2026, 2, 1),
    'fecha_publicacion': date(2026, 2, 10),
    'nota': 'Población urbana nacional. Muestra ~1,200-1,300. Margen ±2.8%.',
    'resultados': [
        {'nombre': 'Rafael López Aliaga', 'porcentaje': 13.9},
        {'nombre': 'Keiko Fujimori', 'porcentaje': 7.0},
        {'nombre': 'Alfonso López Chau', 'porcentaje': 5.1},
        {'nombre': 'César Acuña', 'porcentaje': 4.4},
        {'nombre': 'Carlos Álvarez', 'porcentaje': 4.0},
        {'nombre': 'Indecisos', 'porcentaje': 29.1},
        {'nombre': 'Blanco / Nulo / Viciado', 'porcentaje': 16.1},
    ],
    'fuente_url': 'https://rpp.pe/politica/elecciones/intencion-de-voto-elecciones-presidenciales-peru-2026-encuesta-cpi-revela-liderazgo-de-rafael-lopez-aliaga-y-29-de-indecisos-noticia-1676700',
    'orden': 2,
}


class Command(BaseCommand):
    help = 'Carga 3 encuestas de referencia (IEP, Datum, CPI) con enlaces a fuentes oficiales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Elimina las encuestas actuales y vuelve a cargar IEP, Datum y CPI.',
        )

    def handle(self, *args, **options):
        if options.get('replace'):
            n = Encuesta.objects.count()
            Encuesta.objects.all().delete()
            self.stdout.write(f'Eliminadas {n} encuesta(s) anterior(es).')

        if Encuesta.objects.exists() and not options.get('replace'):
            self.stdout.write('Ya existen encuestas. Usa --replace para reemplazarlas por IEP, Datum y CPI.')
            return

        for data in (IEP_DATA, DATUM_DATA, CPI_DATA):
            Encuesta.objects.create(activo=True, **data)
            self.stdout.write(f'  ✓ {data["encuestadora"]} ({data["siglas"]}) – fuente: {data["fuente_url"][:50]}...')

        self.stdout.write(self.style.SUCCESS('\n3 encuestas cargadas (IEP, Datum, CPI). Actualiza datos desde /admin/ cuando tengas nuevas cifras.'))
