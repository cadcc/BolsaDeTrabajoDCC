from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.forms import OfferForm

@csrf_exempt
def home(request):
    return render(request, 'app/home.html')

@csrf_exempt
def company_offer_form(request):
    return render(request, 'app/form.html')

@csrf_exempt
def offer(request):
    return render(request, 'app/offer.html')

@csrf_exempt
def offer_list(request):
    return render(request, 'app/offer_list.html')

@csrf_exempt
def login_upasaporte(request):
    return render(request, 'app/offer_list.html')

@csrf_exempt
def suscription(request):
    return render(request, 'app/suscription.html')

def enviar_oferta(request):
    form = OfferForm(request.POST)
    if (form.is_valid()):

        titulo_oferta = form.cleaned_data['titulo_oferta']
        nombre_empresa = form.cleaned_data['nombre_empresa']
        jornada_trabajo = form.cleaned_data['jornada_trabajo']
        select_tipo_oferta = form.cleaned_data['select_tipo_oferta']
        perfil_objetivo = form.cleaned_data['perfil_objetivo']
        desc_oferta = form.cleaned_data['desc_oferta']
        habilidades_deseadas = form.cleaned_data['habilidades_deseadas']
        habilidades_requeridas = form.cleaned_data['habilidades_requeridas']
        remuneracion = form.cleaned_data['remuneracion']
        sueldo_minimo = form.cleaned_data['sueldo_minimo']
        se_ofrece = form.cleaned_data['se_ofrece']
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
        select_dur_min = form.cleaned_data['select_dur_min']
        comen_dur = form.cleaned_data['comen_dur']
        etiquetas = form.cleaned_data['etiquetas']


        print('titulo_oferta: ' + titulo_oferta)
        print('nombre_empresa: ' + nombre_empresa)
        print('jornada_trabajo: ' + jornada_trabajo)
        print('select_tipo_oferta: ' + select_tipo_oferta)
        print('perfil_objetivo: ' + perfil_objetivo)
        print('desc_oferta: ' + desc_oferta)
        print('habilidades_deseadas: ' + habilidades_deseadas)
        print('habilidades_requeridas: ' + habilidades_requeridas)
        print('remuneracion: ' + remuneracion)
        print('sueldo_minimo: ' + sueldo_minimo)
        print('se_ofrece: ' + se_ofrece)
        print('fecha_inicio: ' + str(fecha_inicio))
        print('fecha_fin: ' + str(fecha_fin))
        print('select_dur_min: ' + select_dur_min)
        print('comen_dur: ' + comen_dur)
        print('etiquetas: ' + etiquetas)

        return render(request, 'app/offer.html')
    return render(request, 'app/home.html')
