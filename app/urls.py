from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^company_offer_form/$', views.company_offer_form, name='company_offer_form'),
    url(r'^offer/$', views.offer, name='offer'),
    url(r'^offer_list/$', views.offer_list, name='offer_list')
]