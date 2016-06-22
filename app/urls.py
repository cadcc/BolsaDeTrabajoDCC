from django.conf.urls import url

from app.views import common, company, offer, user, valoration, admin

urlpatterns = [
    url(r'^enviar-oferta$', offer.OfertaCreate.as_view(), name='formulario'),
    url(r'^oferta/(?P<offer_id>(\d{1,}))$', offer.offer, name='oferta'),
    url(r'^lista-de-ofertas/$', offer.offer_list, name='listado_ofertas'),
    url(r'^buscar/$', offer.search_offer, name='busqueda'),
    url(r'^$', common.home, name='home'),
    url(r'^login_user$', user.login_user, name='login_user'),
    url(r'^logout$', common.logout_user, name='logout'),
    url(r'^login_empresa$', company.login_empresa, name='login_empresa'),
    url(r'^suscripciones$', offer.suscription, name='suscription'),
    url(r'^solicitar-acceso$', user.registro, name='registro'),
    url(r'^ingreso-a-empresas$', company.registro_empresa, name='registro_empresas'),
    url(r'^empresa/(?P<nombre_empresa>([a-zA-Z0-9]+\-)*[a-zA-Z0-9]+)$', company.empresa, name='empresa'),
    # Esta ruta deberia ser la misma que 'formulario' pero con método POST
    url(r'^enviar_oferta$', offer.OfertaCreate.as_view(), name='enviar_oferta'),
    url(r'^registrar-usuario$', view=user.registrar_usuario, name='registrar_usuario'),
    url(r'^registrar-empresa$', view=company.registrar_empresa, name='registrar_empresa'),
    url(r'^usuario-pendiente$', view=user.wait_for_check_user, name='usuario_pendiente'),
    url(r'^empresa-pendiente$', view=company.wait_for_check_company, name='empresa_pendiente'),
    url(r'^descripcion-empresa$', view=company.change_description, name='descripcion_empresa'),
    url(r'^encargados$', view=company.encargados, name='encargados'),
    url(r'^evaluar-oferta$', view=offer.evaluate_offer, name='evaluar_oferta'),
    url(r'^evaluar-practica$', view=offer.evaluate_practice, name='evaluar_practica'),
    url(r'^comentar-oferta$', view=valoration.comment_offer, name="comentar_oferta"),
    url(r'^comentar-empresa$', view=valoration.comment_company, name="comentar_empresa"),
    url(r'^editar-comentario-oferta$', view=valoration.edit_comment_offer, name="editar_comentario_oferta"),
    url(r'^editar-comentario-empresa$', view=valoration.edit_comment_company, name="editar_comentario_empresa"),
    url(r'^seguir-oferta$', view=offer.followOffer, name="seguir_oferta"),
    url(r'^mis-marcadores$', view=offer.markers, name="mis_marcadores"),
    url(r'^reportar-comentario$', view=valoration.reportComment, name="reportar_comentario"),
    url(r'^permisos$', view=admin.manage_permissions, name="permisos"),
    url(r'^permisos/remove$', view=admin.remove_role, name="quitar_permisos"),
    url(r'^filtrar/$', view=offer.filter, name='filtros'),
    url(r'^moderar-comentarios/$', view=valoration.moderateComments, name='moderar-cometarios'),
    url(r'^resolver-reporte$', view=valoration.resolveReport, name='resolver-reporte'),
    url(r'^eliminar-comentario$', view=valoration.deleteComment, name='eliminar-comentario'),
    url(r'^enviar-advertencia$', view=valoration.sendWarning, name='enviar-advertencia'),
    url(r'^mis-advertencias/$', view=valoration.myWarnings, name='mis_advertencias')
]
