from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import ForeignKey
from django.contrib.auth.models import User
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

def notify_telegram_bot(message: str, chat_id: int):
    """
    Send a notification to the user via Telegram bot.
    """
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(BOT_API_URL, json=payload)
    return response.status_code

ACCEPTABLE_RANGES = {
    'int_temp': (0, 10),  
    'ext_temp': (0, 35),  
    'int_hum': (30, 70),  
    'ext_hum': (30, 70),  
    'power_consumption': (0, 1000),
}


@receiver(post_save, sender=SensorFeed)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        fridge_serial_number = instance.fridge.serial_number
        try:

            telegram_user = TelegramUser.objects.get(fridge_id=fridge_serial_number)
            out_of_range_values = []
            sensor_feed_list = SensorFeed.objects.values().filter(fridge=instance.fridge).order_by('-timestamp')
            sensor_feed = sensor_feed_list[1] if len(sensor_feed_list) > 1 else None
            if instance.door and sensor_feed.door:
                out_of_range_values.append("🚪Door is open")
            if not (ACCEPTABLE_RANGES['int_temp'][0] <= instance.int_temp <= ACCEPTABLE_RANGES['int_temp'][1]) and instance.door:
                out_of_range_values.append(f"🌡️Internal temperature: {instance.int_temp}°C")
            if not (ACCEPTABLE_RANGES['ext_temp'][0] <= instance.ext_temp <= ACCEPTABLE_RANGES['ext_temp'][1]):
                out_of_range_values.append(f"🌡External temperature: {instance.ext_temp}°C")
            if not (ACCEPTABLE_RANGES['int_hum'][0] <= instance.int_hum <= ACCEPTABLE_RANGES['int_hum'][1]):
                out_of_range_values.append(f"💧Internal humidity: {instance.int_hum}%")
            if not (ACCEPTABLE_RANGES['ext_hum'][0] <= instance.ext_hum <= ACCEPTABLE_RANGES['ext_hum'][1]):
                out_of_range_values.append(f"❄️External humidity: {instance.ext_hum}%")
            if not (ACCEPTABLE_RANGES['power_consumption'][0] <= instance.power_consumption <= ACCEPTABLE_RANGES['power_consumption'][1]):
                out_of_range_values.append(f"⚡Power consumption: {instance.power_consumption}W")

            if out_of_range_values:
                message = f"⚠️New sensor feed added for fridge {fridge_serial_number} with out-of-range values:\n" + "\n".join(out_of_range_values) + "\nPlease check the fridge.⚠️"
                notify_telegram_bot(message, telegram_user.chat_id)

        except TelegramUser.DoesNotExist:
            pass  # Cosa si fa se non c'è un utente Telegram associato a quel frigo?
