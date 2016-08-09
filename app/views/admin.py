import json
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.conf import settings

from app.forms import AddPublicadorForm, AddAdministradorForm, AddValidadorForm, AddModeradorForm
from app.models import Usuario, Rol, Encargado
from app.views.common import getUser

from sendfile import sendfile

@login_required(login_url='home')
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
                usuario = Usuario.objects.get(pk=form.cleaned_data['validador'])
                rol = Rol.objects.get(nombre='validador')
                usuario.roles.add(rol)
        elif 'add_mod' in request.POST:
            form = AddModeradorForm(request.POST)
            if form.is_valid():
                usuario = Usuario.objects.get(pk=form.cleaned_data['moderador'])
                rol = Rol.objects.get(nombre='moderador')
                usuario.roles.add(rol)
        elif 'add_admin' in request.POST:
            form = AddAdministradorForm(request.POST)
            if form.is_valid():
                usuario = Usuario.objects.get(pk=form.cleaned_data['administrador'])
                rol = Rol.objects.get(nombre='administrador')
                usuario.roles.add(rol)

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

@login_required(login_url='home')
def add_role(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        if 'add_pub' in request.POST:
            form = AddPublicadorForm(request.POST)
            if form.is_valid():
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

@login_required(login_url='home')
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

# Aceptar/Rechazar Usuarios Pendientes -------------------------------------------------------------

@login_required(login_url='home')
def review_users(request):
    user = getUser(request.user)
    context = {'user': user}
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    if 'administrador' not in context['roles']:
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    # GET: Lista de usuarios por aprobar
    context['usuarios_pendientes'] = Usuario.objects.filter(roles__nombre__in=['pendiente']).order_by('last_name')
    return render(request, 'app/aprobar_usuarios.html', context)

@login_required(login_url='home')
def accept_user(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        user_id = request.POST.get('user_id')
        usuario = Usuario.objects.get(pk=user_id)

        pendiente = Rol.objects.get(nombre='pendiente')
        normal = Rol.objects.get(nombre='normal')
        usuario.roles.remove(pendiente)
        usuario.roles.add(normal)
        message = 'El usuario ' + usuario.first_name + ' ' + usuario.last_name + ' ha sido aceptado.'
        return HttpResponse(json.dumps({'msg': message}),
                            content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def reject_user(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        user_id = request.POST.get('user_id')
        usuario = Usuario.objects.get(pk=user_id)
        # usuario.delete()
        message = 'El usuario ' + usuario.first_name + ' ' + usuario.last_name + ' ha sido rechazado.'
        return HttpResponse(json.dumps({'msg': message}),
                            content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def download_file(request, user_id):
    if request.method == 'GET':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        # Do stuff
        usuario_pendiente = Usuario.objects.get(pk=user_id)
        filename = usuario_pendiente.documento

        '''
        fsock = open(settings.MEDIA_ROOT + filename.name, 'r')
        response = HttpResponse(fsock, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s_%s.pdf"' % \
                                          (usuario_pendiente.first_name, usuario_pendiente.last_name)

        print("Generando Response")
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}_{}.pdf"'.format(usuario_pendiente.first_name, usuario_pendiente.last_name)
        #response['X-Sendfile'] = smart_str('/protected/%s' % filename)   # Apache
        response['X-Accel-Redirect'] = smart_str('/protected/{}'.format(filename))    # Nginx

        print("Filename: {}".format(filename))
        print("Content-Disposition: {}".format(response['Content-Disposition']))
        print("X-Accel-Redirect: {}".format(response['X-Accel-Redirect']))

        return response
        '''

        #att_name = "{}_{}.pdf".format(usuario_pendiente.first_name, usuario_pendiente.last_name)
        return sendfile(request, filename)
    else:
        return HttpResponseNotAllowed('GET')


# Aceptar/Rechazar Empresas ------------------------------------------------------------------------

@login_required(login_url='home')
def review_companies(request):
    user = getUser(request.user)
    context = {'user': user}
    if not user.isUsuario():
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
    context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
    if 'administrador' not in context['roles']:
        return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

    # GET: Lista de empresas por aprobar
    encargados = Encargado.objects.all()
    context['empresas_pendientes'] = encargados.filter(empresa__validada=False)
    return render(request, 'app/aprobar_empresas.html', context)

@login_required(login_url='home')
def accept_company(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        enc_id = request.POST.get('enc_id')
        encargado = Encargado.objects.get(pk=enc_id)
        empresa = encargado.empresa
        empresa.validada = True
        encargado.administrador = True
        encargado.save()
        empresa.save()

        message = 'La solicitud de Validación de la empresa empresa \"' + empresa.nombre + '\" ha sido aceptada.'
        return HttpResponse(json.dumps({'msg': message}),
                            content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def reject_company(request):
    if request.method == 'POST':
        user = getUser(request.user)
        context = {'user': user}
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        context['roles'] = list(map(lambda rol: str(rol), user.roles.all()))
        if 'administrador' not in context['roles']:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        enc_id = request.POST.get('enc_id')
        encargado = Encargado.objects.get(pk=enc_id)
        message = 'La solicitud de Validación de la empresa empresa \"' + encargado.empresa.nombre + '\" ha sido rechazada.'
        # encargado.delete()
        return HttpResponse(json.dumps({'msg': message}),
                            content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')
