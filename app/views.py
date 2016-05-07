import json
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest

from app.models import Usuario, Rol, Oferta, Empresa, Validacion, Etiqueta, ValoracionOferta
from app.forms import OfferForm, UserForm, CompanyForm, CommentOfferForm

#------------------------------------------------------------

from django.views.generic.edit import CreateView

#@csrf_exempt
class OfertaCreate(CreateView):
    model = Oferta
    form_class = OfferForm
    template_name = 'app/enviar_oferta.html'

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        if (form.cleaned_data['nombre_empresa'] != ''):
            nueva_empresa, creada = Empresa.objects.get_or_create(nombre=form.cleaned_data['nombre_empresa'])
            form.instance.empresa = nueva_empresa
        return super(OfertaCreate, self).form_valid(form)

#------------------------------------------------------------

@csrf_exempt
def home(request):
    user = request.user
    context = {
        'main_url': settings.MAIN_URL,
        'user': user
    }
    if user.is_authenticated():
        return redirect(reverse(offer_list))
    return render(request, 'app/home.html', context)

@csrf_exempt
def company_offer_form(request):
    context = {
        'main_url': settings.MAIN_URL
    }
    if request.method == 'GET':
        f = OfferForm(request.POST)
        #return render(request, 'app/form.html', context)
    return HttpResponseNotAllowed('GET')

