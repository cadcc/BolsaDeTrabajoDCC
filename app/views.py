from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    return render(request, 'app/home.html')

@csrf_exempt
def company_offer_form(request):
    return render(request, 'app/form.html')

@csrf_exempt
def offer(request):
    return render(request, 'app/offer.html')

@csrf_exempt
def offer_list(request):
    return render(request, 'app/offer_list.html')

@csrf_exempt
def login_upasaporte(request):
    return render(request, 'app/offer_list.html')

@csrf_exempt
def suscription(request):
    return render(request, 'app/suscription.html')