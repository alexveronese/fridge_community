import datetime

from django.forms import BooleanField

from main.models import *
from datetime import timedelta, timezone
from django.contrib.auth.models import User
import random
from django.contrib.auth.models import Group, Permission

def erase_db():
    print("Erasing DB")
    Fridge.objects.all().delete()
    SensorFeed.objects.all().delete()
    User.objects.all().delete()
    TelegramUser.objects.all().delete()
    print("DB empty")


def init_db():
    if len(Fridge.objects.all()) != 0:
        return

    if len(User.objects.all()) <= 1:
        print("Creating Customers")
        for i in range(1, 5):
            u = User.objects.create_user(username="user" + str(i), password="samplepw1!")
            g = Group.objects.get(name="Customers")
            g.user_set.add(u)
            print("Created user" + str(i) + " with name:  " + u.username)
            u.save()

        print("Creating Operators")
        m = User.objects.create_user(username="operator1", password="samplepw1!")
        g = Group.objects.get(name="Operators")
        g.user_set.add(m)

    print("Creating Fridges")
    for i in range(1, 5):
        f = Fridge()
        f.serial_number = str(i)
        f.secret_number = str(i) + str(i) + str(i)
        f.save()

    print("Creating SensorFeeds")
    for i in range(1, 20):
        s = SensorFeed()
        s.fridge = Fridge.objects.get(pk=1)
        s.door = random.choice([True, False])
        s.int_temp = random.randint(2, 15)
        s.int_hum = random.randint(20, 70)
        s.ext_temp = random.randint(18, 35)
        s.power_consumption = random.randint(0, 1000)
        s.timestamp = datetime.datetime.now() + timedelta(seconds=5 * i)
        s.save()

        if s.int_temp > 5 and s.door == False:
            s.alarm_temp = True
        else:
            s.alarm_temp = False

        s.save()

    print("Associating Fridge and Users")
    fridge = Fridge.objects.get(pk=1)
    user = User.objects.get(username="user1")
    fridge.user = user
    fridge.save()


    print("DB initialized")

def init_groups():
    customers = Group.objects.get_or_create(name="Customers")
    customers_perms = []

    operator = Group.objects.get_or_create(name="Operators")
    operators_perms = []
    print("Groups initialized")