from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^enviar-oferta$', views.company_offer_form, name='formulario'),
    url(r'^oferta/$', views.offer, name='oferta'),
    url(r'^lista-de-ofertas/$', views.offer_list, name='listado_ofertas'),
    url(r'^$', views.home, name='home'),
    url(r'^login_upasaporte$', views.login_upasaporte, name='login_upasaporte'),
    url(r'^suscripciones$', views.suscription, name='suscription'),
    url(r'^solicitar-acceso$', views.registro, name='registro'),
    url(r'^ingreso-a-empresas$', views.registro_empresa, name='login_empresas'),
    url(r'^empresa/(?P<nombre_empresa>([a-zA-Z0-9]+\-)*[a-zA-Z0-9]+)$', views.empresa, name='registro'),
    #!Esta ruta deberia ser la misma que 'formulario' pero con método POST !
    url(r'^enviar_oferta', views.enviar_oferta, name='enviar_oferta'),
]
