from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from braces.views import GroupRequiredMixin
from main.forms import CreateFridgeForm
from .models import *

TEMP_TRESHOLD = 8
UMI_TRESHOLD = 80


class HomeView(TemplateView):
    template_name = 'main/home.html'


class CreateFridgeView(GroupRequiredMixin, CreateView):
    group_required = ["Operators"]
    title = "Register new Fridge"
    form_class = CreateFridgeForm
    template_name = "main/create_entry.html"
    success_url = reverse_lazy("main:home")


class FridgeListView(ListView):
    title = "Fridge List"
    model = Fridge
    template_name = "main/fridge_list.html"

    def get_queryset(self):
        return Fridge.objects.all().order_by("id")




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