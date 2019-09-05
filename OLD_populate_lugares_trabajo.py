import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from socios.models import KerLugarTrabajo

lugares = [
['Linea 1','PML SP','Puesto de Maniobra Local SP'],
['Linea 1','PML PJ','Puesto de Maniobra Local PJ'],
['Linea 1','PML MQ','Puesto de Maniobra Local MQ'],
['Linea 1','PML LD','Puesto de Maniobra Local LD'],
['Linea 1','CPS','Acopio Vigilante Privado'],
['Linea 1','Cochera/Taller Neptuno',''],
['Linea 2','PML LC','Puesto de Maniobra Local LC'],
['Linea 2','PML VN','Puesto de Maniobra Local VN'],
['Linea 2','CPS ZP','Acopio Vigilante Privado ZP'],
['Linea 2','CPS LC','Acopio Vigilante Privado LC'],
['Linea 2','Cochera/Taller Lo Ovalle',''],
['Linea 4','PML TOB','Puesto de Maniobra Local TOB'],
['Linea 4','PPA','PPA'],
['Linea 4','Cochera/Taller Puente Alto',''],
['Linea 4','Cochera/Taller Intermedio Quilín',''],
['Linea 4a','PML LCI','Puesto de Maniobra Local LCI'],
['Linea 4a','PML VIM','Puesto de Maniobra Local VIM'],
['Linea 5','PML PM','Puesto de Maniobra Local PM'],
['Linea 5','PML VV','Puesto de Maniobra Local VV'],
['Linea 5','Cochera/Taller San Eugenio',''],
['Linea 6','Linea 6',''],
['Edifico SEAT PCC','Edifico SEAT PCC',''],
]

print('populating roles')

for l in lugares:
    if l[1] == 'Cochera/Taller Neptuno':
        lugar = KerLugarTrabajo.get_or_create(linea=l[0],
                                        lugar=l[1],
                                        nombre_corto=l[0]+' - '+l[1],
                                        nombre_largo=l[0]+' - '+l[1],
                                        user_creacion='167458262')
    elif l[0] == 'Linea 6' or l[0] == 'Edifico SEAT PCC':
        lugar = KerLugarTrabajo.get_or_create(linea=l[0],
                                        lugar=l[1],
                                        nombre_corto=l[0],
                                        nombre_largo=l[0],
                                        user_creacion='167458262')
    else:
        lugar = KerLugarTrabajo.get_or_create(linea=l[0],
                                        lugar=l[1],
                                        nombre_corto=l[0]+' - '+l[1],
                                        nombre_largo=l[0]+' - '+l[2],
                                        user_creacion='167458262')

print('populating roles completed')
