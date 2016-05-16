from django.conf.urls import url

from app.views import common, company, offer, user, valoration

urlpatterns = [
    url(r'^enviar-oferta$', offer.OfertaCreate.as_view(), name='formulario'),
    url(r'^oferta/(?P<offer_id>(\d{1,}))$', offer.offer, name='oferta'),
    url(r'^lista-de-ofertas/$', offer.offer_list, name='listado_ofertas'),
    url(r'^$', common.home, name='home'),
    url(r'^login_user$', user.login_user, name='login_user'),
    url(r'^logout$', common.logout_user, name='logout'),
    url(r'^login_empresa$', company.login_empresa, name='login_empresa'),
    url(r'^suscripciones$', offer.suscription, name='suscription'),
    url(r'^solicitar-acceso$', user.registro, name='registro'),
    url(r'^ingreso-a-empresas$', company.registro_empresa, name='registro_empresas'),
    url(r'^empresa/(?P<nombre_empresa>([a-zA-Z0-9]+\-)*[a-zA-Z0-9]+)$', company.empresa, name='empresa'),
    #!Esta ruta deberia ser la misma que 'formulario' pero con método POST !
    url(r'^enviar_oferta$', offer.OfertaCreate.as_view(), name='enviar_oferta'),
    url(r'^registrar-usuario$', view=user.registrar_usuario, name='registrar_usuario'),
    url(r'^registrar-empresa$', view=company.registrar_empresa, name='registrar_empresa'),
    url(r'^usuario-pendiente$', view=user.wait_for_check_user, name='usuario_pendiente'),
    url(r'^empresa-pendiente$', view=company.wait_for_check_company, name='empresa_pendiente'),
    url(r'^evaluar-oferta$', view=offer.evaluate_offer, name='evaluar_oferta'),
    url(r'^evaluar-practica$', view=offer.evaluate_practice, name='evaluar_practica'),
    url(r'^comentar-oferta$', view=valoration.comment_offer, name="comentar_oferta"),
    url(r'^editar-comentario-oferta', view=valoration.edit_comment_offer, name="editar_comentario_oferta")
]
