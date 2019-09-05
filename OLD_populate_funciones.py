import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from socios.models import KerRol, KerFun

roles = [
['Administracion','Rol para dar o revocar roles a los socios'],
['Socio','Todos los usuarios tienen este rol y sirve para ver la informacion personal propia y editar algunos campos personales'],
['Mantencion','Rol para agregar, editar, actualizar y/o desactivar socios'],
['Asistencia','Rol para ingresar y ver funcionalidades de asistencia'],
['Contabilidad','Rol para ver e ingresar movimientos contables, ver balance y reportes'],
['Historial','Rol para ver el log (historial) de las tablas (permite ver quien ha realizado cambios en las tablas)']
]

# print('populating roles')
#
# for r in roles:
#     rol = KerRol.objects.get_or_create(tipo_rol=r[0],descripcion=r[1],user_creacion='167458262')
#
# print('populating roles completed')
