from django.conf import settings
from django.contrib.auth import authenticate, login
from app.backends import U_PasaporteBackend
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.forms import UserForm
from app.models import Usuario, Rol
from app.views.common import getUser, home
import requests
from urllib.parse import urlparse, parse_qs, urlsplit
import sys
from bs4 import BeautifulSoup



def login_user(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me', False)
        baseUser = authenticate(username=username, password=password)
        if baseUser is not None and getUser(baseUser).isUsuario():    #verificar en nuestra base de datos
            #verificar si el usuario esta pendiente
            if 'pendiente' in map(lambda rol: str(rol), baseUser.usuario.roles.all()):
                return redirect(reverse(wait_for_check_user))
            baseUser.usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            #setear tiempo de sesion
            time_session = settings.SESSION_TIME_REMEMBER_ME if remember_me else settings.SESSION_TIME_NORMAL
            request.session.set_expiry(time_session)
            #loguear
            login(request, baseUser)
        else: #por aca hay que ver el tema con u-pasaporte
            post_data= {'username':username, 'password':password, 'servicio': 'bolsa_cadcc', 'debug':1}
            try:
                response = requests.post("https://www.u-cursos.cl/upasaporte/adi", data=post_data)
            except requests.exceptions.RequestException:
                context['error_login'] = 'Error de conexión con servidor U-Pasaporte'
                return render(request, 'app/home.html', context)
            soup = BeautifulSoup(response.text,'html.parser')
            try:
                parsing = (urlparse(settings.MAIN_URL+"?"+response.text[response.text.index('alias'):]))
            except ValueError:
                if response.status_code == 200 and soup.find(id="merror") is not None:
                    #No hay registros de existencia del usuario
                    context['error_login'] = ''+soup.find(id="merror").li.text
                    return render(request, 'app/home.html', context)
                else: 
                    context['error_login'] = 'Error interno del servidor U-Pasaporte'
                    return render(request, 'app/home.html', context)
            parsed = parse_qs(parsing.query)
            base = parsed['base'][0]
            rut = parsed['rut'][0]
            email = parsed['email'][0]
            first_name = parsed['nombre1'][0]
            last_name = parsed['apellido1'][0]
            hash_photo = urlparse(parsed['img'][0]).path.split("/")[2]
            datos_extra = { 'first_name': first_name, 'last_name': last_name, 'documento': None,}
            username = "UPass"+rut+"Base"+base
            try:
                usuario = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                usuario = Usuario.objects.create_user(username=username, email=email,**datos_extra)
                rol = Rol.objects.get(nombre='normal')
                usuario.roles.add(rol)
                usuario.set_unusable_password()
                usuario.save()
            baseUser = U_PasaporteBackend.authenticate(U_PasaporteBackend,username=username)
            if baseUser is not None and getUser(baseUser).isUsuario():
                baseUser.usuario.backend = 'app.backends.U_PasaporteBackend'
                time_session = settings.SESSION_TIME_REMEMBER_ME if remember_me else settings.SESSION_TIME_NORMAL
                request.session.set_expiry(time_session)
                #loguear
                login(request, baseUser.usuario)
            else: 
                context['error_login'] = 'Nombre de usuario o contraseña no válido!'
                return render(request, 'app/home.html', context)
        #Esta redirección es cuando todo sale bien
        return redirect(reverse(home))
    #Esta redirección es cuando no manda método POST
    return HttpResponseNotAllowed('POST')

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