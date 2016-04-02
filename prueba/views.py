from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def prueba_1(request):
    context = {'hola': 'texto para la primera vista'}
    return render(request, 'prueba/vista_1.html', context)

@csrf_exempt
def prueba_2(request):
    context = {'hola': 'texto para la segunda vista'}
    return render(request, 'prueba/vista_2.html', context)