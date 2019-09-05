import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from socios.models import KerEvento

roles = [
['Beneficios','Se registra todo lo relativo a beneficios'],
['Reclamos','Se registra todo lo relativo a reclamos del socio'],
['Otros','Otras atenciones'],
]

print('populating eventos')

for r in roles:
    rol = KerEvento.objects.get_or_create(tipo_evento=r[0],descripcion=r[1],user_creacion='167458262')

print('populating eventos completed')
