from itertools import chain

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Case, BooleanField
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app.forms import CompanyForm, CompanyDescriptionForm, EncargadoForm, NuevoEncargadoForm, ProfileImageForm
from app.models import Empresa, Encargado, ValoracionEmpresa, Usuario, Oferta, AdvertenciaValoracionEmpresa
from app.views.common import home, getUser
import json

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

@csrf_exempt
def crear_encargado(request):
    if (request.method == 'POST'):
        user = getUser(request.user)
        if not user.isEncargado or not user.administrador:
            return redirect(reverse(home))
        form = NuevoEncargadoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            telefono = form.cleaned_data['telefono']
            password = form.cleaned_data['password']
            Encargado.objects.create_user(first_name=nombre, email=email,
                                                                    password=password,
                                                                    empresa=user.empresa, username=email, administrador=False, telefono=telefono)
        empresa = user.empresa
        encargados = empresa.encargado_set.all()
        context = {
            'empresa': empresa,
            'encargado': user,
            'user': user,
            'encargados': encargados,
            'form': form
        }
        return render(request, 'app/encargados_empresa.html', context)
    else:
        return redirect(reverse(home))
@csrf_exempt
def modificar_encargado(request):
    if(request.method == 'POST'):
        user = getUser(request.user)
        user_id = 0
        if 'user_id' not in request.POST:
            return redirect(reverse(home))
        user_id = request.POST.get('user_id')
        if not user.isEncargado:
            return redirect(reverse(home))
        if not user.administrador and user_id != user.pk:
            return redirect(reverse(home))
        encargado_to_update = Encargado.objects.get(pk=user_id)
        if encargado_to_update is None:
            return redirect(reverse(home))
        if encargado_to_update.empresa != user.empresa:
            return redirect(reverse(home))
        form = EncargadoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            telefono = form.cleaned_data['telefono']

            encargado_to_update.first_name = nombre
            encargado_to_update.telefono = telefono
            encargado_to_update.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'failed', 'message': 'Teléfono o nombre no válido'})
    else:
        return redirect(reverse(home))

@csrf_exempt
def eliminar_encargado(request):
    if (request.method == 'POST'):
        user = getUser(request.user)
        if 'user_id' not in request.POST:
            return redirect(reverse(home))
        user_id = request.POST.get('user_id')
        if not user.isEncargado or not user.administrador:
            return redirect(reverse(home))
        encargado_to_delete = Encargado.objects.get(pk=user_id)
        if encargado_to_delete is None:
            return redirect(reverse(home))
        if encargado_to_delete.empresa != user.empresa:
            return redirect(reverse(home))
        if encargado_to_delete.administrador:
            return JsonResponse({'status': 'fail', 'message': 'El encargado administrador no puede ser eliminado.'})
        encargado_to_delete.delete()
        return JsonResponse({'status': 'ok'})
    else:
        return redirect(reverse(home))

def load_info_company(user, empresa):
    context = {}
    if empresa is None:
        return redirect(reverse(home))
    context['empresa'] = empresa
    context['encargado'] = Encargado.objects.filter(empresa=empresa, administrador=True).first()
    context['user'] = user
    context['roles'] = []

    if user.isUsuario():
        all_comments_report = ValoracionEmpresa.objects.filter(empresa=empresa, reportes=user).annotate(
            reportado=Case(default=True, output_field=BooleanField()))
        all_comments_no_report = ValoracionEmpresa.objects.filter(empresa=empresa).exclude(reportes=user).annotate(
            reportado=Case(default=False, output_field=BooleanField()))
        all_comments = sorted(chain(all_comments_report, all_comments_no_report),
                              key=lambda valoration: valoration.fecha_creacion)

        comments_without_warning = []
        for comment in all_comments:
            warnings = AdvertenciaValoracionEmpresa.objects.filter(valoracion=comment, resuelto=False)
            if len(warnings) == 0:
                comments_without_warning.append(comment)

        context['comments'] = comments_without_warning

    context['company_offers'] = Oferta.objects.filter(empresa=empresa, publicada=True).order_by('titulo')
    if user.isUsuario():
        context['roles'] = list(map(lambda x: str(x), Usuario.objects.get(pk=context['user'].id).roles.all()))
        context['user_already_comment'] = len(
            ValoracionEmpresa.objects.filter(empresa=empresa, usuario=user)) > 0
    return context

@login_required(login_url='home')
def empresa(request, id_empresa):
    empresa = Empresa.objects.filter(pk=id_empresa).first()
    if empresa is None:
        return redirect(reverse(home))
    user = getUser(request.user)
    if isinstance(user, Encargado) and user.empresa != empresa:
        return redirect(reverse(home))
    context = load_info_company(user, empresa)
    return render(request, 'app/company.html', context)

@login_required(login_url='home')
def mi_empresa(request):
    user = getUser(request.user)
    if user.isUsuario():
        return redirect(reverse(home))
    empresa = user.empresa
    context = load_info_company(user, empresa)
    return render(request, 'app/company.html', context)

@csrf_exempt
def login_empresa(request):
    if request.method == 'POST':
        context = {}
        email = request.POST.get('email')
        password = request.POST.get('password')
        baseUser = authenticate(username=email, password=password)
        if baseUser is not None and getUser(baseUser).isEncargado():    #verificar en nuestra base de datos
            #verificar si el usuario esta pendiente
            if baseUser.encargado.empresa.validada == False:
                return redirect(reverse(wait_for_check_company))
            #baseUser.usuario.backend = 'django.contrib.auth.backend    s.ModelBackend'
            login(request, baseUser)
        else:   #No hay registros de existencia del usuario
            context['error_login'] = 'Combinación de usuario y contraseña inválida'
            return render(request, 'app/registro_empresa.html', context)
        #return redirect('/empresa/' + str(baseUser.encargado.empresa.id))
        return redirect(reverse('mi_empresa'))
    return HttpResponseNotAllowed('POST')

@csrf_exempt
def wait_for_check_company(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'app/empresa_pendiente.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@login_required(login_url='home')
def change_description(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isEncargado() or not user.empresa.validada or not user.administrador:
            return HttpResponseBadRequest('No tienes permisos.')

        form = CompanyDescriptionForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            user.empresa.descripcion = description
            user.empresa.save()
        return redirect(reverse(empresa, args=[user.empresa.url_encoded_name()]))
    else:
        return redirect(reverse(home))

@login_required(login_url='home')
def change_picture(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isEncargado() or not user.empresa.validada or not user.administrador:
            return HttpResponseBadRequest('No tienes permisos.')

        form = ProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            user.empresa.logo = image
            user.empresa.save()
            return JsonResponse({'status': 'ok', 'url': user.empresa.logo.url})
        return JsonResponse({'status': 'failed', 'message': 'La imagen debe tener proporción 1:1 y ser de un tamaño menor a 1MB.'})
    else:
        return redirect(reverse(home))

@login_required(login_url='home')
def encargados(request):
    if request.method == 'GET':
        user = getUser(request.user)
        if not user.isEncargado() or not user.empresa.validada or not user.administrador:
            return redirect(reverse(home))

        empresa = user.empresa
        encargados = empresa.encargado_set.all()
        context = {
            'empresa' : empresa,
            'encargado' : user,
            'user' : user,
            'encargados' : encargados,
        }
        return render(request, 'app/encargados_empresa.html', context)
    else:
        context = {}
        return render(request, 'app/encargados_empresa.html', context)
