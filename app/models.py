from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    nombre = models.CharField(max_length=64)
    telefono = models.CharField(max_length=16)
    email = models.EmailField()
    direccion = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Region(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    nombre = models.CharField(max_length=64)
    region = models.ForeignKey(Region)

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=64)
    tipo = models.IntegerField()

    def __str__(self):
        return str(self.tipo) + ' - ' + self.nombre


class Oferta(models.Model):
    titulo = models.CharField(max_length=64)
    tipo = models.IntegerField()
    jornada = models.IntegerField()
    habilidades_deseadas = models.TextField()
    habilidades_requeridas = models.TextField()
    descripcion = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(max_length=16)
    requiere_experiencia = models.TextField()
    remunerado = models.BooleanField()
    sueldo_minimo = models.IntegerField()
    comentario_sueldo = models.TextField()
    caracteristicas = models.TextField()
    empresa = models.ForeignKey(Empresa)
    fecha_publicacion = models.DateTimeField()
    fecha_comienzo = models.DateTimeField()
    fecha_termino = models.DateTimeField()
    duracion_minima = models.IntegerField()
    direccion = models.CharField(max_length=64)
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    etiquetas = models.ManyToManyField(Etiqueta)
    comuna = models.ForeignKey(Comuna)

    def __str__(self):
        return self.titulo


class Usuario(models.Model):
    nombre = models.CharField(max_length=64)
    apellido = models.CharField(max_length=64)
    email = models.EmailField()
    fecha = models.DateField()
    roles = models.ManyToManyField(Rol)
    marcadores = models.ManyToManyField(Oferta)

    def __str__(self):
        return self.nombre + " " + self.apellido


class Validacion(models.Model):
    aceptado = models.BooleanField()
    comentario = models.TextField()
    fecha = models.DateTimeField()
    usuario = models.ForeignKey(Usuario)
    oferta = models.ForeignKey(Oferta)

    def __str__(self):
        return str(self.aceptado) + ' - ' + self.comentario


class Suscripcion(models.Model):
    periodicidad = models.IntegerField()
    etiquetas = models.ManyToManyField(Etiqueta)

    def __str__(self):
        return str(self.periodicidad)


class Valoracion(models.Model):
    comentario = models.TextField()
    fecha = models.DateTimeField()
    usuario = models.ForeignKey(Usuario)
    oferta = models.ForeignKey(Oferta)
    valor = models.IntegerField()

    def __str__(self):
        return self.usuario + ' - ' + str(self.valor) + ' - ' + self.comentario