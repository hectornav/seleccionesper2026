from django.db import models
from django.utils.text import slugify


class Partido(models.Model):
    nombre = models.CharField(max_length=200)
    siglas = models.CharField(max_length=20)
    color_primario = models.CharField(max_length=7, default='#CC0000')
    color_secundario = models.CharField(max_length=7, default='#FFFFFF')
    logo = models.ImageField(upload_to='partidos/', blank=True, null=True)
    ideologia = models.CharField(max_length=100, blank=True)

    # Transparencia ONPE (Agregados)
    transparencia_onpe_total_candidatos = models.IntegerField(default=0, help_text='Total de candidatos presentados en el registro ONPE')
    transparencia_onpe_presentaron = models.IntegerField(default=0, help_text='Número de candidatos que declararon cuentas dentro/fuera de plazo')
    transparencia_porcentaje = models.FloatField(default=0.0, help_text='Porcentaje de cumplimiento (0 a 100)')
    transparencia_ultima_actualizacion = models.DateField(null=True, blank=True, help_text='Última vez que se actualizó con reporte ONPE')

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

    ROL_PLANCHA_CHOICES = [
        ('presidente', 'Candidato/a a la Presidencia'),
        ('vp1', '1er Vicepresidente/a'),
        ('vp2', '2do Vicepresidente/a'),
    ]

    ROL_PLANCHA_LABELS = {
        'presidente': '🇵🇪 Candidato/a Presidencial',
        'vp1': '1er Vicepresidente/a',
        'vp2': '2do Vicepresidente/a',
    }

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
    score_corrupcion = models.IntegerField(default=5, help_text='1=Investigado/StatusQuo, 10=AnticorrupcionRadical')
    score_descentralizacion = models.IntegerField(default=5, help_text='1=Centralista, 10=Federalista/Regionalista')

    # Metadatos
    ultima_actualizacion = models.DateField(auto_now=True)
    fuente_datos = models.CharField(max_length=200, default='Plan de Gobierno JNE 2026')
    verificado = models.BooleanField(default=False)

    # Estado
    fallecido = models.BooleanField(default=False, help_text='Marcar si el candidato ha fallecido')
    fecha_fallecimiento = models.DateField(null=True, blank=True, help_text='Fecha de fallecimiento (opcional)')

    # Transparencia Financiera (ONPE)
    info_financiera_estado = models.CharField(max_length=50, blank=True, help_text='Ej: DENTRO DE PLAZO, NO PRESENTO')
    info_financiera_ingresos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Ingresos declarados (S/)')
    info_financiera_gastos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Gastos declarados (S/)')
    info_financiera_fecha = models.DateField(null=True, blank=True, help_text='Fecha de presentación en ONPE')

    orden = models.IntegerField(default=0)

    # Hoja de Vida JNE (datos completos del JSON del JNE)
    hoja_vida_jne = models.JSONField(default=dict, blank=True, help_text='Datos completos de la hoja de vida del JNE')

    # Plancha Presidencial
    rol_plancha = models.CharField(
        max_length=20,
        choices=ROL_PLANCHA_CHOICES,
        default='presidente',
        help_text='Rol dentro de la plancha presidencial',
    )

    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['orden', 'nombre']

    def save(self, *args, **kwargs):
        # ensure posicion_politica always matches one of the choice keys
        if self.posicion_politica:
            # lower case and replace spaces/hyphens with underscore
            cleaned = self.posicion_politica.lower().replace('-', '_').replace(' ', '_')
            # also map a couple of common variants
            variants = {
                'centroizquierda': 'centro_izquierda',
                'centroderecha': 'centro_derecha',
            }
            self.posicion_politica = variants.get(cleaned, cleaned)
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

    def rol_plancha_label(self):
        return self.ROL_PLANCHA_LABELS.get(self.rol_plancha, self.rol_plancha)

    def companeros_plancha(self):
        """Devuelve los otros miembros de la plancha presidencial (mismo partido).
        Si soy presidente: devuelve solo VPs.
        Si soy VP: devuelve presidente + otro VP.
        """
        if self.rol_plancha == 'presidente':
            roles = ['vp1', 'vp2']
        else:
            roles = ['presidente', 'vp1', 'vp2']
        return (
            Candidato.objects
            .filter(partido=self.partido, rol_plancha__in=roles)
            .exclude(pk=self.pk)
            .order_by('rol_plancha')
        )


