from django.shortcuts import render
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic import TemplateView
from django.conf import settings

class PruebaPage(LoginRequiredMixin,TemplateView):
    template_name = 'stuff_base_ejemplo.html'

def prueba2(request):
    print(settings.BASE_DIR)
    context = {
        'base':settings.BASE_DIR
    }
    return render(request,'stuff_base_ejemplo.html',context)
