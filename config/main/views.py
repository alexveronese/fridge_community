from typing import Any

import requests
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from django.contrib.auth.decorators import login_required
from braces.views import GroupRequiredMixin, LoginRequiredMixin
from .forms import CreateFridgeForm, AddFridgeForm
from .models import *



class HomeView(TemplateView):
    template_name = 'main/home.html'

# Operators views
class CreateFridgeView(GroupRequiredMixin, CreateView):
    group_required = ["Operators"]
    title = "Register new Fridge"
    form_class = CreateFridgeForm
    template_name = "main/create_entry.html"
    success_url = reverse_lazy("main:home")

# Customers views
class FridgeListView(ListView):
    title = "Fridge List"
    model = Fridge
    template_name = "main/fridge_list.html"

    def get_queryset(self):
        return Fridge.objects.all().order_by("id")


@login_required
def addFridge(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    if fridge.user is not None:
        return redirect(reverse("main:fridge_list") + "?conf=err")
    else:
        if request.method == "POST":
            form = AddFridgeForm(request.POST)
            if form.is_valid():
                secret_number = form.cleaned_data.get("secret_number")
                if secret_number == fridge.secret_number:
                    fridge.user = request.user
                    fridge.save()
                    return redirect(reverse("main:my_fridge_list"))
                else:
                    return redirect(reverse("main:fridge_list") + "?conf=err")

        form = AddFridgeForm()
        return render(request, template_name="main/add_fridge.html", context={"fridge": fridge, "form": form})


class MyFridgeListView(LoginRequiredMixin, ListView):
    model = Fridge
    title = "My Fridges"
    template_name = "main/my_fridge_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        user = User.objects.filter(id=self.request.user.id)[0]
        return Fridge.objects.filter(user=user)


def process_data(request):
    if request.method == 'POST':
        data = request.POST.dict()
        fridge_id = data.get('id')
        button_state = data.get('button_state')
        temp_in = data.get('temp_in')
        hum_in = data.get('hum_in')
        temp_out = data.get('temp_out')
        pot_val = data.get('pot_val')
        alarm = data.get('alarm')

        fridge = get_object_or_404(Fridge, pk=fridge_id)
        if not fridge:
            return print(f'fridge {fridge_id} not exist')

        sfeed = SensorFeed(
            fridge=fridge_id,
            door=button_state,
            int_temp=temp_in,
            int_hum=hum_in,
            ext_temp=temp_out,
            power_consumption=pot_val
        )
        sfeed.save()

        # alarm
        url = "https://api.telegram.org/bot7953385844:AAHapKUAmpOs6OSml9S5X8Zg-0xmLO8GX6A"
        if alarm[0]:
            # temperatureIN too high
            x = requests.post(url + "/notify", data=sfeed.int_temp) # cambiare nome "/notify" con metodo del bot


        print(f"Dati ricevuti: {data}") # debug

