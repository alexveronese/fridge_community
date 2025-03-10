from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("regfridge/", CreateFridgeView.as_view(), name="register_fridge"),
    path("fridgelist/", FridgeListView.as_view(), name="fridge_list"),
    path("regfridgelist", RegFridgeListView.as_view(), name="regfridge_list"),
    path("addfridge/<pk>/", addFridge, name="add_fridge"),
    path("myfridgelist/", MyFridgeListView.as_view(), name="my_fridge_list"),
    path("data/", process_data, name='process_data'),
    path('chart-data/<pk>/', get_grafico, name='chart_data'),
    path('data/alarm/<pk>/',send_alarm, name='send_alarm'),
    path('data/predict/<pk>/',process_bot_predict, name='process_bot_predict'),
    path('notify-bot/', notify_telegram_bot, name='notify_bot'),
    path('api/store_chat_id/', store_chat_id, name='store_chat_id'),
    path('api/get_least_recent_data/', get_least_recent_data, name='get_least_recent_data'),
]
