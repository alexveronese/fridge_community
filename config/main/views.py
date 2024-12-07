from django.shortcuts import render
from django.views.generic import DetailView, TemplateView, ListView

TEMP_TRESHOLD = 8
UMI_TRESHOLD = 80


class HomeView(TemplateView):
    template_name = 'main/home.html'

def process_data(request):
    if request.method == 'POST':
        data = []# prendi i dati dalla post
        alarm(data)

def alarm(sensors):
    # Dobbiamo decidere un ordine prestabilito dato che sappiamo solo il dato
    if sensors[0] >= TEMP_TRESHOLD:
        pass    # do something

    if sensors[1] >= UMI_TRESHOLD:
        pass    # do something