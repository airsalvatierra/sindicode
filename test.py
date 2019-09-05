import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from django.db.models.functions import TruncMonth
import datetime

from finanzas.models import IngresoEgreso
from django.utils.translation import gettext
from calendar import monthrange

###############################################################################

pendientes  = IngresoEgreso.objects.exclude(estado="Cerrado").annotate(fec_trunc=TruncMonth('fecha')).values('fec_trunc').distinct()
# # pendientes  = IngresoEgreso.objects.exclude(estado="Cerrado").annotate(fec_trunc=TruncMonth('fecha')).only('fecha').distinct()
# # print(pendientes)
# # MESES = list([(pen['fec_trunc'], pen['fec_trunc'].strftime("%m-%Y")) for pen in pendientes])
# # tuple(BLANK_CHOICE_DASH + [(choice.username, choice) for choice in get_user_model().objects.all().order_by('last_name')])
# MESES = []
# # # #
# for pen in pendientes:
#     MESES.append((str(pen['fec_trunc']),pen['fec_trunc'].strftime("%m-%Y")))
# #     # print(pen['fec_trunc'].strftime("%m-%Y"))
# #     # print(pen.fec_trunc)
# # #
# print(MESES)

# for pen in pendientes:
#     print(pen.fecha)
# obj = pendientes.all().values('fec_trunc')
# meses = obj.distinct()
#
# for men in meses:
#     print(men)
# for pen in pendientes:
#     if gettext(pen.fec_trunc.strftime("%B")) == 'Octubre':
#         print(gettext(pen.fec_trunc.strftime("%B")))

# mes = 10
# pendientes = IngresoEgreso.objects.filter(fecha__month=mes).exclude(estado="Cerrado")
# for pen in pendientes:
#     print(pen)

dia = '2018-10-08'
nuevo = datetime.datetime.strptime(dia,"%Y-%m-%d")
ini_mes = nuevo.replace(day=1)
cant_dias_mes = monthrange(ini_mes.year,ini_mes.month)
fin_mes = nuevo.replace(day=cant_dias_mes[1])
pendientes = IngresoEgreso.objects.filter(fecha__range=(ini_mes,fin_mes)).exclude(estado="Cerrado")

print(ini_mes)
print(cant_dias_mes)
print(cant_dias_mes[1])
print(fin_mes)
print('----')
for pen in pendientes:
    print('folio: ' + str(pen.folio) + ' - fecha: ' + pen.fecha.strftime("%d-%m-%Y"))
