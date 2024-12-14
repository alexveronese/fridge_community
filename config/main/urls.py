from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("regfridge/", CreateFridgeView.as_view(), name="register_fridge"),
    path("fridgelist/", FridgeListView.as_view(), name="fridge_list"),
    path("addfridge/<pk>/", addFridge, name="add_fridge"),
    path("myfridgelist/", MyFridgeListView.as_view(), name="my_fridge_list"),
    path("data/", process_data, name="process_data"),
    path('grafico/', get_grafico, name='Chart_Data'),
]