from django.db import models
from candidatos.models import Candidato

class Voto(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='votos')
    ip_address = models.GenericIPAddressField()
    fecha_voto = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent the same IP from voting multiple times for ANY candidate (or you can scope it, but usually it's one vote total)
        # However, to be simple, we just record IPs. We can do logic in views.
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'

    def __str__(self):
        return f"Voto para {self.candidato.nombre} desde {self.ip_address}"
