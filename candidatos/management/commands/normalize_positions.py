from django.core.management.base import BaseCommand
from candidatos.models import Candidato


class Command(BaseCommand):
    help = 'Clean up posicion_politica values to match model choices'

    def handle(self, *args, **options):
        updated = 0
        for c in Candidato.objects.all():
            original = c.posicion_politica
            if original:
                cleaned = original.lower().replace('-', '_').replace(' ', '_')
                variants = {
                    'centroizquierda': 'centro_izquierda',
                    'centroderecha': 'centro_derecha',
                }
                newval = variants.get(cleaned, cleaned)
                if newval != original:
                    c.posicion_politica = newval
                    c.save()
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Normalized {updated} records"))
