import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.datetime_safe import datetime

from app.forms import CommentForm
from app.models import ValoracionOferta, Usuario, Oferta, Empresa, ValoracionEmpresa, AdvertenciaValoracionOferta, \
    AdvertenciaValoracionEmpresa
from app.views.common import getUser
from app.views.company import load_info_company, empresa
from app.views.offer import load_info_offer, offer

def new_score(valorations):
    sum = 0
    for val in valorations:
        sum += val
    return sum/len(valorations)

def new_score_offer(offer):
    valorations = list(map(lambda o: o.valor, ValoracionOferta.objects.filter(oferta=offer)))
    return new_score(valorations)

def new_score_company(company):
    valorations = list(map(lambda o: o.valor, ValoracionEmpresa.objects.filter(empresa=company)))
    return new_score(valorations)

@login_required(login_url='home')
def comment_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        offer_id = request.POST.get('offer_id')
        form = CommentForm(request.POST)
        if form.is_valid():
            #obtener datos del formulario
            comment = form.cleaned_data['comment']
            is_important = form.cleaned_data['is_important']
            valoration = form.cleaned_data['valoration']

            #crear valoracion
            actual_offer = Oferta.objects.get(pk=offer_id)
            valoration_offer = ValoracionOferta(
                usuario=user,
                oferta=actual_offer,
                valor=valoration,
                comentario=comment,
                prioritario=is_important
            )
            valoration_offer.save()

            #actualizar puntaje de la oferta
            score = new_score_offer(actual_offer)
            actual_offer.puntuacion = score
            actual_offer.save()
            return redirect(reverse(offer, args=[offer_id]))
        context = load_info_offer(offer_id)
        context['form'] = form
        return render(request, 'app/offer.html', context)
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def edit_comment_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        comment_id = request.POST.get('comment_id')
        actual_valoration = ValoracionOferta.objects.get(pk=comment_id)

        #comprobar que sea el dueño del comentario el que lo edita
        if user.id == actual_valoration.usuario_id:
            actual_offer = Oferta.objects.get(pk=actual_valoration.oferta_id)
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.cleaned_data['comment']
                is_important = form.cleaned_data['is_important']
                valoration = form.cleaned_data['valoration']

                #actualizar informacion del comentario
                actual_valoration.comentario = comment
                actual_valoration.prioritario = is_important
                actual_valoration.valor = valoration
                actual_valoration.fecha_modificacion = timezone.now()
                actual_valoration.save()

                #actualizar puntaje de la oferta
                score = new_score_offer(actual_offer)
                actual_offer.puntuacion = score
                actual_offer.save()
                return redirect(reverse(offer, args=[actual_offer.id]))
            context = load_info_offer(actual_offer.id)
            context['form'] = form
            return render(request, 'app/offer.html', context)
        else:
            return HttpResponseBadRequest('No tienes permisos para editar este comentario')
    else:
        return HttpResponseNotAllowed('POST')

