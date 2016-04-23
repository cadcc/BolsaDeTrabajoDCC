from django import forms

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

