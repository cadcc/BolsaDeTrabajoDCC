import re
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from app.models import Oferta, Rol, Jornada, Encargado, Comuna
from app.models import Usuario
from app.models import Empresa


class Login_upasaporteForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class CompanyForm(forms.Form):
    company_name = forms.CharField()
    attendant_name = forms.CharField()
    attendant_email = forms.EmailField()
    attendant_password = forms.CharField()
    attendant_repassword = forms.CharField()


    def clean_attendant_email(self):
        attendant_email = self.cleaned_data['attendant_email']
        if Usuario.objects.filter(email=attendant_email) or Encargado.objects.filter(email=attendant_email):
            raise forms.ValidationError('El correo electrónico ingresado ya se '
                                        'encuentra registrado en el sistema.')
        return attendant_email

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        if not re.match(r'^([A-Za-z0-9]+\s)*[A-Za-z0-9]+$', company_name):
            raise forms.ValidationError("El nombre de la empresa debe ser alfa-numérico")
        if Empresa.objects.filter(nombre=company_name):
            raise forms.ValidationError('La empresa \''+company_name+'\' ya se encuentra registrada.')
        return company_name

    def clean_attendant_repassword(self):
        attendant_password = self.cleaned_data['attendant_password']
        attendant_repassword = self.cleaned_data['attendant_repassword']
        if attendant_password != attendant_repassword:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return attendant_repassword

class UserForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    document = forms.FileField()
    password = forms.CharField()
    repassword = forms.CharField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email) or Encargado.objects.filter(email=email):
            raise forms.ValidationError('El correo electrónico ingresado ya se '
                                        'encuentra registrado en el sistema.')
        return email

    def clean_repassword(self):
        password = self.cleaned_data['password']
        repassword = self.cleaned_data['repassword']
        if password != repassword:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return repassword

    def clean_document(self):
        document = self.cleaned_data['document']
        types = document.content_type.split('/')
        max_size = 2**20 * 5 #tamaño maximo de 5 MB
        if 'pdf' not in types:
            raise forms.ValidationError('Solo se permiten documentos PDF')
        if document.size > max_size:
            raise forms.ValidationError('El archivo subido supera los 5MB')
        return document

class CommentForm(forms.Form):
    valoration = forms.IntegerField()
    is_important = forms.BooleanField(required=False)
    comment = forms.CharField(required=False)

    def clean_valoration(self):
        valoration = self.cleaned_data['valoration']
        if  not 0 < valoration <= 5:
            raise forms.ValidationError('Las puntuaciones van entre 1 y 5 estrellas.')
        return valoration * 20

class CompanyDescriptionForm(forms.Form):
    description = forms.CharField(required=True)

class NuevoEncargadoForm(forms.Form):
    nombre = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telefono = forms.CharField(required=True)
    password = forms.CharField(required=True)
    repassword = forms.CharField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email) or Encargado.objects.filter(email=email):
            raise forms.ValidationError('El correo electrónico ingresado ya se '
                                        'encuentra registrado en el sistema.')
        return email

    def clean_repassword(self):
        password = self.cleaned_data['password']
        repassword = self.cleaned_data['repassword']
        if password != repassword:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return repassword

    def clean_telefono(self):
        phone = self.cleaned_data['telefono']
        phone = phone.replace(' ', '')
        if len(phone) < 7 or len(phone) > 20:
            raise forms.ValidationError('El número de teléfono no es correcto')
        if (phone[0] == '+' and not phone[1:].isnumeric()) and not phone.isnumeric():
            raise forms.ValidationError('El número de teléfono no es correcto')
        return phone

class EncargadoForm(forms.Form):
    nombre = forms.CharField(required=True)
    telefono = forms.CharField(required=True)

    def clean_telefono(self):
        phone = self.cleaned_data['telefono']
        phone = phone.replace(' ', '')
        if len(phone) < 7 or len(phone) > 20:
            raise forms.ValidationError('El número de teléfono no es correcto')
        if (phone[0] == '+' and not phone[1:].isnumeric()) and not phone.isnumeric():
            raise forms.ValidationError('El número de teléfono no es correcto')
        return phone

class AddPublicadorForm(forms.Form):
    publicador = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(roles__nombre__in=['normal'])
                                .exclude(roles__nombre__in=['publicador'])
                                .order_by('last_name'),
        required=True)


class AddValidadorForm(forms.Form):
    validador = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(roles__nombre__in=['normal'])
                                .exclude(roles__nombre__in=['validador'])
                                .order_by('last_name'),
        required=True)


class AddModeradorForm(forms.Form):
    moderador = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(roles__nombre__in=['normal'])
                                .exclude(roles__nombre__in=['moderador'])
                                .order_by('last_name'),
        required=True)