class CandidatoCongresal(models.Model):
    """Candidatos al Congreso (Diputados, Senadores, Parlamento Andino) con info financiera ONPE."""
    CARGO_CHOICES = [
        ('DIPUTADO', 'Diputado'),
        ('SENADOR', 'Senador'),
        ('REPRESENTANTE DEL PARLAMENTO ANDINO', 'Parlamento Andino'),
    ]

    ESTADO_CHOICES = [
        ('DENTRO DE PLAZO', 'Dentro de plazo'),
        ('FUERA DE PLAZO', 'Fuera de plazo'),
        ('NO PRESENTO', 'No presentó'),
    ]

    GENERO_CHOICES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]

    dni = models.CharField(max_length=15)
    nombre = models.CharField(max_length=250)
    genero = models.CharField(max_length=15, choices=GENERO_CHOICES, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    cargo = models.CharField(max_length=60, choices=CARGO_CHOICES)
    organizacion_politica = models.CharField(max_length=200)
    partido = models.ForeignKey(Partido, on_delete=models.SET_NULL, null=True, blank=True, related_name='congresales')
    departamento = models.CharField(max_length=80, blank=True)
    provincia = models.CharField(max_length=80, blank=True)
    distrito = models.CharField(max_length=80, blank=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='NO PRESENTO')
    fecha_presentacion = models.CharField(max_length=30, blank=True)
    ingresos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gastos = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    entrega = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = 'Candidato Congresal'
        verbose_name_plural = 'Candidatos Congresales'
        ordering = ['organizacion_politica', 'cargo', 'nombre']
        indexes = [
            models.Index(fields=['cargo']),
            models.Index(fields=['departamento']),
            models.Index(fields=['organizacion_politica']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.cargo} - {self.organizacion_politica})"


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


class Encuesta(models.Model):
    """Estadísticas de intención de voto de encuestadoras oficiales del Perú."""
    encuestadora = models.CharField(max_length=120, help_text='Ej: IEP, CPI, Datum, etc.')
    siglas = models.CharField(max_length=20, blank=True, help_text='Siglas de la encuestadora')
    fecha_terreno = models.DateField(help_text='Fecha de realización del trabajo de campo')
    fecha_publicacion = models.DateField(null=True, blank=True)
    resultados = models.JSONField(
        default=list,
        help_text='Lista de {"nombre": "Apellido Nombre", "porcentaje": 15.5}. Ordenar por porcentaje descendente.'
    )
    fuente_url = models.URLField(blank=True, help_text='Enlace a la publicación oficial')
    nota = models.CharField(max_length=300, blank=True, help_text='Ej: Solo Lima, nacional, etc.')
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Encuesta de intención de voto'
        verbose_name_plural = 'Encuestas de intención de voto'
        ordering = ['-fecha_terreno', '-fecha_publicacion', 'orden']

    def __str__(self):
        return f"{self.encuestadora} – {self.fecha_terreno}"


class Sugerencia(models.Model):
    TIPO_CHOICES = [
        ('mejora', 'Mejora de la plataforma'),
        ('dato', 'Corrección de datos'),
        ('idea', 'Idea nueva'),
        ('otro', 'Otro'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='mejora')
    mensaje = models.TextField(help_text='Sugerencia o comentario del ciudadano')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sugerencia'
        verbose_name_plural = 'Sugerencias'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} – {self.fecha.strftime('%d/%m/%Y %H:%M')}"
