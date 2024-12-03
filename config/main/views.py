from django.shortcuts import render
from django.views.generic import DetailView, TemplateView, ListView


class HomeView(TemplateView):
    template_name = 'main/home.html'
