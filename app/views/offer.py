import json
import re
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.db.models import Q, Case, When, BooleanField

from app.forms import OfferForm
from app.models import Oferta, Empresa, Usuario, Encargado, Etiqueta, Validacion, ValoracionOferta, TipoEtiqueta, Region, Comuna, Jornada
from app.views.common import getUser
from django.core.mail import EmailMessage


class OfertaCreate(CreateView):
    model = Oferta
    form_class = OfferForm
    template_name = 'app/enviar_oferta_alt.html'

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        # Empresa -------------------------------------------------
        if (form.cleaned_data['nombre_empresa'] != ''):
            nueva_empresa, creada = Empresa.objects.get_or_create(nombre=form.cleaned_data['nombre_empresa'])
            form.instance.empresa = nueva_empresa

        # Sueldo Base  --------------------------------------------
        if (form.cleaned_data['remunerado'] == 'Por Determinar' or form.cleaned_data['remunerado'] == 'Sin Remunaración'):
            form.instance.sueldo_minimo = 0

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

        # Información extra formulario
        json_file = open('./static/tooltips.json')
        json_data = json_file.read()
        context['info'] = json.loads(json_data)
        json_file.close()
        context['empresas'] = Empresa.objects.all().order_by('nombre')
        context['jornadas'] = Jornada.objects.all().order_by('nombre')
        context['remuneraciones'] = Oferta.OPCIONES_REMUNERACION
        context['tipos'] = Oferta.OPCIONES_TIPO

        etiquetas = Etiqueta.objects.filter(validado=True).order_by('nombre')
        tipos_etiquetas = TipoEtiqueta.objects.exclude(nombre='tipo de oferta').exclude(nombre='jornada')
        #tipos_etiquetas = TipoEtiqueta.objects.all()
        dict_etiquetas = {}
        for tipo in tipos_etiquetas:
            dict_etiquetas[tipo.nombre] = etiquetas.filter(tipo_id=tipo.id).order_by('nombre')
        context['etiquetas'] = dict_etiquetas

        regiones = Region.objects.all().order_by('id')
        comunas = Comuna.objects.all().order_by('nombre')
        dict_comunas = {}
        for region in regiones:
            dict_comunas[region.nombre] = comunas.filter(region_id=region.id)
        context['comunas'] = dict_comunas
        context['regiones'] = regiones
        return context

