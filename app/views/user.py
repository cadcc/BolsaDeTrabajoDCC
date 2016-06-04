from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from app.forms import UserForm
from app.models import Usuario, Rol
from app.views.common import getUser, home


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
        elif False: #por aca hay que ver el tema con u-pasaporte
            print('Aún no tenemos U-Pasaporte')
        else:   #No hay registros de existencia del usuario
            context['error_login'] = 'Nombre de usuario o contraseña no válido!'
            return render(request, 'app/home.html', context)
        return redirect(reverse(home))
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