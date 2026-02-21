from django.db import models
from candidatos.models import Candidato


class Voto(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='votos')
    ip_address = models.GenericIPAddressField()
    # keep track of the session key (cookie) so that two visitors behind
    # the same NAT/proxy can each register one vote.  We don't enforce a
    # database-level uniqueness constraint here because session keys can be
    # blank on some clients and because we decide logic in the view.
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    fecha_voto = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'
        # you could also add unique_together = (('session_key',),)
        # or an index above, but the view handles the semantics.

    def __str__(self):
        return f"Voto para {self.candidato.nombre} desde {self.ip_address} (sesión {self.session_key})"
