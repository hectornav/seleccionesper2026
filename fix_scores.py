import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from candidatos.models import Candidato

for c in Candidato.objects.all():
    pos = c.posicion_politica.lower().replace('-', '_')
    if pos == 'izquierda' or pos == 'centro_izquierda':
        c.score_medio_ambiente = 2 if pos == 'izquierda' else 4
    elif pos == 'derecha' or pos == 'centro_derecha':
        c.score_medio_ambiente = 9 if pos == 'derecha' else 7
    else:  # centro
        c.score_medio_ambiente = 5
    
    if c.slug == 'keiko-fujimori-higuchi':
        c.score_medio_ambiente = 8
    elif c.slug == 'vladimir-roy-cerr-n-rojas':
        c.score_medio_ambiente = 2
    
    c.save()

print("Medio Ambiente Scores updated!")
