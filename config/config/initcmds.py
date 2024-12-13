from main.models import *
from datetime import timedelta
from django.contrib.auth.models import User
import random
from django.contrib.auth.models import Group, Permission

def erase_db():
    print("Erasing DB")
    Fridge.objects.all().delete()
    print("DB empty")


def init_db():
    if len(Fridge.objects.all()) != 0:
        return

    print("Creating DB")

    # code for creating DB

    print("DB initialized")

def init_groups():
    customers = Group.objects.get_or_create(name="Customers")
    customers_perms = []

    manager = Group.objects.get_or_create(name="Managers")
    managers_perms = []
    print("Groups initialized")