from django.db import models
from apps.proyectos.models import Proyecto
from apps.common.models import BaseModel

class CoeficienteCruce(BaseModel):
    """
    Coeficiente de equivalencia por tipo de vehículo.
    - is_standard=True, proyecto=None → librería global (semilla inicial)
    - is_standard=False, proyecto=X  → sobreescritura específica del proyecto
    """
    nomenclatura    = models.CharField(max_length=10)
    tipo_transporte = models.CharField(max_length=50)
    coeficiente     = models.FloatField()
    is_standard     = models.BooleanField(default=False)

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='coeficientes',
        blank=True,
        null=True,   # null = coeficiente estándar global
    )

    class Meta:
        constraints = [
            # Solo puede existir un coeficiente por nomenclatura dentro de un proyecto
            models.UniqueConstraint(
                fields=['nomenclatura', 'proyecto'],
                name='unique_coef_por_proyecto'
            ),
            # Y solo uno estándar global por nomenclatura
            models.UniqueConstraint(
                fields=['nomenclatura'],
                condition=models.Q(proyecto__isnull=True),
                name='unique_coef_estandar'
            ),
        ]

    def __str__(self):
        scope = f"[{self.proyecto}]" if self.proyecto else "[estándar]"
        return f"{self.nomenclatura} {scope} — {self.tipo_transporte} ({self.coeficiente})"


# managers.py (o dentro del mismo archivo)

class CoeficienteCruceManager(models.Manager):

    def resolver_para_proyecto(self, proyecto) -> dict[str, float]:
        """
        Devuelve un dict {nomenclatura: coeficiente} resolviendo
        la herencia: proyecto sobreescribe estándar.
        
        Uso: CoeficienteCruce.objects.resolver_para_proyecto(proyecto)
        """
        estandares = self.filter(proyecto__isnull=True).values('nomenclatura', 'coeficiente')
        propios    = self.filter(proyecto=proyecto).values('nomenclatura', 'coeficiente')

        # Estándares como base, propios sobreescriben
        coefs = {c['nomenclatura']: c['coeficiente'] for c in estandares}
        coefs.update({c['nomenclatura']: c['coeficiente'] for c in propios})
        return coefs