from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app.forms import CompanyForm
from app.models import Empresa, Encargado
from app.views.common import home, getUser


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
