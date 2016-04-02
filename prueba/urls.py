from django.conf.urls import url
from prueba import views

urlpatterns = [
    url(r'^vista_1/$', views.prueba_1, name='prueba_1'),
    url(r'^vista_2/$', views.prueba_2, name='prueba_2')
]