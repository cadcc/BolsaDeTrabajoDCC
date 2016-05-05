from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from app.models import Oferta

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

class OfferForm(ModelForm):
    class Meta:
        model = Oferta
        fields = (
            'titulo',
            'empresa',
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
            'nombre_encargado',
            'email_encargado',
            'telefono_encargado',
            'etiquetas',
        )
        labels ={
            'titulo': _('Título de la Oferta'),
        }
        help_texts = {
            'titulo': _('Tooltip Titulo')
        }
