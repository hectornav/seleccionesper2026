import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Candidato, Partido, Propuesta, PreguntaQuiz, ResultadoQuiz, Encuesta, Sugerencia


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
            # Omitir candidatos que aún no han sido evaluados (scores en 0)
            if sum([candidato.score_economia, candidato.score_seguridad, candidato.score_medio_ambiente, candidato.score_educacion, candidato.score_salud, candidato.score_corrupcion, candidato.score_descentralizacion]) == 0:
                continue

            score_total = 0
            max_score = 0

            scores_candidato = {
                'economia_empleo': candidato.score_economia,
                'seguridad_ciudadana': candidato.score_seguridad,
                'medio_ambiente': candidato.score_medio_ambiente,
                'educacion': candidato.score_educacion,
                'salud': candidato.score_salud,
                'anticorrupcion': candidato.score_corrupcion,
                'reforma_estado': candidato.score_descentralizacion,
            }
            
            pesos = {
                'economia_empleo': 2.0,
                'seguridad_ciudadana': 2.0,
                'educacion': 1.5,
                'salud': 1.5,
                'medio_ambiente': 1.0,
                'anticorrupcion': 1.5,
                'reforma_estado': 1.0,
            }

            for pregunta_id, valor_usuario in respuestas.items():
                try:
                    pregunta = PreguntaQuiz.objects.get(id=pregunta_id)
                    score_candidato = scores_candidato.get(pregunta.tema, 5)
                    peso = pesos.get(pregunta.tema, 1.0)
                    
                    diferencia = abs(int(valor_usuario) - score_candidato)
                    # Metodología ponderada con penalización no lineal (penaliza distancias grandes)
                    penalizacion = (diferencia / 9.0) ** 1.5
                    similitud = max(0, 10 - (10 * penalizacion)) * peso
                    
                    score_total += similitud
                    max_score += 10 * peso
                except PreguntaQuiz.DoesNotExist:
                    pass

            porcentaje = round((score_total / max_score * 100) if max_score > 0 else 0)

            # Brújula de Confianza: datos verificables
            posiciones = candidato.posicionamiento_issues or {}
            total_issues = len(posiciones) if posiciones else 0
            issues_claros = sum(1 for v in posiciones.values() if v and v != 'no especificado') if posiciones else 0
            transparencia = round(issues_claros / total_issues * 100) if total_issues > 0 else 0

            ant_lower = (candidato.antecedentes or '').lower()
            # Positive indicators: real legal issues (affirmative phrasing only)
            indicadores_alerta = [
                'múltiples procesos', 'acusaciones de corrupción',
                'sentenciado', 'condenado', 'prófugo', 'prisión preventiva',
                'lavado de activos', 'organización criminal',
                'inhabilitado', 'vacado', 'tiene procesos',
                'acusado de', 'investigado por',
            ]
            tiene_antecedentes = bool(
                candidato.antecedentes
                and len(candidato.antecedentes.strip()) > 10
                and any(ind in ant_lower for ind in indicadores_alerta)
            )

            # Posiciones en temas clave formateadas
            labels_issues = {
                'asamblea_constituyente': '🏛️ Constituyente',
                'libre_comercio_tlc': '💹 Libre comercio',
                'privatizacion_empresas_estado': '🏭 Privatización',
                'relaciones_venezuela_cuba': '🌎 Venezuela/Cuba',
                'pena_muerte': '⚖️ Pena de muerte',
            }
            posiciones_fmt = []
            for key, label in labels_issues.items():
                val = posiciones.get(key)
                if val and val != 'no especificado':
                    posiciones_fmt.append({'label': label, 'valor': val, 'claro': True})
                elif key in posiciones:
                    posiciones_fmt.append({'label': label, 'valor': 'No se pronuncia', 'claro': False})

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
                # Brújula de Confianza
                'transparencia': transparencia,
                'score_anticorrupcion': candidato.score_corrupcion,
                'tiene_antecedentes': tiene_antecedentes,
                'antecedentes_texto': candidato.antecedentes if tiene_antecedentes else '',
                'posiciones': posiciones_fmt,
                'experiencia': candidato.experiencia[:150] if candidato.experiencia else '',
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


def encuestas_popup(request):
    """Devuelve el HTML del contenido del modal de encuestas (para cargar vía AJAX).

    Se muestran todas las encuestas activas ordenadas por fecha para poder ver
    la evolución histórica en el tiempo.
    """
    encuestas = Encuesta.objects.filter(activo=True)
    return render(request, 'candidatos/partial_encuestas_popup.html', {'encuestas': encuestas})


def sugerencias(request):
    enviado = False
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'mejora')
        mensaje = request.POST.get('mensaje', '').strip()
        if mensaje and len(mensaje) <= 2000:
            tipos_validos = [c[0] for c in Sugerencia.TIPO_CHOICES]
            if tipo not in tipos_validos:
                tipo = 'mejora'
            Sugerencia.objects.create(tipo=tipo, mensaje=mensaje)
            enviado = True
    return render(request, 'candidatos/sugerencias.html', {'enviado': enviado})
