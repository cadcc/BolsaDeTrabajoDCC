import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from app.forms import OfferForm
from app.models import Oferta, Empresa, Usuario, Encargado, Etiqueta, Validacion, ValoracionOferta, TipoEtiqueta, Region, Comuna
from app.views.common import getUser


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
        context['regiones'] = Region.objects.all()
        context['comunas'] = Comuna.objects.all().order_by('nombre')
        context['empresas'] = Empresa.objects.all().order_by('nombre')
        return context

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

        if accept == 'aceptada':  # la oferta fue aceptada
            offer.publicada = True
            offer.fecha_publicacion = datetime.now()
            tipo = offer.tipo.lower()
            if tipo != 'práctica':
                offer.etiquetas.add(Etiqueta.objects.filter(nombre=tipo).last())
            offer.save()
            return HttpResponse(json.dumps({'msg': 'Oferta agregada del sistema'}), content_type='application/json')
        else:
            # hacer cosas de rechazo de oferta como mandar correo y cosas
            # offer.delete() #dejar comentado para no borrar ofertas accidentalmente
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

@csrf_exempt
def suscription(request):
    context = {}
    return render(request, 'app/suscription.html', context)
