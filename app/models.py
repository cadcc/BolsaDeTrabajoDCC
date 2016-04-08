from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=64)
    apellido = models.CharField(max_length=64)
    email = models.EmailField()
    fecha = models.DateField()
    roles = models.ManyToManyField(Rol)

    def __str__(self):
        return self.nombre + " " + self.apellido

class Rol(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=64)
    tipo = models.IntegerField()

    def __str__(self):
        return self.tipo + " - " + self.nombre

class Suscripcion(models.Model):
    periodicidad = models.IntegerField()
    etiquetas = models.ManyToManyField(Etiqueta)

    def __str__(self):
        return self.periodicidad
