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
    user_request = request.user
    context = {'user': user_request}
    if user_request.is_authenticated():
        user = getUser(user_request)
        if isinstance(user, Usuario):
            return redirect(reverse('listado_ofertas'))
        elif isinstance(user, Encargado):
            return redirect(reverse('empresa', args=[user.empresa.url_encoded_name()]))
    return render(request, 'app/home.html', context)

@login_required
@csrf_exempt
def logout_user(request):
    logout(request)
    return redirect(reverse(home))
