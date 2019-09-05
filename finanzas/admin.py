from django.contrib import admin
from finanzas.models import IngresoEgreso,Saldo,Item

class IngresoEgresoAdmin(admin.ModelAdmin):
    fields = ['fecha','monto','tipo_mov']
    list_display = ['fecha','monto','tipo_mov',]

class SaldoAdmin(admin.ModelAdmin):
    fields = ['item','monto','estado','fec_creacion','user_creacion']
    list_display = ['item','monto','estado']

class ItemAdmin(admin.ModelAdmin):
    fields = ['item','estado','fec_creacion','user_creacion']
    list_display = ['item','estado']


# Register your models here.
admin.site.register(IngresoEgreso,IngresoEgresoAdmin)
admin.site.register(Saldo,SaldoAdmin)
admin.site.register(Item,ItemAdmin)
