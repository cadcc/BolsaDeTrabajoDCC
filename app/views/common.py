from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app.models import Usuario, Encargado


def getUser(user):
    try:
        usuario = user.usuario
        return usuario
    except Usuario.DoesNotExist:
        return user.encargado

@csrf_exempt
def home(request):
# <<<<<<< HEAD
#     if(request.method == 'POST'):
#         if not request.form['ticket']: return -1
#         params = { 'servicio': servicio, 'ticket': request.form['ticket'] }
#         data = urllib2.urlopen( url_upasaporte + '/?' + urllib.urlencode( params ) ).read()
#         if not data: return -1

#         data = json.loads( data )
#         print(data)
#         #Aqui se puede jugar con los datos :) guardarlos en db,
#         #chequear si la persona realmente tiene acceso, etc.
# #        redirect = 'http://EL_SITIO_DONDE_REDIRIGIR_AL_USUARIO.com'

#         #Tambien se puede inicializar la sesion con datos 
#         #(solo si manejas la sesion del lado del servidor)
#         #session.new = True
#         #session['nombre'] = data['alias']
#         #redirect += '/auth/'+session.sid
# #        return redirect
#     else:
#         user_request = request.user
#         context = {'user': user_request}
#         if user_request.is_authenticated():
#             user = getUser(user_request)
#             if isinstance(user, Usuario):
#                 return redirect(reverse('listado_ofertas'))
#             elif isinstance(user, Encargado):
    #            return redirect(reverse('empresa', args=[user.empresa.url_encoded_name()]))
    #    return render(request, 'app/home.html', context)
    user_request = request.user
    context = {'user': user_request}
    if user_request.is_authenticated():
        user = getUser(user_request)
        if user.isUsuario():
            return redirect(reverse('listado_ofertas'))
        elif user.isEncargado():
            return redirect(reverse('empresa', args=[user.empresa.url_encoded_name()]))
    return render(request, 'app/home.html', context)

@login_required
@csrf_exempt
def logout_user(request):
    logout(request)
    return redirect(reverse(home))
