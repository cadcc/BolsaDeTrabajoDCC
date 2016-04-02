from django.db import models

# Create your models here.
class PruebaLoca(models.Model):
    nombre = models.CharField(max_length=24)

    def __unicode__(self):
        return self.nombre
