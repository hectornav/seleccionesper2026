from django.urls import path
from . import views

app_name = 'votacion'

urlpatterns = [
    path('votar/<int:candidato_id>/', views.votar, name='votar'),
    path('api/resultados/', views.resultados, name='resultados'),
    path('intencion/', views.resultados_view, name='intencion'),
]
