import json
import random
from typing import Any
from xml.sax.handler import version

import requests as rq
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from django.contrib.auth.decorators import login_required
from braces.views import GroupRequiredMixin, LoginRequiredMixin

from .forms import CreateFridgeForm, AddFridgeForm
from .models import *
import pandas as pd
import joblib


# Telegram Bot Configuration
BOT_TOKEN = "7953385844:AAHapKUAmpOs6OSml9S5X8Zg-0xmLO8GX6A"  # Replace with your actual bot token
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
class HomeView(TemplateView):
    template_name = 'main/home.html'

# Operators views
class CreateFridgeView(GroupRequiredMixin,CreateView):
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
        user = self.request.user
        return Fridge.objects.order_by("serial_number")


class RegFridgeListView(ListView):
    title = "Fridge List"
    model = Fridge
    template_name = "main/fridge_list.html"

    def get_queryset(self):
        user = self.request.user
        return Fridge.objects.filter(user=None).order_by("serial_number")

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
    """Reiceves data from Bridge

    Pattern received = { id, button_state, temp_in, hum_in, temp_out, pot_val}
    add instance SensorFeed to database


   """
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

        if int(temp_in) > 5 and button_state == '0':
            alarm = 1
        else:
            alarm = 0

        # alarm = 1

        sfeed = SensorFeed(
            fridge=fridge,
            door=button_state,
            int_temp=temp_in,
            int_hum=hum_in,
            ext_temp=temp_out,
            power_consumption=pot_val,
            alarm_temp=alarm
        )
        try:
            sfeed.full_clean()
            sfeed.save()
        except ValidationError as e:
            print("Validation Error", e)


        print(f"Dati ricevuti: {data}") # debug

        send_telegram_notification(sfeed)

        return HttpResponse('Ok')


@login_required
def get_grafico(request, pk):
    """Render Grafici.html

    Pass {temp, hum_in, pow_consumption} to html for creating graph

    """

    fridge = get_object_or_404(Fridge, pk=pk)
    # fridge = None

    #if not fridge:
    #    fridge = Fridge.objects.create(serial_number=1, user=request.user.id)

    """
    for i in range(1):
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
    time = []
    set = SensorFeed.objects.values().order_by('-timestamp')[:10]

    # send_data_TELEGRAM([1],0)
    for s in set:
        temp.append(s.get('int_temp'))
        hum.append(s.get('int_hum'))
        pow_cons.append(s.get('power_consumption'))
        time.append((s.get('timestamp')).strftime('%H:%M:%S'))


    temp = temp[::-1]
    hum = hum[::-1]
    pow_cons = pow_cons[::-1]
    time = time[::-1]
    return render(request, 'main/chart_data.html', {'pk': pk, 'temp': temp, 'hum': hum, 'pow': pow_cons, 'time': time})




def predict(external_temp, internal_temp_variation, door_open_time):
    """Predict using random_forest algorithm

    Return { 0 --> Behaving well,
             2 --> Behaving inappropriately,
             other --> Bad }

    """
    new_data = pd.DataFrame(data={
        'external_temp': external_temp,
        'internal_temp_variation': internal_temp_variation,
        'door_open_time': door_open_time
    }, index=[0, 1, 2])

    print(type(door_open_time))

    clf_loaded=joblib.load('C:\\Users\\veron\\Desktop\\Uni\\LM\\1_ANNO\\1_SEM\\IOT\\fridge_community\\config\\main\\random_forest_model.pkl')

    # Prediction on new data
    prediction = clf_loaded.predict(new_data)

    if prediction[0] == 0:
        print("The user is behaving well")  # good
    elif prediction[0] == 2:
        print("The user is behaving inappropriately")  # medium
    else:
        print("The user is behaving terribly")  # bad
    return prediction[0]


def send_alarm(request, pk):
    """Process GET from Bridge

    Bridge need to know if alarms have gone off

    """
    fridge = get_object_or_404(Fridge, pk=pk)
    alarm = SensorFeed.objects.filter(fridge=fridge).order_by('timestamp').reverse()[0]
    if request.method == 'GET':
        return JsonResponse(data={'value': alarm.alarm_temp})


def process_bot_predict(request, pk):
    """Process behaving evaluation from telegram

    gets the last sensorfeeds sampled with an open_door value and predict behave

    """
    fridge = get_object_or_404(Fridge, pk=pk)
    if request.method == 'GET':
        sfeed = SensorFeed.objects.filter(fridge=fridge).order_by('timestamp').reverse()[0:]
        last = sfeed[0]
        first = None
        for feed in sfeed:
            if not feed.door:
                first = feed
                break

        if first is None:
            first = sfeed[len(sfeed) - 1]

        time_opened = last.timestamp - first.timestamp
        time_opened_float = time_opened.total_seconds()

        var = abs(last.int_temp - first.int_temp)

        pred = predict(last.ext_temp, var, time_opened_float)

        return JsonResponse(data={'value': str(pred)})




@csrf_exempt
def store_chat_id(request):
    """
    API endpoint to store the user's Telegram chat_id.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            username = data.get('username')
            fridge_id =  data.get('fridge_id')

            if not chat_id:
                return JsonResponse({'error': 'chat_id is required'}, status=400)

            # Save or update the chat_id in the database
            user, created = TelegramUser.objects.update_or_create(
                chat_id=chat_id,
                defaults={'username': username, 'fridge_id': fridge_id},
            )
            return JsonResponse({'status': 'success', 'created': created})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)












