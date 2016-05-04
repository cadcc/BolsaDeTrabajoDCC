from django import forms

from app.models import Usuario


class Login_upasaporteForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class OfferForm(forms.Form):
    jornadas = [('full-time', 'full-time'),
                ('part-time', 'part-time')]
    opciones_rem = [('mensual', 'mensual'),
                    ('sin determinar', 'sin determinar'),
                    ('Sin remuneracion', 'sin remuneracion'),
                    ('otro', 'otro')]
    choices_select_tipo = [('practica', 'practica'),
                           ('memoria', 'memoria'),
                           ('trabajo', 'trabajo')]
    choices_select_dur = [('1', '1'), ('2', '2'), ('3', '3')]

    titulo_oferta = forms.CharField()
    nombre_empresa = forms.CharField()
    jornada_trabajo = forms.ChoiceField(choices=jornadas)
    select_tipo_oferta = forms.ChoiceField(choices=choices_select_tipo)
    perfil_objetivo = forms.CharField()
    desc_oferta = forms.CharField()
    habilidades_deseadas = forms.CharField()
    habilidades_requeridas = forms.CharField()
    remuneracion = forms.ChoiceField(choices=opciones_rem)
    sueldo_minimo = forms.CharField()
    se_ofrece = forms.CharField()
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()
    select_dur_min = forms.ChoiceField(choices=choices_select_dur)
    comen_dur = forms.CharField()
    etiquetas = forms.CharField()

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