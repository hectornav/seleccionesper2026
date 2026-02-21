import requests
from .models import Visita

class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capturamos la IP real (detrás de proxies si aplica)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Procesar la respuesta primero
        response = self.get_response(request)

        # Evitar tracking de archivos estáticos, admin o local
        if not request.path.startswith(('/static/', '/media/', '/admin/')) and ip not in ('127.0.0.1', '::1'):
            try:
                # Solo guardamos si no es una IP local/privada
                # Usamos ip-api.com (Gratis hasta 45 req/min)
                response_geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
                data = response_geo.json()
                
                if data.get('status') == 'success':
                    Visita.objects.create(
                        ip=ip,
                        pais=data.get('country', 'Desconocido'),
                        ciudad=data.get('city', 'Desconocido'),
                        region=data.get('regionName', 'Desconocido'),
                        path=request.path,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                else:
                    # Si falla el geo, guardamos solo la IP
                    Visita.objects.create(
                        ip=ip,
                        path=request.path,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
            except Exception:
                # En caso de error de conexión, guardar registro básico para no romper la app
                try:
                    Visita.objects.create(
                        ip=ip,
                        path=request.path,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except:
                    pass

        return response
