import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Candidato, Partido, Propuesta, PreguntaQuiz, ResultadoQuiz


def home(request):
    candidatos = Candidato.objects.select_related('partido').all()
    partidos = Partido.objects.all()
    total_candidatos = candidatos.count()

    posicion = request.GET.get('posicion', '')
    partido_id = request.GET.get('partido', '')
    busqueda = request.GET.get('q', '')

    if posicion:
        candidatos = candidatos.filter(posicion_politica=posicion)
    if partido_id:
        candidatos = candidatos.filter(partido_id=partido_id)
    if busqueda:
        candidatos = candidatos.filter(nombre__icontains=busqueda)

    context = {
        'candidatos': candidatos,
        'partidos': partidos,
        'total_candidatos': total_candidatos,
        'posicion_choices': Candidato.POSICION_CHOICES,
        'filtro_posicion': posicion,
        'filtro_partido': partido_id,
        'busqueda': busqueda,
    }
    return render(request, 'candidatos/home.html', context)


def candidato_detail(request, slug):
    candidato = get_object_or_404(Candidato.objects.select_related('partido'), slug=slug)
    propuestas = candidato.propuestas.all()
    propuestas_por_tema = {}
    for p in propuestas:
        tema = p.get_tema_display()
        if tema not in propuestas_por_tema:
            propuestas_por_tema[tema] = []
        propuestas_por_tema[tema].append(p)

    otros_candidatos = Candidato.objects.exclude(id=candidato.id).select_related('partido')[:4]

    context = {
        'candidato': candidato,
        'propuestas_por_tema': propuestas_por_tema,
        'otros_candidatos': otros_candidatos,
    }
    return render(request, 'candidatos/candidato_detail.html', context)


def comparar(request):
    candidatos_todos = Candidato.objects.select_related('partido').all()
    ids = request.GET.getlist('c')
    candidatos_seleccionados = []

    if ids:
        ids_validos = [i for i in ids if i.isdigit()]
        if ids_validos:
            candidatos_seleccionados = list(Candidato.objects.filter(id__in=ids_validos[:3]).select_related('partido'))

    temas = [
        {'key': 'economia', 'label': 'Economía', 'icono': 'bi-graph-up'},
        {'key': 'seguridad', 'label': 'Seguridad', 'icono': 'bi-shield-check'},
        {'key': 'educacion', 'label': 'Educación', 'icono': 'bi-book'},
        {'key': 'salud', 'label': 'Salud', 'icono': 'bi-heart-pulse'},
        {'key': 'medio_ambiente', 'label': 'Medio Ambiente', 'icono': 'bi-tree'},
    ]

    # Slots: siempre 3 posiciones (0 = vacío) para que cada select sepa qué candidato mostrar
    ids_int = [int(i) for i in ids if i.isdigit()]
    slots = (ids_int + [0, 0, 0])[:3]

    context = {
        'candidatos_todos': candidatos_todos,
        'candidatos_seleccionados': candidatos_seleccionados,
        'temas': temas,
        'ids_seleccionados': ids_int,
        'slots': slots,
    }
    return render(request, 'candidatos/comparar.html', context)


def quiz(request):
    preguntas = PreguntaQuiz.objects.prefetch_related('opciones').all()
    context = {
        'preguntas': preguntas,
        'candidatos_count': Candidato.objects.count(),
    }
    return render(request, 'candidatos/quiz.html', context)


@require_POST
def quiz_resultado(request):
    try:
        data = json.loads(request.body)
        respuestas = data.get('respuestas', {})

        candidatos = Candidato.objects.select_related('partido').all()
        resultados = []

        for candidato in candidatos:
            score_total = 0
            max_score = 0

            scores_candidato = {
                'economia': candidato.score_economia,
                'seguridad': candidato.score_seguridad,
                'medio_ambiente': candidato.score_medio_ambiente,
                'educacion': candidato.score_educacion,
                'salud': candidato.score_salud,
            }

            for pregunta_id, valor_usuario in respuestas.items():
                try:
                    pregunta = PreguntaQuiz.objects.get(id=pregunta_id)
                    score_candidato = scores_candidato.get(pregunta.tema, 5)
                    diferencia = abs(int(valor_usuario) - score_candidato)
                    similitud = max(0, 10 - diferencia)
                    score_total += similitud
                    max_score += 10
                except PreguntaQuiz.DoesNotExist:
                    pass

            porcentaje = round((score_total / max_score * 100) if max_score > 0 else 0)

            resultados.append({
                'id': candidato.id,
                'nombre': candidato.nombre,
                'slug': candidato.slug,
                'partido': candidato.partido.siglas,
                'partido_nombre': candidato.partido.nombre,
                'color_partido': candidato.partido.color_primario,
                'foto_url': candidato.get_foto(),
                'posicion': candidato.posicion_label(),
                'lema': candidato.lema,
                'porcentaje': porcentaje,
            })

        resultados.sort(key=lambda x: x['porcentaje'], reverse=True)
        top_candidato = None
        if resultados:
            top_candidato = Candidato.objects.get(id=resultados[0]['id'])
        
        # Save to DB
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if not ip:
            ip = request.META.get('REMOTE_ADDR')

        ResultadoQuiz.objects.create(
            ip=ip, 
            candidato_top=top_candidato,
            respuestas_json=respuestas
        )

        return JsonResponse({'resultados': resultados[:5]})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def sobre_el_proyecto(request):
    return render(request, 'candidatos/sobre.html')
