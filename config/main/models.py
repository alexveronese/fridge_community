from django.contrib.sites import requests
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import ForeignKey
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class Fridge(models.Model):
    serial_number = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(253)], primary_key=True)
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
    alarm_temp = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)

"""
class Anomaly(models.Model):
    fridge = ForeignKey(Fridge, on_delete=models.CASCADE)
"""

class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)  # Unique Telegram chat ID
    username = models.CharField(max_length=150, null=True, blank=True)  # Telegram username
    first_name = models.CharField(max_length=150, null=True, blank=True)  # User's first name
    last_name = models.CharField(max_length=150, null=True, blank=True)  # User's last name
    is_active = models.BooleanField(default=True)  # Whether the user is active
    subscribed_at = models.DateTimeField(auto_now_add=True)  # When the user subscribed
    unsubscribed_at = models.DateTimeField(null=True, blank=True)  # When the user unsubscribed
    fridge_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return self.username or f"Chat ID: {self.chat_id}"

# Telegram Bot Configuration
BOT_TOKEN = "7953385844:AAHapKUAmpOs6OSml9S5X8Zg-0xmLO8GX6A"  # Replace with your actual bot token
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"



