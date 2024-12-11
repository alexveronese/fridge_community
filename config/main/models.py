from django.db import models
from django.db.models import ForeignKey
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Fridge(models.Model):
    serial_number = models.IntegerField(default=1, validators=[MaxValueValidator(255), MinValueValidator(1)])
    secret_number = models.CharField(max_length=3)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class SensorFeed(models.Model):
    fridge = ForeignKey(Fridge, on_delete=models.CASCADE)

    door = models.BooleanField(default=False)
    int_temp = models.IntegerField(default=0)
    int_hum = models.IntegerField(default=0)
    ext_temp = models.IntegerField(default=0)
    ext_hum = models.IntegerField(default=0)
    power_consumption = models.IntegerField(default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

"""
class Anomaly(models.Model):
    fridge = ForeignKey(Fridge, on_delete=models.CASCADE)
"""