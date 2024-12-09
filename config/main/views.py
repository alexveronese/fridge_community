from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from braces.views import GroupRequiredMixin
from main.forms import CreateFridgeForm
from .models import *



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
        data = request.form.to_dict()
        values = data.get("value")
        print(f"Dati ricevuti: {data}") # debug


