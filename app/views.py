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

from app.models import Usuario, Rol, Oferta, Empresa, Validacion, Etiqueta, ValoracionOferta, Encargado, TipoEtiqueta
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

    def get_context_data(self, **kwargs):
        context = super(OfertaCreate, self).get_context_data(**kwargs)
        user_request = self.request.user
        if user_request.is_authenticated():
            usuario = Usuario.objects.filter(pk=user_request).first()
            encargado = Encargado.objects.filter(pk=user_request).first()
            if usuario is not None and usuario.roles is not None:
                context['roles'] = list(map(lambda r: str(r), usuario.roles.all()))
                context['user'] = usuario
            elif encargado is not None:
                context['user'] = encargado
        return context

#------------------------------------------------------------
def getUser(user):
    try:
        usuario = user.usuario
        return usuario
    except Usuario.DoesNotExist:
        return user.encargado

@csrf_exempt
def home(request):
    user_request = request.user
    context = {'user': user_request}
    if user_request.is_authenticated():
        user = getUser(user_request)
        if isinstance(user, Usuario):
            return redirect(reverse(offer_list))
        elif isinstance(user, Encargado):
            return redirect(reverse(empresa, args=[user.empresa.url_encoded_name()]))
    return render(request, 'app/home.html', context)

@login_required
def evaluate_practice(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
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
def evaluate_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        if 'publicador' not in map(lambda rol: str(rol), user.roles.all()):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        offer_id = request.POST.get('offer_id')
        accept = request.POST.get('accept')
        offer = Oferta.objects.get(pk=offer_id)

        if accept == 'aceptada':  #la oferta fue aceptada
            offer.publicada = True
            offer.fecha_publicacion = datetime.now()
            tipo = offer.tipo.lower()
            if tipo != 'práctica':
                offer.etiquetas.add(Etiqueta.objects.filter(nombre=tipo).last())
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
    user = getUser(request.user)
    context = load_info_offer(offer_id)
    if isinstance(user, Usuario):
        context['user_already_comment'] = len(
            ValoracionOferta.objects.filter(oferta=context['oferta'], usuario=request.user.usuario)) > 0
        context['comments'] = ValoracionOferta.objects.filter(oferta=context['oferta']).order_by('fecha_creacion')
        context['roles'] = list(map(lambda x: str(x), Usuario.objects.get(pk=request.user.id).roles.all()))
    return render(request, 'app/offer.html', context)

@login_required
def offer_list(request):
    user = getUser(request.user)
    if not isinstance(user, Usuario):
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    #obtener fecha para comparar
    date_now = timezone.now()
    date_seven_days = date_now - timedelta(days=7)

    #obtener ofertas
    context = {'user': user}
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

    #cargar etiquetas para filtrar
    tipos_etiqueta_query = TipoEtiqueta.objects.all().order_by('nombre')
    tipos_etiqueta = []

    for tipo_etiqueta_query in tipos_etiqueta_query:
        tipos_etiqueta.append({
            'tipo': tipo_etiqueta_query,
            'etiquetas': Etiqueta.objects.filter(tipo=tipo_etiqueta_query).order_by('nombre')
        })

    context['tipos_etiquetas'] = tipos_etiqueta

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
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        offer_id = request.POST.get('offer_id')
        form = CommentOfferForm(request.POST)
        if form.is_valid():
            #obtener datos del formulario
            comment = form.cleaned_data['comment']
            is_important = form.cleaned_data['is_important']
            valoration = form.cleaned_data['valoration']

            #crear valoracion
            actual_offer = Oferta.objects.get(pk=offer_id)
            valoration_offer = ValoracionOferta(
                usuario=user,
                oferta=actual_offer,
                valor=valoration,
                comentario=comment,
                prioritario=is_important
            )
            valoration_offer.save()

            #actualizar puntaje de la oferta
            score = new_score_offer(actual_offer)
            actual_offer.puntuacion = score
            actual_offer.save()
            return redirect(reverse(offer, args=[offer_id]))
        context = load_info_offer(offer_id)
        context['form'] = form
        return render(request, 'app/offer.html', context)
    else:
        return HttpResponseNotAllowed('POST')

@login_required
def edit_comment_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        comment_id = request.POST.get('comment_id')
        actual_valoration = ValoracionOferta.objects.get(pk=comment_id)

        #comprobar que sea el dueño del comentario el que lo edita
        if user.id == actual_valoration.usuario_id:
            actual_offer = Oferta.objects.get(pk=actual_valoration.oferta_id)
            form = CommentOfferForm(request.POST)
            if form.is_valid():
                comment = form.cleaned_data['comment']
                is_important = form.cleaned_data['is_important']
                valoration = form.cleaned_data['valoration']

                #actualizar informacion del comentario
                actual_valoration.comentario = comment
                actual_valoration.prioritario = is_important
                actual_valoration.valor = valoration
                actual_valoration.fecha_modificacion = timezone.now()
                actual_valoration.save()

                #actualizar puntaje de la oferta
                score = new_score_offer(actual_offer)
                actual_offer.puntuacion = score
                actual_offer.save()
                return redirect(reverse(offer, args=[actual_offer.id]))
            context = load_info_offer(actual_offer.id)
            context['form'] = form
            return render(request, 'app/offer.html', context)
        else:
            return HttpResponseBadRequest('No tienes permisos para editar este comentario')
    else:
        return HttpResponseNotAllowed('POST')

def login_user(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me', False)
        baseUser = authenticate(username=username, password=password)
        if baseUser is not None and isinstance(getUser(baseUser), Usuario):    #verificar en nuestra base de datos
            #verificar si el usuario esta pendiente
            if 'pendiente' in map(lambda rol: str(rol), baseUser.usuario.roles.all()):
                return redirect(reverse(wait_for_check_user))
            baseUser.usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            #setear tiempo de sesion
            time_session = settings.SESSION_TIME_REMEMBER_ME if remember_me else settings.SESSION_TIME_NORMAL
            request.session.set_expiry(time_session)
            #loguear
            login(request, baseUser)
        elif False: #por aca hay que ver el tema con u-pasaporte
            print('Aún no tenemos U-Pasaporte')
        else:   #No hay registros de existencia del usuario
            context['error_login'] = 'Nombre de usuario o contraseña no válido!'
            return render(request, 'app/home.html', context)
        return redirect(reverse(home))
    return HttpResponseNotAllowed('POST')

@login_required
@csrf_exempt
def logout_user(request):
    logout(request)
    return redirect(reverse(home))

@csrf_exempt
def suscription(request):
    context = {}
    return render(request, 'app/suscription.html', context)

@csrf_exempt
def registro(request):
    context = {}
    return render(request, 'app/registro.html', context)

@csrf_exempt
def registrar_usuario(request):
    if (request.method == 'POST'):
        context = {}
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
            return render(request, 'app/registro.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def wait_for_check_user(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'app/usuario_pendiente.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def registro_empresa(request):
    context = {}
    return render(request, 'app/registro_empresa.html', context)

@csrf_exempt
def registrar_empresa(request):
    if (request.method == 'POST'):
        context = {}
        form = CompanyForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            attendant_name = form.cleaned_data['attendant_name']
            email = form.cleaned_data['attendant_email']
            password = form.cleaned_data['attendant_password']

            empresa = Empresa.objects.create(nombre=company_name)
            encargado = Encargado.objects.create_user(first_name=attendant_name, email=email, password=password,
                                                 empresa=empresa, username=email, administrador=True)
            return redirect(reverse(wait_for_check_company))
        else:
            context['form'] = form
            return render(request, 'app/registro_empresa.html', context)
    else:
        return HttpResponseNotAllowed('POST')

@login_required
def empresa(request, nombre_empresa):
    context = {}
    nombre_empresa = nombre_empresa.replace('-', ' ')
    empresa = Empresa.objects.filter(nombre=nombre_empresa).first()
    if empresa is None:
        return redirect(reverse(home))
    context['empresa'] = empresa
    context['user'] = getUser(request.user)
    return render(request, 'app/company.html', context)

@csrf_exempt
def login_empresa(request):
    if request.method == 'POST':
        context = {}
        email = request.POST.get('email')
        password = request.POST.get('password')
        baseUser = authenticate(username=email, password=password)
        if baseUser is not None and isinstance(getUser(baseUser), Encargado):    #verificar en nuestra base de datos
            #verificar si el usuario esta pendiente
            if baseUser.encargado.empresa.validada == False:
                return redirect(reverse(wait_for_check_company))
            #baseUser.usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, baseUser)
        else:   #No hay registros de existencia del usuario
            context['error_login'] = 'Combinación de usuario y contraseña inválida'
            return render(request, 'app/registro_empresa.html', context)
        return redirect('/empresa/' + baseUser.encargado.empresa.url_encoded_name())
    return HttpResponseNotAllowed('POST')

@csrf_exempt
def wait_for_check_company(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'app/empresa_pendiente.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def edit_comment(request):
    if request.method == 'POST':
        context = {}
        comment = request.POST.get('comment')
        offer_id = request.POST.get('offer_id')
        oferta = Oferta.objects.filter(pk=offer_id).first()
        if oferta is None:
            return redirect('/oferta/'+offer_id)
        valoracion = ValoracionOferta.objects.filter(oferta=oferta, usuario=request.user.usuario).first()
        if valoracion is None:
            return redirect('/oferta/' + offer_id)

        valoracion.comentario = comment
        valoracion.save()
        return redirect('/oferta/' + offer_id)
    return HttpResponseNotAllowed('POST')
