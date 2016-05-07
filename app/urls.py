from django.conf.urls import url
from app import views
from app.views import OfertaCreate

urlpatterns = [
    url(r'^enviar-oferta$', OfertaCreate.as_view(), name='formulario'),
    url(r'^oferta/(?P<offer_id>(\d{1,}))$', views.offer, name='oferta'),
    url(r'^lista-de-ofertas/$', views.offer_list, name='listado_ofertas'),
    url(r'^$', views.home, name='home'),
    url(r'^login_user$', views.login_user, name='login_user'),
    url(r'^logout$', views.logout_user, name='logout'),
    url(r'^login_empresa$', views.login_empresa, name='login_empresa'),
    url(r'^suscripciones$', views.suscription, name='suscription'),
    url(r'^solicitar-acceso$', views.registro, name='registro'),
    url(r'^ingreso-a-empresas$', views.registro_empresa, name='registro_empresas'),
    url(r'^empresa/(?P<nombre_empresa>([a-zA-Z0-9]+\-)*[a-zA-Z0-9]+)$', views.empresa, name='registro'),
    #!Esta ruta deberia ser la misma que 'formulario' pero con método POST !
    url(r'^enviar_oferta$', OfertaCreate.as_view(), name='enviar_oferta'),
    url(r'^registrar-usuario$', view=views.registrar_usuario, name='registrar_usuario'),
    url(r'^registrar-empresa$', view=views.registrar_empresa, name='registrar_empresa'),
    url(r'^usuario-pendiente$', view=views.wait_for_check_user, name='usuario_pendiente'),
    url(r'^empresa-pendiente$', view=views.wait_for_check_company, name='empresa_pendiente'),
    url(r'^evaluar-oferta$', view=views.evaluate_offer, name='evaluar_oferta'),
    url(r'^evaluar-practica$', view=views.evaluate_practice, name='evaluar_practica'),
    url(r'^comentar-oferta$', view=views.comment_offer, name="comentar_oferta")
]
