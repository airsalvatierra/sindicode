from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from socios.models import User,KerRol,KerFun,Region,Comuna,KerSocioRol,KerEvento

class UserAdmin(admin.ModelAdmin):
    fields = ['username','email','first_name','last_name','is_superuser','is_staff','is_office','foto','fec_creacion','user_creacion']
    search_fields = ['username','is_office']
    list_display = ['username','email','first_name','last_name','is_superuser','is_staff','is_office','fec_creacion','user_creacion']

class KerRolAdmin(admin.ModelAdmin):
    fields = ['tipo_rol','descripcion']

class KerFunAdmin(admin.ModelAdmin):
    fields = ['rol','fun','descripcion']

class KerSocioRolAdmin(admin.ModelAdmin):
    fields = ['socio','rol','fec_creacion','user_creacion']
    list_display = ['socio','rol','fec_creacion','user_creacion']

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(KerRol,KerRolAdmin)
admin.site.register(KerFun,KerFunAdmin)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(KerSocioRol,KerSocioRolAdmin)
admin.site.register(KerEvento)
