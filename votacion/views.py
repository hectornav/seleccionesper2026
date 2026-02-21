from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Voto
from candidatos.models import Candidato
from django.views.decorators.http import require_POST

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_POST
def votar(request, candidato_id):
    ip = get_client_ip(request)
    # Check if this IP has already voted
    has_voted = Voto.objects.filter(ip_address=ip).exists()
    
    if has_voted:
        return JsonResponse({'success': False, 'message': 'Ya has registrado un voto.'}, status=400)
    
    try:
        candidato = Candidato.objects.get(id=candidato_id)
        Voto.objects.create(candidato=candidato, ip_address=ip)
        
        # Calculate new vote count and percentage to return
        total_votos = Voto.objects.count()
        votos_candidato = Voto.objects.filter(candidato=candidato).count()
        porcentaje = round((votos_candidato / total_votos) * 100, 1) if total_votos > 0 else 0
        
        return JsonResponse({
            'success': True,
            'message': '¡Tu voto ha sido registrado exitosamente!',
            'votos_totales': votos_candidato,
            'porcentaje': porcentaje
        })
    except Candidato.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Candidato no encontrado.'}, status=404)

def resultados(request):
    from django.db.models import Count
    total_votos = Voto.objects.count()
    
    # Get candidates with their vote counts
    candidatos_con_votos = Candidato.objects.annotate(num_votos=Count('votos')).filter(num_votos__gt=0).order_by('-num_votos')
    
    resultados_json = []
    for c in candidatos_con_votos:
        pct = round((c.num_votos / total_votos) * 100, 1) if total_votos > 0 else 0
        resultados_json.append({
            'id': c.id,
            'nombre': c.nombre,
            'partido': c.partido.siglas,
            'votos': c.num_votos,
            'porcentaje': pct,
            'color': c.partido.color_primario
        })
        
    return JsonResponse({
        'total_votos': total_votos,
        'resultados': resultados_json
    })

def resultados_view(request):
    from django.shortcuts import render
    return render(request, 'votacion/resultados.html')
