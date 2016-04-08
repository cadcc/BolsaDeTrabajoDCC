from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^formulario/$', views.company_offer_form, name='formulario'),
    url(r'^oferta/$', views.offer, name='oferta'),
    url(r'^listado_ofertas/$', views.offer_list, name='listado_ofertas'),
    url(r'^$', views.home, name='home')
]