@login_required
def evaluate_practice(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
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

        # Enviar Emails
        if offer.notificar:
            if accept:
                email = EmailMessage(
                            '[Bolsa de Trabajo DCC] Tu Oferta ha sido publicada!',
                            'Tu oferta "{}" ha sido aceptada como práctica por nuestro staff, y ya está disponible para los usuarios del sistema.'.format(offer.titulo),
                            to=['{}'.format(offer.email_encargado)])
            else:
                email = EmailMessage(
                            '[Bolsa de Trabajo DCC] Tu Oferta ha sido rechazada.',
                            'Tu oferta "{}" no ha sido aceptada como práctica por nuestro staff.\n Consulta las Preguntas Frecuentes para ver qué es una práctica válida.'.format(offer.titulo),
                            to=['{}'.format(offer.email_encargado)])
            email.send()

        return HttpResponse(json.dumps({'msg': 'Validada como: ' + valid}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required
def evaluate_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        if 'publicador' not in map(lambda rol: str(rol), user.roles.all()):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        offer_id = request.POST.get('offer_id')
        accept = request.POST.get('accept')
        offer = Oferta.objects.get(pk=offer_id)

        if accept == 'aceptada':  # la oferta fue aceptada
            offer.publicada = True
            offer.fecha_publicacion = datetime.now()
            tipo = offer.tipo.lower()
            if tipo != 'práctica':
                offer.etiquetas.add(Etiqueta.objects.filter(nombre=tipo).last())
            offer.save()
            if offer.notificar and tipo != 'práctica':
                email = EmailMessage(
                            '[Bolsa de Trabajo DCC] Tu Oferta ha sido publicada!',
                            'Tu oferta "{}" ha sido aceptada por nuestro staff, y ya está disponible para los usuarios del sistema.'.format(offer.titulo),
                            to=['{}'.format(offer.email_encargado)])
                email.send()
            return HttpResponse(json.dumps({'msg': 'Oferta agregada del sistema'}), content_type='application/json')
        else:
            # hacer cosas de rechazo de oferta como mandar correo y cosas
            # offer.delete() #dejar comentado para no borrar ofertas accidentalmente
            if offer.notificar:
                email = EmailMessage(
                            '[Bolsa de Trabajo DCC] Tu Oferta ha sido rechazada.',
                            'Tu oferta "{}" ha sido rechazada por nuestro staff.\n Consulta las Preguntas Frecuentes para conocer los motivos de rechazo de ofertas.'.format(offer.titulo),
                            to=['{}'.format(offer.email_encargado)])
                email.send()
            return HttpResponse(json.dumps({'msg': 'Oferta eliminada del sistema'}),
                                content_type='application/json')
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
    if user.isUsuario():
        context['isFollowed'] = user.marcadores.all().filter(id=offer_id).last() is not None
        context['user_already_comment'] = len(
            ValoracionOferta.objects.filter(oferta=context['oferta'], usuario=request.user.usuario)) > 0
        context['comments'] = ValoracionOferta.objects.filter(oferta=context['oferta']).order_by('fecha_creacion')
        context['roles'] = list(map(lambda x: str(x), Usuario.objects.get(pk=request.user.id).roles.all()))
    return render(request, 'app/offer.html', context)

def classify_offers(offers_to_filter):
    publicadas = offers_to_filter.filter(publicada=True)

    deadline = timezone.now() - timedelta(days=7)
    q_aprobadas = Q(validacion__isnull=False) & Q(validacion__aceptado=True)
    q_sin_validar = Q(validacion__isnull=True) & Q(fecha_publicacion__lte=deadline)
    return {
        'practices': publicadas.filter(q_sin_validar | q_aprobadas, tipo='Práctica')
                               .annotate(aprobada=Case(When(q_aprobadas, then=True),
                                                       When(q_sin_validar, then=False),
                                                       default=False,
                                                       output_field=BooleanField())),
        'practices_to_check': publicadas.filter(tipo='Práctica', validacion__isnull=True),
        'reports': publicadas.filter(tipo='Memoria'),
        'jobs': publicadas.filter(tipo='Trabajo'),
        'offers_to_check': offers_to_filter.filter(publicada=False).order_by('-fecha_publicacion')
    }

def get_tags():
    tipos_etiqueta_query = TipoEtiqueta.objects.all().order_by('nombre')
    tipos_etiqueta = []

    for tipo_etiqueta in tipos_etiqueta_query:
        tipos_etiqueta.append({
            'tipo': tipo_etiqueta,
            'etiquetas': Etiqueta.objects.filter(tipo=tipo_etiqueta).order_by('nombre')
        })

    return tipos_etiqueta

@login_required
def offer_list(request):
    user = getUser(request.user)
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    #obtener ofertas
    context = classify_offers(Oferta.objects.all().order_by('fecha_publicacion'))

    #datos de usuario
    context['user'] = user
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    context['ids_marcadores'] = list(map(lambda offer: offer.id, user.marcadores.all()))

    #cargar etiquetas para filtrar
    context['tipos_etiquetas'] = get_tags()

    return render(request, 'app/offer_list.html', context)


# Busqueda -----------------------------------------------------------------------------

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.

        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

@login_required
def search_offer(request):
    busqueda = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        busqueda = request.GET['q']

    # No hacer búsquedas muy cortas
    if (len(busqueda) < 3):
        return offer_list(request)

    user = getUser(request.user)
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    context = {'user': user}
    roles = map(lambda rol: str(rol), user.roles.all())
    context['roles'] = list(roles)

    # Generar Q's
    query = get_query(busqueda, ['titulo', 'empresa__nombre'])
    # query = Q(titulo__icontains=busqueda) | Q(empresa__nombre__icontains=busqueda)

    results = Oferta.objects.filter(query).order_by('fecha_publicacion')

    # publicadas = results.filter(publicada=True)
    # deadline = timezone.now() - timedelta(days=7)
    # q_aprobadas = Q(validacion__isnull=False) & Q(validacion__aceptado=True)
    # q_sin_validar = Q(validacion__isnull=True) & Q(fecha_publicacion__lte=deadline)
    # context['practices'] = publicadas.filter(q_sin_validar | q_aprobadas, tipo='Práctica')
    # context['practices_to_check'] = publicadas.filter(tipo='Práctica', validacion__isnull=True)
    # context['reports'] = publicadas.filter(tipo='Memoria')
    # context['jobs'] = publicadas.filter(tipo='Trabajo')
    # context['offers_to_check'] = results.filter(publicada=False).order_by('-fecha_publicacion')
    context.update(classify_offers(results))

    context['query'] = busqueda
    context['busqueda'] = True

    return render(request, 'app/offer_list.html', context)

# --------------------------------------------------------------------------------------

@csrf_exempt
def suscription(request):
    context = {}
    return render(request, 'app/suscription.html', context)

@login_required
def followOffer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos para hacer esta accion')
        offer_id = request.POST.get('offer_id')
        actual_state = request.POST.get('actual_state')
        offer = Oferta.objects.get(pk=offer_id)

        if actual_state == 'True':
            user.marcadores.remove(offer)
        else:
            user.marcadores.add(offer)
        user.save()
        return HttpResponse(json.dumps({'msg': 'Cambiado el estado de seguimiento de la oferta'}),
                                content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

def markers(request):
    user = getUser(request.user)
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    # obtener ofertas
    context = classify_offers(user.marcadores.all())

    # datos de usuario
    context['user'] = user
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    context['ids_marcadores'] = list(map(lambda offer: offer.id, user.marcadores.all()))

    # cargar etiquetas para filtrar
    context['tipos_etiquetas'] = get_tags()
    context['marcadores'] = True
    return render(request, 'app/offer_list.html', context)