@csrf_exempt
def store_chat_id(request):
    """
    API endpoint to store the user's Telegram chat_id.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            username = data.get('username')
            fridge_id =  data.get('fridge_id')

            if not chat_id:
                return JsonResponse({'error': 'chat_id is required'}, status=400)

            # Save or update the chat_id in the database
            user, created = TelegramUser.objects.update_or_create(
                chat_id=chat_id,
                defaults={'username': username, 'fridge_id': fridge_id},
            )
            return JsonResponse({'status': 'success', 'created': created})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_least_recent_data(request):
    """
    API endpoint to get the least recent data from the SensorFeed model.
    """
    if request.method == 'GET':
        try:
            data = json.loads(request.body)
            fridge_number = data.get('fridge_number')
            chat_id = data.get('chat_id')

            if not fridge_number:
                return JsonResponse({'error': 'fridge_number is required'}, status=400)

            if not chat_id:
                return JsonResponse({'error': 'chat_id is required'}, status=400)

            if not TelegramUser.objects.filter(fridge_id=fridge_number, chat_id=chat_id).exists():
                return JsonResponse({'error': 'Unauthorized'}, status=401)

            fridge = Fridge.objects.get(serial_number=fridge_number)

            sensor_feed = SensorFeed.objects.values().filter(fridge=fridge).order_by('timestamp').last()
            if sensor_feed:
                response_data = {
                    'fridge': fridge.serial_number,
                    'door': sensor_feed.get('door'),
                    'int_temp': sensor_feed.get('int_temp'),
                    'int_hum': sensor_feed.get('int_hum'),
                    'ext_temp': sensor_feed.get('ext_temp'),
                    'power_consumption': sensor_feed.get('power_consumption'),
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'No data found'}, status=404)
        except Fridge.DoesNotExist:
            return JsonResponse({'error': 'Fridge not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def notify_telegram_bot(message: str, chat_id: int):
    """
    Send a notification to the user via Telegram bot.
    """
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = rq.post(BOT_API_URL,json=payload)

    return response.status_code


def get_alarm_history(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    try:
        alarms = SensorFeed.objects.filter(alarm_temp=True, fridge=fridge).order_by('-timestamp')
    except SensorFeed.DoesNotExist:
        alarms = []
    return render(request, 'main/alarms_history.html', {'pk': pk, 'alarms': alarms})



ACCEPTABLE_RANGES = {
    'int_temp': (0, 10),
    'ext_temp': (0, 35),
    'int_hum': (20, 70),
    'power_consumption': (0, 1000),
}

#def send_telegram_notification(sender, instance, created, **kwargs):
@receiver(post_save, sender=SensorFeed)
def send_telegram_notification(instance, **kwargs):
    #if created:
    fridge_serial_number = instance.fridge.serial_number
    try:

        telegram_user = TelegramUser.objects.get(fridge_id=fridge_serial_number)
        out_of_range_values = []
        sensor_feed_list = SensorFeed.objects.values().filter(fridge=instance.fridge).order_by('-timestamp')
        if len(sensor_feed_list) > 1:
            sensor_feed = SensorFeed(
                int_temp=sensor_feed_list[2]['int_temp'],
                door=sensor_feed_list[2]['door'],
                int_hum=sensor_feed_list[2]['int_hum'],
                ext_temp=sensor_feed_list[2]['ext_temp'],
                power_consumption=sensor_feed_list[2]['power_consumption']
            )
        else:
            sensor_feed = None
        if instance.door and sensor_feed.door:
            out_of_range_values.append("🚪Door is open")
        if not (ACCEPTABLE_RANGES['int_temp'][0] <= instance.int_temp <= ACCEPTABLE_RANGES['int_temp'][1]) and instance.door:                out_of_range_values.append(f"🌡️Internal temperature: {instance.int_temp}°C")
        if not (ACCEPTABLE_RANGES['ext_temp'][0] <= instance.ext_temp <= ACCEPTABLE_RANGES['ext_temp'][1]):
            out_of_range_values.append(f"🌡External temperature: {instance.ext_temp}°C")
        if not (ACCEPTABLE_RANGES['int_hum'][0] <= instance.int_hum <= ACCEPTABLE_RANGES['int_hum'][1]):                out_of_range_values.append(f"💧Internal humidity: {instance.int_hum}%")
        if not (ACCEPTABLE_RANGES['power_consumption'][0] <= instance.power_consumption <= ACCEPTABLE_RANGES['power_consumption'][1]):
            out_of_range_values.append(f"⚡Power consumption: {instance.power_consumption}W")

        if out_of_range_values:
            message = f"⚠️New sensor feed added for fridge {fridge_serial_number} with out-of-range values:\n" + "\n".join(out_of_range_values) + "\nPlease check the fridge.⚠️"
            notify_telegram_bot(message, telegram_user.chat_id)

    except TelegramUser.DoesNotExist:
        pass
