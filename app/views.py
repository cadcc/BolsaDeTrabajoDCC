from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseNotAllowed

from app.models import Usuario, Rol, Oferta, Empresa
from app.forms import OfferForm, UserForm, CompanyForm


#------------------------------------------------------------

from django.views.generic.edit import CreateView

#@csrf_exempt
class OfertaCreate(CreateView):
    model = Oferta
    form_class = OfferForm
    template_name = 'app/enviar_oferta.html'
    success_url = 'home'

    #def form_valid(self, form):
    #    if (form.instance.nombre_empresa != ''):
    #        nueva_empresa = Empresa.create(form.instance.nombre_empresa)
    #        nueva_empresa.save()
    #        form.instance.empresa = nueva_empresa.pk


#@csrf_exempt
class RolCreate(CreateView):
    model = Rol
    fields = ('nombre',)
    template_name = 'app/enviar_oferta.html'

    def get_success_url(self):
        return reverse('home')

#------------------------------------------------------------


@csrf_exempt
def home(request):
    context = {
        'main_url': settings.MAIN_URL
    }
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

@csrf_exempt
def offer(request):
    context = {
        'main_url': settings.MAIN_URL
    }
    return render(request, 'app/offer.html', context)

@csrf_exempt
@login_required
def offer_list(request):
    user = request.user
    context = {}
    context['main_url'] = settings.MAIN_URL
    context['user'] = user
    roles = map(lambda rol: str(rol), user.roles.all())
    context['roles'] = roles
    if 'pendiente' in roles:
        return redirect(reverse(wait_for_check_user))
    return render(request, 'app/offer_list.html', context)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        context = {
            'main_url': settings.MAIN_URL
        }
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:    #verificar en nuestra base de datos
            login(request, user)
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

            return render(request, 'app/usuario_pendiente.html', context)
        else:
            context['form'] = form
            print('algo fallo :c')
            return render(request, 'app/registro.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@csrf_exempt
def wait_for_check_user(request):
    if (request.method == 'GET'):
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
        return HttpResponseNotAllowed('GET')
    return

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
    return HttpResponseNotAllowed('GET')

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
