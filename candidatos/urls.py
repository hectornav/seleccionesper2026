from django.urls import path
from . import views

app_name = 'candidatos'

urlpatterns = [
    path('', views.home, name='home'),
    path('candidato/<slug:slug>/', views.candidato_detail, name='candidato_detail'),
    path('comparar/', views.comparar, name='comparar'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz/resultado/', views.quiz_resultado, name='quiz_resultado'),
    path('sobre/', views.sobre_el_proyecto, name='sobre'),
]
