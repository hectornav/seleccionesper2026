import json
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Candidato, CandidatoCongresal, Partido, Propuesta, PreguntaQuiz, ResultadoQuiz, Encuesta, Sugerencia


def home(request):
    candidatos = Candidato.objects.select_related('partido').filter(rol_plancha='presidente')
    partidos = Partido.objects.filter(
        candidatos__rol_plancha='presidente'
    ).distinct()
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

    # Prefetch VPs and congresales count per partido
    candidatos = list(candidatos)
    partido_ids = [c.partido_id for c in candidatos]
    vps = Candidato.objects.filter(
        partido_id__in=partido_ids,
        rol_plancha__in=['vp1', 'vp2'],
    ).select_related('partido').order_by('rol_plancha')

    congresales_count = {}
    for cc in CandidatoCongresal.objects.filter(partido_id__in=partido_ids).values('partido_id').annotate(total=models.Count('id')):
        congresales_count[cc['partido_id']] = cc['total']

    vps_by_partido = {}
    for vp in vps:
        vps_by_partido.setdefault(vp.partido_id, []).append(vp)

    for c in candidatos:
        c.vps = vps_by_partido.get(c.partido_id, [])
        c.total_congresales = congresales_count.get(c.partido_id, 0)

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

    plancha = candidato.companeros_plancha().select_related('partido')

    # Procesar datos JNE para el template
    jne = candidato.hoja_vida_jne or {}
    hv_jne = {}
    if jne:
        hv_jne = {
            'datos_personales': jne.get('datos_personales', {}),
            'educacion_universitaria': jne.get('educacion_universitaria', []),
            'educacion_posgrado': jne.get('educacion_posgrado', []),
            'educacion_basica': jne.get('educacion_basica', {}),
            'experiencia_laboral': jne.get('experiencia_laboral', []),
            'cargos_partidarios': jne.get('cargos_partidarios', []),
            'sentencias_penales': jne.get('sentencias_penales', []),
            'sentencias_obligatorias': jne.get('sentencias_obligatorias', []),
            'ingresos': jne.get('ingresos', {}),
            'bienes_inmuebles': jne.get('bienes_inmuebles', []),
            'bienes_muebles': jne.get('bienes_muebles', []),
            'info_adicional': jne.get('info_adicional', []),
            'anotaciones_marginales': jne.get('anotaciones_marginales', []),
            'estado_candidato': jne.get('_estado_candidato', ''),
            'dni': jne.get('_dni', ''),
        }
        # Calcular patrimonio total
        patrimonio = 0
        for bien in hv_jne['bienes_inmuebles']:
            patrimonio += bien.get('autovaluo', 0) or 0
        for bien in hv_jne['bienes_muebles']:
            patrimonio += bien.get('valor', 0) or 0
        hv_jne['patrimonio_total'] = patrimonio
        hv_jne['tiene_sentencias'] = bool(hv_jne['sentencias_penales'] or hv_jne['sentencias_obligatorias'])
        # Normalizar campos de educación para evitar KeyError en templates
        for edu in hv_jne['educacion_universitaria']:
            edu.setdefault('carrera', edu.get('especialidad', ''))
            edu.setdefault('universidad', edu.get('centro_estudio', ''))
        for edu in hv_jne['educacion_posgrado']:
            edu.setdefault('especialidad', edu.get('carrera', ''))
            edu.setdefault('centro_estudio', edu.get('universidad', ''))
        for exp in hv_jne['experiencia_laboral']:
            exp.setdefault('cargo', exp.get('ocupacion', ''))
            exp.setdefault('centro_trabajo', '')

    # Congresales del mismo partido (diputados y senadores)
    congresales_partido = []
    congresales_total = 0
    if candidato.partido:
        congresales_qs = CandidatoCongresal.objects.filter(partido=candidato.partido)
        congresales_total = congresales_qs.count()
        # Mostrar una muestra representativa: primeros de cada cargo
        congresales_partido = list(
            congresales_qs.order_by('cargo', 'nombre')[:12]
        )

    # Plan de Gobierno por dimensiones (del JNE)
    plan_gobierno = jne.get('plan_gobierno', {})
    plan_dims = []
    dim_labels = {
        'dimension_social': ('Social', 'bi-people-fill', '#e11d48'),
        'dimension_economica': ('Económica', 'bi-graph-up-arrow', '#2563eb'),
        'dimension_ambiental': ('Ambiental', 'bi-tree-fill', '#16a34a'),
        'dimension_institucional': ('Institucional', 'bi-bank2', '#9333ea'),
    }
    for dim_key, (label, icon, color) in dim_labels.items():
        items = plan_gobierno.get(dim_key, [])
        if items:
            plan_dims.append({
                'label': label,
                'icon': icon,
                'color': color,
                'items': items,
            })
    plan_pdfs = {
        'completo': plan_gobierno.get('pdf_completo_url', ''),
        'resumen': plan_gobierno.get('pdf_resumen_url', ''),
    }

    context = {
        'candidato': candidato,
        'propuestas_por_tema': propuestas_por_tema,
        'otros_candidatos': otros_candidatos,
        'plancha': plancha,
        'hv_jne': hv_jne,
        'congresales_partido': congresales_partido,
        'congresales_total': congresales_total,
        'plan_dims': plan_dims,
        'plan_pdfs': plan_pdfs,
    }
    return render(request, 'candidatos/candidato_detail.html', context)


