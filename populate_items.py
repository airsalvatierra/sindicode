import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from finanzas.models import Item

items = [
['Cuotas Planilla','Cuota Sindical','Vigente','167458262'],
['Cuotas Planilla','Aportantes','Vigente','167458262'],
['Cuotas Planilla','Devolucion Prestamos Sindicales','Vigente','167458262'],
['Cuotas Planilla','Cuotas Club de Pesca','Vigente','167458262'],
['Cuotas Planilla','Convenio BCI Nova','Vigente','167458262'],
['Cuotas Planilla','Convenio CrediChile','Vigente','167458262'],
['Cuotas Planilla','Convenio BBVA','Vigente','167458262'],
['Cuotas Planilla','Devolucion Giannina Barahona','Vigente','167458262'],
['Multas Sindicales','Multas Sindicales','Vigente','167458262'],
['Interes Inversiones','Interes Inversiones','Vigente','167458262'],
['Venta Activos Fijos Sin Uso','Venta Activos Fijos Sin Uso','Vigente','167458262'],
['Aportes Sindicales Externos','Aportes Sindicales Externos','Vigente','167458262'],
['Depositos a Plazo 1','Depositos a Plazo 1','Vigente','167458262'],
['Depositos a Plazo - Pre Universitario','Depositos a Plazo - Pre Universitario','Vigente','167458262'],
['Depositos a Plazo - Capacitacion','Depositos a Plazo - Capacitacion','Vigente','167458262'],
['Reingresos por Saldos FXR','Reingresos por Saldos FXR','Vigente','167458262'],
['Remuneraciones y Leyes Sociales','Pago Personal Sindicato','Vigente','167458262'],
['Remuneraciones y Leyes Sociales','Pago Leyes Sociales Personal Sindicato','Vigente','167458262'],
['Asesorias','Contable','Vigente','167458262'],
['Asesorias','Informatica','Vigente','167458262'],
['Asesorias','Periodista','Vigente','167458262'],
['Asesorias','Laboral','Vigente','167458262'],
['Asesorias','Ergonomica','Vigente','167458262'],
['Asesorias','Pago Retenciones','Vigente','167458262'],
['Servicios Juridicos Socios-Organizacion','Servicios Juridicos','Vigente','167458262'],
['Servicios Juridicos Socios-Organizacion','Pago Retencion Impuesto','Vigente','167458262'],
['Balance, EERR y Renta','Balance, EERR y Renta','Vigente','167458262'],
['Servicios Basicos','Luz','Vigente','167458262'],
['Servicios Basicos','Celular','Vigente','167458262'],
['Servicios Basicos','Internet','Vigente','167458262'],
['Servicios Basicos','Clave','Vigente','167458262'],
['Articulos de Oficina','Articulos de Oficina','Vigente','167458262'],
['Mantencion y Reparacion Oficina y Equipos','Mantencion y Reparacion Oficina y Equipos','Vigente','167458262'],
['Arriendos','Arriendos','Vigente','167458262'],
['Gastos Comunes','Gastos Comunes','Vigente','167458262'],
['Contribuciones y Gastos Notariales','Contribuciones y Gastos Notariales','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Matrimonio','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Nacimiento','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Defuncion','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Asignacion Escolar Carga','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Asignacion Escolar Trabajador','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Beneficio Gastos Funerales','Vigente','167458262'],
['Beneficios Entregados Sin Retorno','Aportes','Vigente','167458262'],
['Beneficios Entregados - Prestamos','Prestamo Auxilio General','Vigente','167458262'],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Medico','Vigente','167458262'],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Combinado','Vigente','167458262'],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Especial','Vigente','167458262'],
['Cuotas Federacion','Cuotas Federacion','Vigente','167458262'],
['Conmemoración Giannina Barahona','Conmemoración Giannina Barahona','Vigente','167458262'],
['Conmemoración Dia de la Mujer','Conmemoración Dia de la Mujer','Vigente','167458262'],
['Conmemoración 1 de Mayo','Conmemoración 1 de Mayo','Vigente','167458262'],
['Campeonato Copa Sindicato Unificado','Campeonato Copa Sindicato Unificado','Vigente','167458262'],
['Fiestas Patrias','Fiestas Patrias','Vigente','167458262'],
['Aniversario','Aniversario','Vigente','167458262'],
['Tocata','Tocata','Vigente','167458262'],
['Navidad','Navidad','Vigente','167458262'],
['Despedida por Retiros','Despedida por Retiros','Vigente','167458262'],
['Seminario/Capacitacion','Seminario/Capacitacion','Vigente','167458262'],
['Seminario Salud Laboral','Seminario Salud Laboral','Vigente','167458262'],
['Aportes Actividades Socios','Fiestas Patrias','Vigente','167458262'],
['Aportes Actividades Socios','Fin de Año','Vigente','167458262'],
['Aportes Actividades Socios','Especiales','Vigente','167458262'],
['Gastos Bancarios','Gastos Bancarios','Vigente','167458262'],
['Gastos Eventos y Reuniones (Asambleas)','Gastos Eventos y Reuniones (Asambleas)','Vigente','167458262'],
['Gastos Representacion y Otros','Gastos Representacion y Otros','Vigente','167458262'],
['Gastos Oficina (Alimentacion)','Gastos Oficina (Alimentacion)','Vigente','167458262'],
['Patrimonio','Patrimonio','Vigente','167458262'],
['Conservacion Patrimonio','Conservacion Patrimonio','Vigente','167458262'],
['Biblioteca Sindical','Biblioteca Sindical','Vigente','167458262'],
['Software Contable','Software Contable','Vigente','167458262'],
['Pre Universitario','Pre Universitario','Vigente','167458262'],
['Imprevistos','Imprevistos','Vigente','167458262'],
]

print('populating items')

for i in items:
    item = Item.objects.get_or_create(nombre=i[0]+' - '+i[1],item=i[0],subitem=i[1],estado='Vigente',user_creacion='167458262')

print('populating items completed')
