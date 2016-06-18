import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect

from app.forms import AddPublicadorForm, AddAdministradorForm, AddValidadorForm, AddModeradorForm
from app.models import Usuario, Rol
from app.views.common import getUser

@login_required
def manage_permissions(request):
    user = getUser(request.user)
    context = {'user': user}
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    if 'administrador' not in context['roles']:
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    if request.method == 'POST':
        if 'add_pub' in request.POST:
            form = AddPublicadorForm(request.POST)
            if form.is_valid():
                usuario = Usuario.objects.get(pk=form.cleaned_data['publicador'])
                rol = Rol.objects.get(nombre='publicador')
                usuario.roles.add(rol)
        elif 'add_val' in request.POST:
            form = AddValidadorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=form.cleaned_data['validador']).roles.add(Rol.objects.get(nombre='validador'))
        elif 'add_mod' in request.POST:
            form = AddModeradorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=form.cleaned_data['moderador']).roles.add(Rol.objects.get(nombre='moderador'))
        elif 'add_admin' in request.POST:
            form = AddAdministradorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=form.cleaned_data['administrador']).roles.add(Rol.objects.get(nombre='administrador'))

    usuarios = Usuario.objects.filter(roles__nombre__in=['normal']).order_by('last_name')
    context['publicadores'] = usuarios.filter(roles__nombre__in=['publicador'])
    context['not_publicadores'] = usuarios.exclude(roles__nombre__in=['publicador'])
    context['validadores'] = usuarios.filter(roles__nombre__in=['validador'])
    context['not_validadores'] = usuarios.exclude(roles__nombre__in=['validador'])
    context['administradores'] = usuarios.filter(roles__nombre__in=['administrador'])
    context['not_administradores'] = usuarios.exclude(roles__nombre__in=['administrador'])
    context['moderadores'] = usuarios.filter(roles__nombre__in=['moderador'])
    context['not_moderadores'] = usuarios.exclude(roles__nombre__in=['moderador'])

    context['pub_form'] = AddPublicadorForm()
    context['val_form'] = AddValidadorForm()
    context['mod_form'] = AddModeradorForm()
    context['admin_form'] = AddAdministradorForm()
    return render(request, 'app/permisos.html', context)

@login_required
def add_role(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        print("--> Revisando formularios")
        if 'add_pub' in request.POST:
            print("---> Agregar Publicador")
            form = AddPublicadorForm(request.POST)
            print("---> isBound: " + str(form.is_bound))
            print("---> errors: " + str(form.errors))
            print("---> valor publicador: " + str(request.POST.get('publicador')))
            if form.is_valid():
                print("----> Publicador valido")
                usuario = Usuario.objects.get(pk=form.cleaned_data['publicador'])
                rol = Rol.objects.get(nombre='publicador')
                usuario.roles.add(rol)
                usuario.save()
        elif 'add_val' in request.POST:
            form = AddValidadorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=request.POST['validador']).roles.add(Rol.objects.get(nombre='validador'))
        elif 'add_mod' in request.POST:
            form = AddModeradorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=request.POST['moderador']).roles.add(Rol.objects.get(nombre='moderador'))
        elif 'add_admin' in request.POST:
            form = AddAdministradorForm(request.POST)
            if form.is_valid():
                Usuario.objects.get(pk=request.POST['administrador']).roles.add(Rol.objects.get(nombre='administrador'))
    return redirect(reverse(manage_permissions))

@login_required
def remove_role(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        user_id = request.POST.get('user_id')
        rol_name = request.POST.get('rol')

        if user_id == user.id and rol_name == 'administrador':
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        usuario = Usuario.objects.get(pk=user_id)
        rol = Rol.objects.get(nombre=rol_name)
        usuario.roles.remove(rol)
        message = 'El usuario ' + usuario.first_name + ' ' + usuario.last_name + ' ha perdido el rol ' + rol_name + '.'
        return HttpResponse(json.dumps({'msg': message}),
                            content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')