def comment_company(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        company_id = request.POST.get('company_id')
        form = CommentForm(request.POST)
        actual_company = Empresa.objects.get(pk=company_id)
        if form.is_valid():
            # obtener datos del formulario
            comment = form.cleaned_data['comment']
            is_important = form.cleaned_data['is_important']
            valoration = form.cleaned_data['valoration']

            # crear valoracion
            valoration_company = ValoracionEmpresa(
                usuario=user,
                empresa=actual_company,
                valor=valoration,
                comentario=comment,
                prioritario=is_important
            )
            valoration_company.save()

            # actualizar puntaje de la oferta
            score = new_score_company(actual_company)
            actual_company.puntaje = score
            actual_company.save()
            return redirect(reverse(empresa, args=[actual_company.url_encoded_name()]))
        context = load_info_company(user, actual_company)
        context['form'] = form
        return render(request, 'app/company.html', context)
    else:
        return HttpResponseNotAllowed('POST')

def edit_comment_company(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        comment_id = request.POST.get('comment_id')
        actual_valoration = ValoracionEmpresa.objects.get(pk=comment_id)
        actual_company = Empresa.objects.get(pk=actual_valoration.empresa_id)

        #comprobar que sea el dueño del comentario el que lo edita
        if user.id == actual_valoration.usuario_id:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.cleaned_data['comment']
                is_important = form.cleaned_data['is_important']
                valoration = form.cleaned_data['valoration']

                #actualizar informacion del comentario
                actual_valoration.comentario = comment
                actual_valoration.prioritario = is_important
                actual_valoration.valor = valoration
                actual_valoration.fecha_modificacion = timezone.now()
                actual_valoration.save()

                #actualizar puntaje de la oferta
                score = new_score_company(actual_company)
                actual_company.puntaje = score
                actual_company.save()
                return redirect(reverse(empresa, args=[actual_company.url_encoded_name()]))
            context = load_info_company(user, actual_company)
            context['form'] = form
            return render(request, 'app/company.html', context)
        else:
            return HttpResponseBadRequest('No tienes permisos para editar este comentario')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def reportComment(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes permisos!!!')
        comment_id = request.POST.get('comment_id')
        type = request.POST.get('type')
        if type == 'offer':
            actual_comment = ValoracionOferta.objects.get(pk=int(comment_id))
            already_comment = actual_comment.reportes.filter(id=user.id)
        else:
            actual_comment = ValoracionEmpresa.objects.get(pk=int(comment_id))
            already_comment = actual_comment.reportes.filter(id=user.id)
        if len(already_comment) > 0:
            return HttpResponse(json.dumps({'msg': 'ya reportado'}),
                                content_type='application/json')
        else:
            actual_comment.reportes.add(user)
            actual_comment.save()
        return HttpResponse(json.dumps({'msg': 'ok'}),
                            content_type='application/json')
    return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def moderateComments(request):
    if request.method == 'GET':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        roles = list(map(lambda rol: str(rol), user.roles.all()))
        if 'moderador' not in roles:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        # obtencion de comnetarios reportados
        offers_report_comments = list(filter(lambda comment: len(comment.reportes.all()) > settings.MAX_REPORTS_NUMBER and ((not comment.hasWarning()) or (comment.hasWarning() and comment.wasEdited())), ValoracionOferta.objects.all()))
        company_report_comments = list(filter(lambda comment: len(comment.reportes.all()) > settings.MAX_REPORTS_NUMBER and ((not comment.hasWarning()) or (comment.hasWarning() and comment.wasEdited())), ValoracionEmpresa.objects.all()))

        context = {
            'user': user,
            'roles': roles,
            'report_comments': offers_report_comments + company_report_comments
        }
        return render(request, 'app/moderar_comentarios.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@login_required(login_url='home')
def resolveReport(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        roles = list(map(lambda rol: str(rol), user.roles.all()))
        if 'moderador' not in roles:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        # recuperar datos
        id_comment = int(request.POST.get('id_comment'))
        type_comment = request.POST.get('type')

        if type_comment == 'offer':
            try:
                comment = ValoracionOferta.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador eliminó este reporte',
                    'show': 'true'
                }), content_type='application/json')
        elif type_comment == 'company':
            try:
                comment = ValoracionEmpresa.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador eliminó este reporte',
                    'show': 'true'
                }), content_type='application/json')
        else:
            return HttpResponseBadRequest(json.dumps({
                'msg': 'Error al obtener el tipo de comentario'
            }), content_type='application/json')
        # eliminar reportes
        comment.reportes.clear()
        comment.save()

        # actualizar advertencia
        warning = comment.getLastWarning()
        if warning:
            warning.resuelto = True
            warning.save()
        return HttpResponse(json.dumps({'msg': 'Reporte resuelto correctamente'}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def deleteComment(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        roles = list(map(lambda rol: str(rol), user.roles.all()))
        if 'moderador' not in roles:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        # recuperar datos
        id_comment = int(request.POST.get('id_comment'))
        type_comment = request.POST.get('type')
        if type_comment == 'offer':
            try:
                comment = ValoracionOferta.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya eliminó este comentario',
                    'show': 'true'
                }), content_type='application/json')
        elif type_comment == 'company':
            try:
                comment = ValoracionEmpresa.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya eliminó este comentario',
                    'show': 'true'
                }), content_type='application/json')
        else:
            return HttpResponseBadRequest(json.dumps({
                'msg': 'Error al obtener el tipo de comentario'
            }), content_type='application/json')

        # eliminar comentario
        comment.delete()
        return HttpResponse(json.dumps({'msg': 'Comentario eliminado correctamente'}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def sendWarning(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        roles = list(map(lambda rol: str(rol), user.roles.all()))
        if 'moderador' not in roles:
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        # recuperar datos
        id_comment = int(request.POST.get('id_comment'))
        type_comment = request.POST.get('type')
        warning = request.POST.get('warning')

        if type_comment == 'offer':
            try:
                comment = ValoracionOferta.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya eliminó este comentario',
                    'show': 'true'
                }), content_type='application/json')
            if comment.hasWarning():
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya mandó una advertencia de este reporte',
                    'show': 'true'
                }), content_type='application/json')
            comment_warning = AdvertenciaValoracionOferta(
                valoracion=comment,
                advertencia=warning
            )
        elif type_comment == 'company':
            try:
                comment = ValoracionEmpresa.objects.get(pk=id_comment)
            except:
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya eliminó este comentario',
                    'show': 'true'
                }), content_type='application/json')
            if comment.hasWarning():
                return HttpResponseBadRequest(json.dumps({
                    'msg': 'Otro moderador ya mandó una advertencia de este reporte',
                    'show': 'true'
                }), content_type='application/json')
            comment_warning = AdvertenciaValoracionEmpresa(
                valoracion=comment,
                advertencia=warning
            )
        else:
            return HttpResponseBadRequest(json.dumps({
                'msg': 'Error al obtener el tipo de comentario'
            }), content_type = "application/json")
        # guardar advertencia
        comment_warning.save()
        return HttpResponse(json.dumps({'msg': 'Advertencia realizada corectamente'}), content_type='application/json')
    else:
        return HttpResponseNotAllowed('POST')

@login_required(login_url='home')
def myWarnings(request):
    if request.method == 'GET':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        roles = list(map(lambda rol: str(rol), user.roles.all()))

        context = {
            'user': user,
            'roles': roles
        }
        return render(request, 'app/mis_advertencias.html', context)
    else:
        return HttpResponseNotAllowed('GET')

@login_required(login_url='home')
def editCommentForWarning(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not user.isUsuario():
            return HttpResponseBadRequest('No tienes permisos!!!')
        comment_id = request.POST.get('comment_id')
        type = request.POST.get('type')
        edit_text = request.POST.get('edit_text')

        if type == 'offer':
            actual_comment = ValoracionOferta.objects.get(pk=int(comment_id))
        else:
            actual_comment = ValoracionEmpresa.objects.get(pk=int(comment_id))

        # actualizar advertencia
        actual_warning = actual_comment.getLastWarning()
        actual_warning.modificado = True

        # actualizar comentario
        actual_comment.comentario = edit_text
        actual_comment.fecha_modificacion = datetime.now()

        # guardar cambios
        actual_comment.save()
        actual_warning.save()

        return HttpResponse(json.dumps({'msg': 'Edición de comentario realizada'}),
                            content_type='application/json')
    return HttpResponseNotAllowed('POST')