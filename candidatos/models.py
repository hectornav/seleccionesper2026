from django.db import models
from django.utils.text import slugify


class Partido(models.Model):
    nombre = models.CharField(max_length=200)
    siglas = models.CharField(max_length=20)
    color_primario = models.CharField(max_length=7, default='#CC0000')
    color_secundario = models.CharField(max_length=7, default='#FFFFFF')
    logo = models.ImageField(upload_to='partidos/', blank=True, null=True)
    ideologia = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.siglas} - {self.nombre}"


class Candidato(models.Model):
    POSICION_CHOICES = [
        ('izquierda', 'Izquierda'),
        ('centro_izquierda', 'Centro-Izquierda'),
        ('centro', 'Centro'),
        ('centro_derecha', 'Centro-Derecha'),
        ('derecha', 'Derecha'),
    ]

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='candidatos')
    foto = models.ImageField(upload_to='candidatos/', blank=True, null=True)
    foto_url = models.URLField(blank=True, help_text='URL de foto si no hay archivo subido')
    edad = models.IntegerField()
    region = models.CharField(max_length=100)
    profesion = models.CharField(max_length=200)
    posicion_politica = models.CharField(max_length=20, choices=POSICION_CHOICES, default='centro')
    posicion_politica_detalle = models.CharField(max_length=200, blank=True, help_text='Descripción detallada de la posición política')
    biografia = models.TextField()
    experiencia = models.TextField()
    antecedentes = models.TextField(blank=True, default='', help_text='Antecedentes legales o judiciales conocidos')
    lema = models.CharField(max_length=300, blank=True)
    es_destacado = models.BooleanField(default=False)

    # Información del Plan de Gobierno
    link_plan_gobierno = models.URLField(blank=True, help_text='Link al PDF del plan de gobierno en JNE')
    resumen_propuestas = models.TextField(blank=True, help_text='Resumen general de las propuestas')
    propuestas_destacadas = models.JSONField(default=list, blank=True, help_text='Lista de propuestas destacadas')

    # Posicionamiento en temas clave (JSON)
    posicionamiento_issues = models.JSONField(default=dict, blank=True, help_text='Posición en temas clave como Asamblea Constituyente, Privatización, etc.')

    # Scores para el quiz (1-10)
    score_economia = models.IntegerField(default=5, help_text='1=Estado, 10=Libre mercado')
    score_seguridad = models.IntegerField(default=5, help_text='1=Derechos, 10=Mano dura')
    score_medio_ambiente = models.IntegerField(default=5, help_text='1=Conservador, 10=Progresista')
    score_educacion = models.IntegerField(default=5, help_text='1=Pública, 10=Privada')
    score_salud = models.IntegerField(default=5, help_text='1=Universal, 10=Privada')

    # Metadatos
    ultima_actualizacion = models.DateField(auto_now=True)
    fuente_datos = models.CharField(max_length=200, default='Plan de Gobierno JNE 2026')
    verificado = models.BooleanField(default=False)

    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['orden', 'nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def get_foto(self):
        if self.foto:
            return self.foto.url
        if self.foto_url:
            return self.foto_url
        return None

    def posicion_label(self):
        return dict(self.POSICION_CHOICES).get(self.posicion_politica, '')

    def posicion_color(self):
        colors = {
            'izquierda': '#e74c3c',
            'centro_izquierda': '#e67e22',
            'centro': '#27ae60',
            'centro_derecha': '#2980b9',
            'derecha': '#8e44ad',
        }
        return colors.get(self.posicion_politica, '#95a5a6')


class Propuesta(models.Model):
    TEMA_CHOICES = [
        ('seguridad_ciudadana', 'Seguridad Ciudadana'),
        ('economia_empleo', 'Economía y Empleo'),
        ('salud', 'Salud'),
        ('educacion', 'Educación'),
        ('anticorrupcion', 'Lucha Anticorrupción'),
        ('infraestructura_agua_saneamiento', 'Infraestructura, Agua y Saneamiento'),
        ('medio_ambiente', 'Medio Ambiente'),
        ('reforma_estado', 'Reforma del Estado'),
        ('mypes_emprendimiento', 'MYPEs y Emprendimiento'),
        ('genero_inclusion', 'Género e Inclusión'),
        ('pensiones_adulto_mayor', 'Pensiones y Adulto Mayor'),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    ICONO_POR_TEMA = {
        'seguridad_ciudadana': 'bi-shield-check',
        'economia_empleo': 'bi-graph-up-arrow',
        'salud': 'bi-heart-pulse',
        'educacion': 'bi-book',
        'anticorrupcion': 'bi-eye',
        'infraestructura_agua_saneamiento': 'bi-water',
        'medio_ambiente': 'bi-tree',
        'reforma_estado': 'bi-bank',
        'mypes_emprendimiento': 'bi-shop',
        'genero_inclusion': 'bi-people',
        'pensiones_adulto_mayor': 'bi-person-heart',
    }

    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='propuestas')
    tema = models.CharField(max_length=50, choices=TEMA_CHOICES)
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    icono = models.CharField(max_length=50, default='bi-star')

    class Meta:
        verbose_name = 'Propuesta'
        verbose_name_plural = 'Propuestas'
        ordering = ['prioridad', 'tema']

    def __str__(self):
        return f"{self.candidato.nombre} - {self.get_tema_display()}"

    def save(self, *args, **kwargs):
        if not self.icono or self.icono == 'bi-star':
            self.icono = self.ICONO_POR_TEMA.get(self.tema, 'bi-star')
        super().save(*args, **kwargs)


class PreguntaQuiz(models.Model):
    texto = models.CharField(max_length=500)
    tema = models.CharField(max_length=50, choices=Propuesta.TEMA_CHOICES)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Pregunta Quiz'
        verbose_name_plural = 'Preguntas Quiz'

    def __str__(self):
        return self.texto


class OpcionQuiz(models.Model):
    pregunta = models.ForeignKey(PreguntaQuiz, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=300)
    valor = models.IntegerField(help_text='Valor en escala 1-10 que indica la posición política')
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.pregunta} - {self.texto}"


class Visita(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    pais = models.CharField(max_length=100, default="Desconocido")
    ciudad = models.CharField(max_length=100, default="Desconocido")
    region = models.CharField(max_length=100, default="Desconocido")
    path = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.pais} - {self.ciudad} ({self.fecha})"


class ResultadoQuiz(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    candidato_top = models.ForeignKey(Candidato, on_delete=models.SET_NULL, null=True, blank=True)
    respuestas_json = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Resultado de Quiz'
        verbose_name_plural = 'Resultados de Quiz'
        ordering = ['-fecha']

    def __str__(self):
        candidato_nombre = self.candidato_top.nombre if self.candidato_top else "Ninguno"
        return f"Test de {self.ip} - Top: {candidato_nombre}"
