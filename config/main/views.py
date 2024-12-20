import json
import random
from typing import Any

import requests
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
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
        return Fridge.objects.all().order_by("serial_number")


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


@csrf_exempt
def process_data(request):
    if request.method == 'POST':
        data = request.POST.dict()
        fridge_id = data.get('id')
        button_state = data.get('button_state')
        temp_in = data.get('temp_in')
        hum_in = data.get('hum_in')
        temp_out = data.get('temp_out')
        pot_val = data.get('pot_val')

        fridge = get_object_or_404(Fridge, pk=fridge_id)
        if not fridge:
            return print(f'fridge {fridge_id} not exist')
        try:
            temp_in = int(temp_in)
            hum_in = int(hum_in)
            temp_out = int(temp_out)
            pot_val = int(pot_val)
        except ValueError:
            return Exception("Errore dati")

        sfeed = SensorFeed(
            fridge=fridge,
            door=button_state,
            int_temp=temp_in,
            int_hum=hum_in,
            ext_temp=temp_out,
            power_consumption=pot_val
        )
        try:
            sfeed.full_clean()
            sfeed.save()
        except ValidationError as e:
            print("Validation Error", e)


        # alarm
        url = "https://api.telegram.org/bot7953385844:AAHapKUAmpOs6OSml9S5X8Zg-0xmLO8GX6A"
        """
        if alarm[0]:
            # temperatureIN too high
            x = requests.post(url + "/notify", data=sfeed.int_temp) # cambiare nome "/notify" con metodo del bot
        """

        print(f"Dati ricevuti: {data}") # debug


@login_required
def get_grafico(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    # fridge = None
    """
    if not fridge:
        fridge = Fridge.objects.create(serial_number=1)
    for i in range(10):
    #se non avete dati di sensori mettete questi
        sfeed = SensorFeed(
            fridge=fridge,
            int_temp=random.randint(1,4),
            door=0,
            int_hum=random.randint(0,80),
            ext_temp=0,
            power_consumption=random.randint(0,5)
        )
        try:
            sfeed.full_clean()
            sfeed.save()
        except ValidationError as e:
            print("Validation Error", e)
            """
    # Passa i dati di SensorFeed al template
    temp = []
    pow_cons = []
    hum = []
    set = SensorFeed.objects.values().order_by('timestamp').reverse()[:10]
    # send_data_TELEGRAM([1],0)
    for s in set:
        temp.append(s.get('int_temp'))
        hum.append(s.get('int_hum'))
        pow_cons.append(s.get('power_consumption'))

    return render(request, 'main/grafici.html', {'temp': temp, 'hum': hum, 'pow': pow_cons})


def send_data_TELEGRAM(alarm, sfeed):

    url = "https://api.telegram.org/bot7953385844:AAHapKUAmpOs6OSml9S5X8Zg-0xmLO8GX6A"
    if alarm[0]:
        # temperatureIN too high
        message = 'Ciao! Questo è un messaggio dal bot.'
        data = {'chat_id': 1, 'text': message}
        x = requests.post(url + "/sendMessage",data=data) # cambiare nome "/notify" con metodo del bot







