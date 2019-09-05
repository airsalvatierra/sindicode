from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from asistencias.models import AsistenciaEnc,AsistenciaDet

class AsistenciaEncAdmin(admin.ModelAdmin):
    fields = ['fec_evento','tipo_evento','archivo','cant_asistencias','cant_ausentes','cant_total']
    list_display = ['fec_evento','tipo_evento','archivo','cant_asistencias','cant_ausentes','cant_total']

class AsistenciaDetAdmin(admin.ModelAdmin):
    fields = ['fec_evento','rut_socio','nombre','apellido','est_asistencia']
    list_display = ['fec_evento','rut_socio','nombre','apellido','est_asistencia']


# Register your models here.
admin.site.register(AsistenciaEnc,AsistenciaEncAdmin)
admin.site.register(AsistenciaDet,AsistenciaDetAdmin)
