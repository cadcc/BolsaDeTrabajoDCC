from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone

from app.forms import CommentOfferForm
from app.models import ValoracionOferta, Usuario, Oferta
from app.views import offer
from app.views.common import getUser
from app.views.offer import load_info_offer


def new_score_offer(offer):
    valorations = list(map(lambda o: o.valor, ValoracionOferta.objects.filter(oferta=offer)))
    sum = 0
    for val in valorations:
        sum += val
    return sum/len(valorations)

@login_required
def comment_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')

        offer_id = request.POST.get('offer_id')
        form = CommentOfferForm(request.POST)
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

@login_required
def edit_comment_offer(request):
    if request.method == 'POST':
        user = getUser(request.user)
        if not isinstance(user, Usuario):
            return HttpResponseBadRequest('No tienes los permisos necesarios para esta acción!!!')
        comment_id = request.POST.get('comment_id')
        actual_valoration = ValoracionOferta.objects.get(pk=comment_id)

        #comprobar que sea el dueño del comentario el que lo edita
        if user.id == actual_valoration.usuario_id:
            actual_offer = Oferta.objects.get(pk=actual_valoration.oferta_id)
            form = CommentOfferForm(request.POST)
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