class AddAdministradorForm(forms.Form):
    administrador = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(roles__nombre__in=['normal'])
                                .exclude(roles__nombre__in=['administrador'])
                                .order_by('last_name'),
        required=True)


class OfferForm(ModelForm):
    nombre_empresa = forms.CharField(max_length=64, required=False, label="Nombre Empresa")
    tipo = forms.ChoiceField(choices=Oferta.OPCIONES_TIPO, widget=forms.RadioSelect(), label="Tipo de Oferta")
    sueldo_minimo = forms.IntegerField(min_value=0, required=False, label="Sueldo Base")
    duracion_minima = forms.IntegerField(min_value=0, label="Duración Mínima (meses)")
    jornada = forms.ModelChoiceField(queryset=Jornada.objects.all(), widget=forms.RadioSelect(), empty_label=None, label="Tipo de Jornada")
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.exclude(validada=True).order_by('nombre'))
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all().order_by('nombre'))
    fecha_comienzo = forms.DateField(input_formats=('%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y'))
    fecha_termino = forms.DateField(input_formats=('%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y'))
    hora_ingreso = forms.TimeField()
    hora_salida = forms.TimeField()

    class Meta:
        model = Oferta
        fields = (
            'titulo',
            'empresa',
            'nombre_empresa',
            'tipo',
            'descripcion',
            'requiere_experiencia',
            'habilidades_requeridas',
            'habilidades_deseadas',
            'se_ofrece',
            'jornada',
            'comentario_jornada',
            'hora_ingreso',
            'hora_salida',
            'remunerado',
            'sueldo_minimo',
            'comentario_sueldo',
            'fecha_comienzo',
            'fecha_termino',
            'duracion_minima',
            'comentario_duracion',
            'direccion',
            'comuna',
            'etiquetas',
            'nombre_encargado',
            'email_encargado',
            'telefono_encargado',
            'notificar',
        )

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        self.fields['empresa'].required = False
        self.fields['requiere_experiencia'].required = False
        self.fields['comentario_jornada'].required = False
        self.fields['comentario_sueldo'].required = False
        self.fields['comentario_duracion'].required = False

    def clean(self):
        data = super(OfferForm, self).clean()
        empresa = data.get("empresa")
        nueva_empresa = data.get("nombre_empresa")
        if ((empresa == None or empresa == 'Otra') and nueva_empresa == ''):
            raise forms.ValidationError('Debe elegir una Empresa del listado o agregar una Nueva Empresa')
        elif ((empresa == None or empresa == 'Otra') and nueva_empresa != ''):
            nueva_empresa_obj = Empresa.objects.filter(nombre=nueva_empresa).first()
            if (nueva_empresa_obj and nueva_empresa_obj.validada):
                raise forms.ValidationError('La empresa seleccionada es una Empresa Verificada en el sistema. Por favor, inicie sesión como Encargado de dicha empresa para publicar.')

        sueldo = data.get("sueldo_minimo")
        remuneracion = data.get("remunerado")
        if (remuneracion == 'Mensual'):
            if sueldo and sueldo < 0:
                raise forms.ValidationError('El sueldo base mínimo es 0')
            elif not sueldo:
                raise forms.ValidationError('Debe especificar un Sueldo Base al elegir una remuneración Mensual')

        ini = data.get("fecha_comienzo")
        fin = data.get("fecha_termino")
        if ini and fin:
            if (fin < ini):
                raise forms.ValidationError('La fecha de término es menor a la fecha de inicio')

    def clean_duracion_minima(self):
        duracion = self.cleaned_data['duracion_minima']
        if duracion < 0:
            raise forms.ValidationError('La duración no puede ser menor que 0')
        return duracion

    def clean_telefono_encargado(self):
        telefono = self.cleaned_data['telefono_encargado']
        if not re.match(r'^(\+56 ?)?((9|2) [0-9]{4} [0-9]{4}|(9|2) [0-9]{8}|[0-9]{2} [0-9]{3} [0-9]{4}|[0-9]{9})$', telefono):
            raise forms.ValidationError("El teléfono debe tener 9 dígitos ('+56' opcional)")
        return telefono

class ProfileImageForm(forms.Form):
    image = forms.ImageField()

    def clean_image(self):
        from PIL import Image
        from io import BytesIO
        image = self.cleaned_data['image']
        imageo = Image.open(image)
        w, h = imageo.size
        if not w == h:
            raise forms.ValidationError("La imagen no es cuadrada")
        imageo = imageo.resize((100, 100), Image.ANTIALIAS)
        image_file = BytesIO()
        imageo.save(image_file, 'JPEG', quality=90)

        image.file = image_file
        return image
