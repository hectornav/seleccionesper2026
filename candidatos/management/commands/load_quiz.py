from django.core.management.base import BaseCommand
from candidatos.models import PreguntaQuiz, OpcionQuiz


PREGUNTAS = [
    # ── 1. ECONOMÍA (score_economia: 1=Estado, 10=Libre mercado) ──
    {
        "texto": "🛒 Un litro de aceite cuesta el doble que hace un año. ¿Qué debería hacer el gobierno?",
        "tema": "economia_empleo",
        "orden": 1,
        "opciones": [
            {"texto": "Que el Estado produzca alimentos básicos y los venda a precio justo", "valor": 1, "orden": 1},
            {"texto": "Controlar los precios y sancionar a las empresas que abusan", "valor": 3, "orden": 2},
            {"texto": "Bajar aranceles para que entren más productos importados y haya competencia", "valor": 6, "orden": 3},
            {"texto": "No meterse: el mercado se regula solo y si intervienen es peor", "valor": 9, "orden": 4},
        ],
    },

    # ── 2. SEGURIDAD (score_seguridad: 1=Derechos, 10=Mano dura) ──
    {
        "texto": "🚨 Te enteras que un vecino de tu barrio fue asaltado por tercera vez este mes. ¿Qué solución apoyarías?",
        "tema": "seguridad_ciudadana",
        "orden": 2,
        "opciones": [
            {"texto": "Más programas para jóvenes en riesgo: deporte, becas y empleo. La delincuencia nace de la pobreza", "valor": 2, "orden": 1},
            {"texto": "Más patrullaje policial, cámaras y mejor iluminación en las calles", "valor": 5, "orden": 2},
            {"texto": "Penas más duras y que los delincuentes no salgan de la cárcel tan rápido", "valor": 8, "orden": 3},
            {"texto": "Que entren los militares a patrullar las calles. Tolerancia cero", "valor": 10, "orden": 4},
        ],
    },

    # ── 3. EDUCACIÓN (score_educacion: 1=Pública, 10=Privada) ──
    {
        "texto": "📚 Tu sobrino termina el colegio y no tiene plata para una universidad privada. ¿Qué debería pasar?",
        "tema": "educacion",
        "orden": 3,
        "opciones": [
            {"texto": "Toda la educación superior debería ser gratuita, punto. Que el Estado invierta más", "valor": 1, "orden": 1},
            {"texto": "Más vacantes en universidades públicas de calidad y reformar las que están mal", "valor": 3, "orden": 2},
            {"texto": "Darle una beca para que elija el mejor lugar, sea público o privado", "valor": 7, "orden": 3},
            {"texto": "Si se esforzó, las privadas deberían tener créditos accesibles. La competencia mejora la calidad", "valor": 9, "orden": 4},
        ],
    },

    # ── 4. SALUD (score_salud: 1=Universal, 10=Privada) ──
    {
        "texto": "🏥 Tu mamá necesita una operación urgente. En el hospital público le dicen que espere 4 meses. ¿Qué debería cambiar?",
        "tema": "salud",
        "orden": 4,
        "opciones": [
            {"texto": "Invertir masivamente en hospitales públicos para que no haya colas. Salud gratuita para todos", "valor": 1, "orden": 1},
            {"texto": "Mejorar el SIS y EsSalud, pero que las clínicas privadas atiendan a quienes no pueden esperar", "valor": 5, "orden": 2},
            {"texto": "Darle a cada peruano un seguro para que elija dónde atenderse: hospital o clínica", "valor": 7, "orden": 3},
            {"texto": "Que las clínicas privadas puedan crecer más y asociarse con el Estado. La competencia mejora todo", "valor": 9, "orden": 4},
        ],
    },

    # ── 5. MEDIO AMBIENTE (score_medio_ambiente: 1=Bajo compromiso, 10=Alto compromiso) ──
    {
        "texto": "🌿 Descubren oro en una zona de selva virgen cerca de un río que abastece a varios pueblos. ¿Qué se debería hacer?",
        "tema": "medio_ambiente",
        "orden": 5,
        "opciones": [
            {"texto": "Que se explote el oro, genera empleo y el país necesita crecer. Ya se verá lo del río", "valor": 1, "orden": 1},
            {"texto": "Permitir la minería pero con reglas ambientales y que la empresa pague por los daños", "valor": 4, "orden": 2},
            {"texto": "Solo si pasa una evaluación ambiental estricta y las comunidades están de acuerdo", "valor": 7, "orden": 3},
            {"texto": "Ni hablar. Ese río y esa selva no se tocan. Hay que proteger la Amazonía cueste lo que cueste", "valor": 10, "orden": 4},
        ],
    },

    # ── 6. CORRUPCIÓN (score_corrupcion: 1=Status quo, 10=Anticorrupción radical) ──
    {
        "texto": "🐀 Un alcalde robó millones pero hizo pistas, colegios y un hospital. La gente del pueblo lo defiende. ¿Tú qué opinas?",
        "tema": "anticorrupcion",
        "orden": 6,
        "opciones": [
            {"texto": "Si hizo obras, por lo menos hizo algo. Todos roban, al menos este trabajó", "valor": 1, "orden": 1},
            {"texto": "Estuvo mal, pero hay que mejorar los controles para que no se repita", "valor": 4, "orden": 2},
            {"texto": "Debe ser investigado y sancionado. Las obras no borran el robo", "valor": 7, "orden": 3},
            {"texto": "Cárcel y que le quiten todo. Que nunca más pueda ser candidato a nada", "valor": 10, "orden": 4},
        ],
    },

    # ── 7. DESCENTRALIZACIÓN (score_descentralizacion: 1=Centralista, 10=Federalista) ──
    {
        "texto": "🗺️ En tu región hay plata del canon minero pero las obras las decide Lima. ¿Qué debería pasar?",
        "tema": "reforma_estado",
        "orden": 7,
        "opciones": [
            {"texto": "Que Lima decida, porque los gobernadores regionales se roban la plata", "valor": 1, "orden": 1},
            {"texto": "Que Lima supervise pero que la región proponga en qué gastar", "valor": 4, "orden": 2},
            {"texto": "Que la región maneje su presupuesto con rendición de cuentas transparente", "valor": 7, "orden": 3},
            {"texto": "Autonomía total: que cada región recaude y gaste según sus necesidades, como un sistema federal", "valor": 10, "orden": 4},
        ],
    },
]


class Command(BaseCommand):
    help = "Carga las preguntas y opciones del Test Electoral en la base de datos"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina todas las preguntas existentes antes de cargar",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            eliminadas, _ = PreguntaQuiz.objects.all().delete()
            self.stdout.write(f"Eliminadas {eliminadas} preguntas existentes.")

        if PreguntaQuiz.objects.exists() and not options["reset"]:
            self.stdout.write(self.style.WARNING(
                "Ya existen preguntas en la BD. Usa --reset para reemplazarlas."
            ))
            return

        total_preguntas = 0
        total_opciones = 0

        for p_data in PREGUNTAS:
            pregunta = PreguntaQuiz.objects.create(
                texto=p_data["texto"],
                tema=p_data["tema"],
                orden=p_data["orden"],
            )
            total_preguntas += 1

            for o_data in p_data["opciones"]:
                OpcionQuiz.objects.create(
                    pregunta=pregunta,
                    texto=o_data["texto"],
                    valor=o_data["valor"],
                    orden=o_data["orden"],
                )
                total_opciones += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Cargadas {total_preguntas} preguntas con {total_opciones} opciones."
        ))
