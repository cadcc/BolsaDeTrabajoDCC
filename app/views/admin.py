from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app.models import Usuario, Rol
from app.views.common import getUser

@login_required
def manage_permissions(request):
    user = getUser(request.user)
    context = {'user': user }
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    if 'administrador' not in context['roles']:
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
    context['administradores'] = Rol.objects.get(pk=1).usuario_set.all()
    context['publicadores'] = Rol.objects.get(pk=2).usuario_set.all()
    context['validadores'] = Rol.objects.get(pk=3).usuario_set.all()
    context['moderadores'] = Rol.objects.get(pk=4).usuario_set.all()
    context['usuarios'] = Usuario.objects.all()

    return render(request, 'app/permisos.html', context)