def comparar(request):
    candidatos_todos = Candidato.objects.filter(rol_plancha='presidente').select_related('partido').all()
    ids = request.GET.getlist('c')
    candidatos_seleccionados = []

    if ids:
        ids_validos = [i for i in ids if i.isdigit()]
        if ids_validos:
            candidatos_seleccionados = list(Candidato.objects.filter(id__in=ids_validos[:3]).select_related('partido'))

    # Enriquecer candidatos seleccionados con datos JNE
    # Usamos una lista de dicts que se pasan en paralelo al template
    candidatos_jne_data = []
    for c in candidatos_seleccionados:
        jne = c.hoja_vida_jne or {}
        dp = jne.get('datos_personales', {})

        # Formación académica
        formacion = []
        for edu in jne.get('educacion_posgrado', [])[:2]:
            formacion.append(edu.get('especialidad', edu.get('carrera', '')))
        for edu in jne.get('educacion_universitaria', [])[:2]:
            formacion.append(edu.get('carrera', edu.get('especialidad', '')))

        # Experiencia top
        experiencia = []
        for exp in jne.get('experiencia_laboral', [])[:3]:
            cargo = exp.get('cargo', exp.get('ocupacion', ''))
            centro = exp.get('centro_trabajo', '')
            experiencia.append(f"{cargo} — {centro}" if centro else cargo)

        # Patrimonio e ingresos
        patrimonio = 0
        for bien in jne.get('bienes_inmuebles', []):
            patrimonio += bien.get('autovaluo', 0) or 0
        for bien in jne.get('bienes_muebles', []):
            patrimonio += bien.get('valor', 0) or 0
        ingresos = jne.get('ingresos', {})

        # Sentencias
        tiene_sentencias = bool(jne.get('sentencias_penales') or jne.get('sentencias_obligatorias'))

        # Plan de gobierno ejes
        plan = jne.get('plan_gobierno', {})
        ejes = []
        dim_labels_cmp = {
            'dimension_social': 'Social',
            'dimension_economica': 'Económica',
            'dimension_ambiental': 'Ambiental',
            'dimension_institucional': 'Institucional',
        }
        for dk, dl in dim_labels_cmp.items():
            items = plan.get(dk, [])
            if items:
                obj = items[0].get('objetivo', '')[:100]
                ejes.append({'dim': dl, 'objetivo': obj + ('...' if len(items[0].get('objetivo', '')) > 100 else '')})

        candidatos_jne_data.append({
            'candidato': c,
            'formacion': formacion[:3],
            'experiencia': experiencia,
            'patrimonio': patrimonio,
            'ingresos': ingresos.get('total', 0) or 0,
            'tiene_sentencias': tiene_sentencias,
            'ejes': ejes,
            'plan_pdf': plan.get('pdf_completo_url', ''),
        })

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
        'candidatos_jne': candidatos_jne_data,
        'temas': temas,
        'ids_seleccionados': ids_int,
        'slots': slots,
    }
    return render(request, 'candidatos/comparar.html', context)


def quiz(request):
    preguntas = PreguntaQuiz.objects.prefetch_related('opciones').all()
    context = {
        'preguntas': preguntas,
        'candidatos_count': Candidato.objects.filter(rol_plancha='presidente').count(),
    }
    return render(request, 'candidatos/quiz.html', context)


