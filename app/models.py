from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class UsuarioBase(AbstractUser):
    pass

    def __str__(self):
        return self.first_name + " " + self.last_name

class Rol(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    sitio_web = models.CharField(max_length=64, null=True)
    logo = models.FileField(upload_to='logos', null=True)
    direccion = models.CharField(max_length=64, null=True)
    descripcion = models.TextField(null=True)
    puntaje = models.IntegerField(default=0)
    validada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def url_encoded_name(self):
        return self.nombre.replace(' ', '-')

class Encargado(UsuarioBase):
    administrador = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

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
        return self.nombre


class Jornada(models.Model):
    OPCIONES_JORNADA = (
        ('FullTime', 'FullTime'),
        ('PartTime', 'PartTime'),
    )
    nombre = models.CharField(max_length=16,
                              choices=OPCIONES_JORNADA,
                              default='FullTime')

    def __str__(self):
        return self.nombre


class Oferta(models.Model):

    OPCIONES_TIPO = (
        ('Práctica', 'Práctica'),
        ('Memoria', 'Memoria'),
        ('Trabajo', 'Trabajo'),
    )
    OPCIONES_REMUNERACION = (
        ('Mensual', 'Mensual'),
        ('Por Determinar', 'Por Determinar'),
        ('Sin Remuneración', 'Sin Remuneración'),
    )

    # Datos Oferta
    titulo = models.CharField(max_length=64)
    empresa = models.ForeignKey(Empresa)
    tipo = models.CharField(max_length=9,
                            choices=OPCIONES_TIPO)
    habilidades_deseadas = models.TextField()
    habilidades_requeridas = models.TextField()
    descripcion = models.TextField()
    requiere_experiencia = models.TextField(null=True)
    se_ofrece = models.TextField()
    fecha_comienzo = models.DateField()
    fecha_termino = models.DateField()
    duracion_minima = models.IntegerField()
    comentario_duracion = models.TextField()
    direccion = models.CharField(max_length=64)
    comuna = models.ForeignKey(Comuna)

    # Datos Encargado
    nombre_encargado = models.CharField(max_length=64)
    email_encargado = models.EmailField()
    telefono_encargado = models.CharField(max_length=16)

    # Jornada
    jornada = models.ForeignKey(Jornada)
    comentario_jornada = models.TextField()
    hora_ingreso = models.TimeField()
    hora_salida = models.TimeField()

    # Remuneracion
    remunerado = models.CharField(max_length=19,
                                  choices=OPCIONES_REMUNERACION)
    sueldo_minimo = models.IntegerField()
    comentario_sueldo = models.TextField()

    # Estado de la Oferta
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    publicada = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(null=True)
    puntuacion = models.IntegerField(default=0)
    visitas = models.IntegerField(default=0)
    notificar = models.BooleanField()
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('oferta-detail', kwargs={'pk': self.pk})

    def formatted_salary(self):
        price = str(self.sueldo_minimo)
        clp = ""
        x = "xxx"
        c = 1
        for i in range(len(price)-1, -1, -1):
            clp = price[i]+clp;
            if c % 3 == 0 and c != len(price):
                x = clp
                clp = '.'+clp
            c = c+1
        return '$' + clp;


class Usuario(UsuarioBase):
    documento = models.FileField(upload_to='user_document', null=True)
    roles = models.ManyToManyField(Rol)
    marcadores = models.ManyToManyField(Oferta)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Validacion(models.Model):
    aceptado = models.BooleanField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario)
    oferta = models.ForeignKey(Oferta)

    def __str__(self):
        return 'Aprobada' if self.aceptado else 'No Aprobada'


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
    prioritario = models.BooleanField()
    reportes = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.usuario) + ' - ' + str(self.valor) + ' - ' +self.comentario

    def value(self):
        return int(self.valor/20)


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
    prioritario = models.BooleanField()
    reportes = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.usuario) + ' - ' + str(self.valor) + ' - ' + self.comentario


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
