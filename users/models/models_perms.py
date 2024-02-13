from django.db import models

class Perms(models.Model):
    class Meta:
        permissions = (
            ("puede_crear_cursos", "Puede crear cursos"),
        )
