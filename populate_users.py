import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import sys, csv
from itertools import cycle

import django
django.setup()
from django.utils import timezone

# Funcion para Validar Rut
def validarRut(rut):
	rut = rut.upper();
	rut = rut.replace("-","")
	rut = rut.replace(".","")
	aux = rut[:-1]
	dv = rut[-1:]

	revertido = map(int, reversed(str(aux)))
	factors = cycle(range(2,8))
	s = sum(d * f for d, f in zip(revertido,factors))
	res = (-s)%11

	if str(res) == dv:
		return True
	elif dv=="K" and res==10:
		return True
	else:
		return False

# from sindicato.settings import AUTH_USER_MODEL
from socios.models import User, KerRol, KerSocioRol

print('Leyendo archivo')

with open('bd_sindicato.csv','r') as csv_file:
	csv_reader = csv.reader(csv_file)
	next(csv_reader)

	with open('informe_carga_bd.csv','w') as new_file:
		csv_writer = csv.writer(new_file)

		print('populating user')
		for line in csv_reader:

			if not validarRut(line[1]):
				linea = 'linea '+line[0]+' - Rut '+line[1]+' es invalido'
				linea.replace('\n', '').replace('\r', '')
				csv_writer.writerow(linea)
			elif not line[7]:
				linea = 'linea '+line[0]+' - Rut '+line[1]+' no tiene correo electronico'
				linea.replace('\n', '').replace('\r', '')
				csv_writer.writerow(linea)
			else:
				usuario = User()
				usuario.username = line[1]
				usuario.email = line[7]
				usuario.first_name = line[4]
				usuario.nom_adicional = line[5]
				usuario.last_name = line[2]
				usuario.ape_materno = line[3]
	            # Valida si tiene direccion
				# if line[8]:
				# 	usuario.dir_domicilio = line[8]
	            # Valida si tiene telefono
				if line[10]:
					usuario.tel_celular = line[10]
				# Valida si tiene el numero de hijos
				if line[11]:
					usuario.num_hijos = line[11]
				# Valida si tiene el estado civil
				if line[14]:
					usuario.estado_civil = line[14]
				usuario.estado_socio = 'Vigente'
				usuario.user_creacion = '167458262'
				usuario.save()
				#usuario.set_password()
				#usuario.save()

				rol = KerRol.objects.get(tipo_rol='Socio')
				sociorol = KerSocioRol.objects.create(socio=usuario,rol=rol,user_creacion='167458262')
				sociorol.save()

				linea = 'linea '+line[0]+' - Rut '+line[1]+' se ha creado como socio en la base de datos'
				linea.replace('\n', '').replace('\r', '')
				csv_writer.writerow(linea)

print('populating user completed')
