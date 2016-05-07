from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from app.models import Oferta, Rol

from app.models import Usuario
from app.models import Empresa


class Login_upasaporteForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class CompanyForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()
    repassword = forms.CharField()


    def clean_email(self):
        email = self.cleaned_data['email']
        if Empresa.objects.filter(email=email):
            raise forms.ValidationError('El correo electrónico ingresado ya se '
                                        'encuentra registrado en el sistema.')
        return email

    def clean_repassword(self):
        password = self.cleaned_data['password']
        repassword = self.cleaned_data['repassword']
        if password != repassword:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return repassword

class UserForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    document = forms.FileField()
    password = forms.CharField()
    repassword = forms.CharField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email):
            raise forms.ValidationError('El correo electrónico ingresado ya se '
                                        'encuentra registrado en el sistema.')
        return email

    def clean_repassword(self):
        password = self.cleaned_data['password']
        repassword = self.cleaned_data['repassword']
        if password != repassword:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return repassword

class CommentOfferForm(forms.Form):
    valoration = forms.IntegerField()
    is_important = forms.BooleanField(required=False)
    comment = forms.CharField(required=False)

    def clean_valoration(self):
        valoration = self.cleaned_data['valoration']
        if  not 0 < valoration <= 5:
            raise forms.ValidationError('Las puntuaciones van entre 1 y 5 estrellas.')
        return valoration * 20

class MyDateInput(forms.DateInput):
    input_type = 'date'

class MyTimeInput(forms.TimeInput):
    input_type = 'time'

class OfferForm(ModelForm):
    nombre_empresa = forms.CharField(max_length=64, required=False)

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
            'comuna',
            #'etiquetas',
            'nombre_encargado',
            'email_encargado',
            'telefono_encargado',
            'notificar',
        )
        labels = {
            'titulo': 'Título de la Oferta',
        }
        help_texts = {
            'titulo': 'Tooltip Titulo'
        }
        widgets = {
            'hora_ingreso': forms.TimeInput(format='%H:%M'),
            'hora_salida': MyTimeInput(),
            'fecha_comienzo': forms.SelectDateWidget,
            'fecha_termino': MyDateInput(),
            'etiquetas': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        self.fields['empresa'].required = False

    def clean(self):
        data = super(OfferForm, self).clean()
        empresa = data.get("empresa")
        nueva_empresa = data.get("nombre_empresa")
        if empresa == None and nueva_empresa == '':
            raise forms.ValidationError('Debe elegir una Empresa del listado o agregar una Nueva Empresa')
