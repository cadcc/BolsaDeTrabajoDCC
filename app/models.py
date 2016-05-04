from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    nombre = models.CharField(max_length=64)
    sitio_web = models.CharField(max_length=64)
    logo = models.FileField(upload_to='logos')
    direccion = models.CharField(max_length=64)
    descripcion = models.TextField()
    puntaje = models.IntegerField(default=0)
    verificada = models.BooleanField(default=False)

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


class TipoEtiqueta(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=64)
    validado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo = models.ForeignKey(TipoEtiqueta)

    def __str__(self):
        return str(self.tipo) + ' - ' + self.nombre


class Jornada(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Oferta(models.Model):
    empresa = models.ForeignKey(Empresa)
    jornada = models.ForeignKey(Jornada)
    comuna = models.ForeignKey(Comuna)
    titulo = models.CharField(max_length=64)
    nombre_encargado = models.CharField(max_length=64)
    tipo = models.CharField(max_length=16)
    habilidades_deseadas = models.TextField()
    habilidades_requeridas = models.TextField()
    descripcion = models.TextField()
    email_encargado = models.EmailField()
    telefono_encargado = models.CharField(max_length=16)
    hora_ingreso = models.TimeField()
    hora_salida = models.TimeField()
    comentario_jornada = models.TextField()
    requiere_experiencia = models.TextField()
    remunerado = models.IntegerField()
    sueldo_minimo = models.IntegerField()
    comentario_sueldo = models.TextField()
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField()
    fecha_comienzo = models.DateTimeField()
    fecha_termino = models.DateTimeField()
    duracion_minima = models.IntegerField()
    se_ofrece = models.TextField()
    comentario_duracion = models.TextField()
    publicada = models.BooleanField(default=False)
    puntuacion = models.IntegerField(default=0)
    visitas = models.IntegerField(default=0)
    notificar = models.BooleanField()
    direccion = models.CharField(max_length=64)
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    etiquetas = models.ManyToManyField(Etiqueta)

    def __str__(self):
        return self.titulo


class Usuario(AbstractUser):
    documento = models.FileField(upload_to='user_document', null=True)
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


class Periodicidad(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return str(self.nombre)


class Suscripcion(models.Model):
    usuario = models.ForeignKey(Usuario)
    periodicidad = models.ForeignKey(Periodicidad)
    fecha_ultimo_envio = models.DateTimeField()
    etiquetas = models.ManyToManyField(Etiqueta)

    def __str__(self):
        return 'suscripcion: usuario ' + self.usuario + ' con periodicidad ' + self.periodicidad


class ValoracionOferta(models.Model):
    usuario = models.ForeignKey(Usuario)
    oferta = models.ForeignKey(Oferta)
    valor = models.IntegerField()
    comentario = models.TextField()
    prioritario = models.BooleanField(default=False)
    reportes = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField()

    def __str__(self):
        return self.usuario + ' - ' + str(self.valor) + ' - ' + self.comentario


class AdvertenciaValoracionOferta(models.Model):
    valoracion = models.ForeignKey(ValoracionOferta)
    resuelto = models.BooleanField(default=False)
    modificado = models.BooleanField(default=False)
    advertencia = models.TextField()

    def __str__(self):
        return self.advertencia


class ValoracionEmpresa(models.Model):
    usuario = models.ForeignKey(Usuario)
    empresa = models.ForeignKey(Empresa)
    valor = models.IntegerField()
    comentario = models.TextField()
    prioritario = models.BooleanField(default=False)
    reportes = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField()

    def __str__(self):
        return self.usuario + ' - ' + str(self.valor) + ' - ' + self.comentario


class AdvertenciaValoracionEmpresa(models.Model):
    valoracion = models.ForeignKey(ValoracionEmpresa)
    resuelto = models.BooleanField(default=False)
    modificado = models.BooleanField(default=False)
    advertencia = models.TextField()

    def __str__(self):
        return self.advertencia


class Visita(models.Model):
    usuario = models.ForeignKey(Usuario)
    oferta = models.ForeignKey(Oferta)
    veces_visitado = models.IntegerField(default=0)

    def __str__(self):
        return str(self.veces_visitado)