@require_POST
def quiz_resultado(request):
    try:
        data = json.loads(request.body)
        respuestas = data.get('respuestas', {})

        candidatos = Candidato.objects.filter(rol_plancha='presidente').select_related('partido')
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

            # Datos del Plan de Gobierno (JNE) para enriquecer resultados
            jne_data = candidato.hoja_vida_jne or {}
            plan_gob = jne_data.get('plan_gobierno', {})
            ejes_resumen = []
            dim_names = {
                'dimension_social': 'Social',
                'dimension_economica': 'Económica',
                'dimension_ambiental': 'Ambiental',
                'dimension_institucional': 'Institucional',
            }
            for dim_key, dim_label in dim_names.items():
                items = plan_gob.get(dim_key, [])
                if items:
                    obj = items[0].get('objetivo', '')
                    if obj:
                        ejes_resumen.append({
                            'dim': dim_label,
                            'objetivo': obj[:120] + ('...' if len(obj) > 120 else ''),
                        })

            # Sentencias del JNE
            sentencias_penales = jne_data.get('sentencias_penales', [])
            sentencias_oblig = jne_data.get('sentencias_obligatorias', [])
            tiene_sentencias_jne = bool(sentencias_penales or sentencias_oblig)

            # Formación académica resumida
            formacion = []
            for edu in jne_data.get('educacion_posgrado', [])[:1]:
                formacion.append(edu.get('especialidad', edu.get('carrera', '')))
            for edu in jne_data.get('educacion_universitaria', [])[:1]:
                formacion.append(edu.get('carrera', edu.get('especialidad', '')))

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
                # Datos JNE enriquecidos
                'ejes_plan': ejes_resumen[:4],
                'tiene_sentencias_jne': tiene_sentencias_jne,
                'formacion': formacion[:2],
                'plan_pdf': plan_gob.get('pdf_completo_url', ''),
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


def transparencia_partidos(request):
    # Solo mostrar partidos que tengan datos de ONPE (al menos un candidato documentado en el reporte)
    partidos = Partido.objects.filter(transparencia_onpe_total_candidatos__gt=0).order_by('-transparencia_porcentaje', '-transparencia_onpe_total_candidatos')
    
    # Calcular promedios globales si hay partidos
    total_general = sum(p.transparencia_onpe_total_candidatos for p in partidos)
    total_presentaron = sum(p.transparencia_onpe_presentaron for p in partidos)
    promedio_global = (total_presentaron / total_general * 100) if total_general else 0
    
    context = {
        'partidos': partidos,
        'promedio_global': promedio_global,
        'total_general': total_general,
        'total_presentaron': total_presentaron
    }
    return render(request, 'candidatos/transparencia_partidos.html', context)


def congresales(request):
    """Vista de candidatos congresales con filtros por cargo, departamento, partido y búsqueda."""
    from django.db.models import Count, Q

    cargo = request.GET.get('cargo', '')
    departamento = request.GET.get('departamento', '')
    partido = request.GET.get('partido', '')
    estado = request.GET.get('estado', '')
    busqueda = request.GET.get('q', '')
    page_num = request.GET.get('page', '1')

    qs = CandidatoCongresal.objects.all()

    if cargo:
        qs = qs.filter(cargo=cargo)
    if departamento:
        qs = qs.filter(departamento=departamento)
    if partido:
        qs = qs.filter(organizacion_politica=partido)
    if estado:
        qs = qs.filter(estado=estado)
    if busqueda:
        qs = qs.filter(Q(nombre__icontains=busqueda) | Q(dni__icontains=busqueda))

    # Opciones para filtros
    cargos_opciones = (
        CandidatoCongresal.objects
        .values_list('cargo', flat=True)
        .distinct()
        .order_by('cargo')
    )
    departamentos_opciones = (
        CandidatoCongresal.objects
        .values_list('departamento', flat=True)
        .distinct()
        .order_by('departamento')
    )
    partidos_opciones = (
        CandidatoCongresal.objects
        .values_list('organizacion_politica', flat=True)
        .distinct()
        .order_by('organizacion_politica')
    )

    # Estadísticas rápidas
    total = qs.count()
    total_presentaron = qs.exclude(estado='NO PRESENTO').count()
    porcentaje_presento = round(total_presentaron / total * 100, 1) if total else 0

    total_no_presentaron = total - total_presentaron

    # Stats por cargo (del conjunto filtrado)
    stats_cargo = qs.values('cargo').annotate(total=Count('id')).order_by('cargo')

    # Paginación
    from django.core.paginator import Paginator
    qs = qs.order_by('organizacion_politica', 'cargo', 'nombre')
    paginator = Paginator(qs, 50)
    try:
        page = paginator.page(int(page_num))
    except Exception:
        page = paginator.page(1)

    context = {
        'page': page,
        'total': total,
        'total_presentaron': total_presentaron,
        'total_no_presentaron': total_no_presentaron,
        'porcentaje_presento': porcentaje_presento,
        'stats_cargo': stats_cargo,
        'cargos_opciones': cargos_opciones,
        'departamentos_opciones': departamentos_opciones,
        'partidos_opciones': partidos_opciones,
        'filtro_cargo': cargo,
        'filtro_departamento': departamento,
        'filtro_partido': partido,
        'filtro_estado': estado,
        'busqueda': busqueda,
    }
    return render(request, 'candidatos/congresales.html', context)


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
