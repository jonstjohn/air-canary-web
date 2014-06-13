from django.shortcuts import render

from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    Home page view
    """
    template_name = 'places/home.html'