@login_required
@csrf_exempt
def evaluate_practice(request):
    if request.method == 'POST':
        user = request.user.usuario
        if 'validador' not in map(lambda rol: str(rol), user.roles.all()):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        offer_id = request.POST.get('offer_id')
        valid = request.POST.get('valid')
        offer = Oferta.objects.get(pk=offer_id)

        accept = True if valid != 'no valida' else False

        tag_prac_1 = Etiqueta.objects.filter(nombre='práctica 1').last()
        tag_prac_2 = Etiqueta.objects.filter(nombre='práctica 2').last()

        validation = Validacion(aceptado=accept, oferta=offer, usuario=user)

        if valid == 'practica 1':  #la oferta fue aceptada
            offer.etiquetas.add(tag_prac_1)
        elif valid == 'practica 2':
            offer.etiquetas.add(tag_prac_2)
        elif valid == 'practica 1 y 2':
            offer.etiquetas.add(tag_prac_1, tag_prac_2)
        else:
            #hacer cosas de rechazo de oferta como mandar correo y cosas
            #offer.delete() #dejar comentado para no borrar ofertas accidentalmente
            #por el momento se guardara en el sistema como no aprobada
            #return HttpResponse(json.dumps({'msg': 'Práctica eliminada del sistema'}), content_type='application/json')
            pass
        validation.save()
        offer.save()
        return HttpResponse(json.dumps({'msg': 'Validada como: ' + valid}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required
@csrf_exempt
def evaluate_offer(request):
    if request.method == 'POST':
        user = request.user.usuario
        if 'publicador' not in map(lambda rol: str(rol), user.roles.all()):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        offer_id = request.POST.get('offer_id')
        accept = request.POST.get('accept')
        offer = Oferta.objects.get(pk=offer_id)

        if accept == 'aceptada':  #la oferta fue aceptada
            offer.publicada = True
            offer.fecha_publicacion = datetime.now()
            offer.save()
            return HttpResponse(json.dumps({'msg': 'Oferta agregada del sistema'}), content_type='application/json')
        else:
            #hacer cosas de rechazo de oferta como mandar correo y cosas
            #offer.delete() #dejar comentado para no borrar ofertas accidentalmente
            return HttpResponse(json.dumps({'msg': 'Oferta eliminada del sistema'}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

def load_info_offer(offer_id):
    offer = Oferta.objects.get(pk=offer_id)
    valid = Validacion.objects.filter(oferta=offer).last()
    return {
        'oferta': offer,
        'validez': str(valid) if valid is not None else 'Sin Validar'
    }

@login_required
def offer(request, offer_id):
    context = load_info_offer(offer_id)
    context['comments'] = ValoracionOferta.objects.filter(oferta=context['oferta']).order_by('fecha_creacion')
    context['user_already_comment'] = len(ValoracionOferta.objects.filter(oferta=context['oferta'], usuario=request.user.usuario)) > 0
    context['main_url'] = settings.MAIN_URL
    return render(request, 'app/offer.html', context)

@login_required
def offer_list(request):
    user = request.user.usuario

    #obtener fecha para comparar
    date_now = timezone.now()
    date_seven_days = date_now - timedelta(days=7)

    context = {}
    context['main_url'] = settings.MAIN_URL
    context['user'] = user
    roles = map(lambda rol: str(rol), user.roles.all())
    context['roles'] = list(roles)
    valid_practices = []
    wait_practices = []
    pre_practices = Oferta.objects.filter(tipo='Práctica', publicada=True).order_by('-fecha_publicacion')
    for i in range(len(pre_practices)):
        practice = {'info': pre_practices[i]}
        valid = Validacion.objects.filter(oferta=pre_practices[i]).last()
        practice['valid'] = str(valid) if valid is not None else 'Sin Validar'
        if valid is not None or pre_practices[i].fecha_ingreso < date_seven_days:
            valid_practices.append(practice)
        if valid is None:
            wait_practices.append(pre_practices[i])
    context['practices'] = valid_practices
    context['jobs'] = Oferta.objects.filter(tipo='Trabajo', publicada=True).order_by('-fecha_publicacion')
    context['reports'] = Oferta.objects.filter(tipo='Memoria', publicada=True).order_by('-fecha_publicacion')
    context['offers_to_check'] = Oferta.objects.filter(publicada=False).order_by('fecha_ingreso')
    context['practices_to_check'] = reversed(wait_practices)
    return render(request, 'app/offer_list.html', context)

def new_score_offer(offer):
    valorations = list(map(lambda o: o.valor, ValoracionOferta.objects.filter(oferta=offer)))
    sum = 0
    for val in valorations:
        sum += val
    return sum/len(valorations)

@login_required
def comment_offer(request):
    if request.method == 'POST':
        user = request.user.usuario
        offer_id = request.POST.get('offer_id')
        form = CommentOfferForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            is_important = form.cleaned_data['is_important']
            valoration = form.cleaned_data['valoration']
            actual_offer = Oferta.objects.get(pk=offer_id)
            valoration_offer = ValoracionOferta(
                usuario=user,
                oferta=actual_offer,
                valor=valoration,
                comentario=comment,
                prioritario=is_important
            )
            valoration_offer.save()
            score = new_score_offer(actual_offer)
            actual_offer.puntuacion = score
            actual_offer.save()
            return redirect(reverse(offer, args=[offer_id]))
        context = load_info_offer(offer_id)
        context['main_url'] = settings.MAIN_URL
        context['form'] = form
        return render(request, 'app/offer.html', context)
    else:
        return HttpResponseNotAllowed('POST')

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        context = {
            'main_url': settings.MAIN_URL
        }
        username = request.POST.get('username')
        password = request.POST.get('password')
        baseUser = authenticate(username=username, password=password)
        if baseUser is not None and baseUser.usuario is not None:    #verificar en nuestra base de datos
            #verificar si el usuario esta pendiente
            if 'pendiente' in map(lambda rol: str(rol), baseUser.usuario.roles.all()):
                return redirect(reverse(wait_for_check_user))
            baseUser.usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, baseUser)
        elif False: #por aca hay que ver el tema con u-pasaporte
            print('Aún no tenemos U-Pasaporte')
        else:   #No hay registros de existencia del usuario
            context['error_login'] = 'Nombre de usuario o contraseña no válido!'
            return render(request, 'app/home.html', context)
        return redirect(reverse(offer_list))
    return HttpResponseNotAllowed('GET')

@csrf_exempt
def logout_user(request):
    logout(request)
    return redirect(reverse(home))

@csrf_exempt
def suscription(request):
    context = {
        'main_url': settings.MAIN_URL
    }
    return render(request, 'app/suscription.html', context)

@csrf_exempt
def registro(request):
    context = {
        'main_url': settings.MAIN_URL
    }
    return render(request, 'app/registro.html', context)

@csrf_exempt
def registrar_usuario(request):
    if (request.method == 'POST'):
        context = {
            'main_url': settings.MAIN_URL
        }
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            document = form.cleaned_data['document']
            #la comprobacion de existencia del correo se hace en el formulario
            email = form.cleaned_data['email']
            #la comprobacion de contrañas se hace en el formulario
            password = form.cleaned_data['password']
            datos_extra = {
                'first_name': first_name,
                'last_name': last_name,
                'documento': document
            }

            usuario = Usuario.objects.create_user(username=email, email=email, password=password, **datos_extra)
            #agregar rol de pendiente
            rol = Rol.objects.get(nombre='pendiente')
            usuario.roles.add(rol)
            usuario.save()

            return redirect(reverse(wait_for_check_user))
        else:
            context['form'] = form
            print('algo fallo :c')
            return render(request, 'app/registro.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def wait_for_check_user(request):
    if request.method == 'GET':
        context = {
            'main_url': settings.MAIN_URL
        }
        return render(request, 'app/usuario_pendiente.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def registro_empresa(request):
    context = {
        'main_url': settings.MAIN_URL
    }
    return render(request, 'app/registro_empresa.html', context)

@csrf_exempt
def registrar_empresa(request):
    if (request.method == 'POST'):
        context = {
            'main_url': settings.MAIN_URL
        }
        form = CompanyForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            document = form.cleaned_data['document']
            password = form.cleaned_data['password']

            empresa = Empresa.objects.create_user(name=name, email=email, password=password)
            return render(request, 'app/registro_empresa.html', context)
        else:
            context['form'] = form
            print('algo fallo :c')
            return render(request, 'app/registro_empresa.html', context)
    else:
        return HttpResponseNotAllowed('POST')

@csrf_exempt
def empresa(request, nombre_empresa):
    context = {
        'main_url': settings.MAIN_URL
    }
    return render(request, 'app/company.html', context)

@csrf_exempt
def login_empresa(request):
    if request.method == 'POST':
        context = {
            'main_url': settings.MAIN_URL
        }
        email = request.POST.get('login_email')
        password = request.POST.get('login_password')
        company = authenticate(email=email, password=password)
        if company is not None:    #verificar en nuestra base de datos
            login(request, company)
        else:   #No hay registros de existencia de la empresa
            context['error_login'] = 'Nombre de usuario o contraseña no válido!'
            return render(request, 'app/home.html', context)
        return redirect(reverse(home))
    return HttpResponseNotAllowed('POST')

@csrf_exempt
def logout_empresa(request):
    logout(request)
    return redirect(reverse(home))

def enviar_oferta(request):
    context = {
        'main_url': settings.MAIN_URL
    }
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

        return render(request, 'app/offer.html', context)
    return render(request, 'app/home.html', context)
