import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sindicato.settings')

import django
django.setup()

from finanzas.models import Saldo, Item

saldos = [
['Cuotas Planilla','Cuota Sindical',0],
['Cuotas Planilla','Aportantes',0],
['Cuotas Planilla','Devolucion Prestamos Sindicales',0],
['Cuotas Planilla','Cuotas Club de Pesca',0],
['Cuotas Planilla','Convenio BCI Nova',0],
['Cuotas Planilla','Convenio CrediChile',0],
['Cuotas Planilla','Convenio BBVA',0],
['Cuotas Planilla','Devolucion Giannina Barahona',0],
['Multas Sindicales','Multas Sindicales',0],
['Interes Inversiones','Interes Inversiones',0],
['Venta Activos Fijos Sin Uso','Venta Activos Fijos Sin Uso',0],
['Aportes Sindicales Externos','Aportes Sindicales Externos',0],
['Depositos a Plazo 1','Depositos a Plazo 1',0],
['Depositos a Plazo - Pre Universitario','Depositos a Plazo - Pre Universitario',0],
['Depositos a Plazo - Capacitacion','Depositos a Plazo - Capacitacion',0],
['Reingresos por Saldos FXR','Reingresos por Saldos FXR',0],
['Remuneraciones y Leyes Sociales','Pago Personal Sindicato',0],
['Remuneraciones y Leyes Sociales','Pago Leyes Sociales Personal Sindicato',0],
['Asesorias','Contable',0],
['Asesorias','Informatica',0],
['Asesorias','Periodista',0],
['Asesorias','Laboral',0],
['Asesorias','Ergonomica',0],
['Asesorias','Pago Retenciones',0],
['Servicios Juridicos Socios-Organizacion','Servicios Juridicos',0],
['Servicios Juridicos Socios-Organizacion','Pago Retencion Impuesto',0],
['Balance, EERR y Renta','Balance, EERR y Renta',0],
['Servicios Basicos','Luz',0],
['Servicios Basicos','Celular',0],
['Servicios Basicos','Internet',0],
['Servicios Basicos','Clave',0],
['Articulos de Oficina','Articulos de Oficina',0],
['Mantencion y Reparacion Oficina y Equipos','Mantencion y Reparacion Oficina y Equipos',0],
['Arriendos','Arriendos',0],
['Gastos Comunes','Gastos Comunes',0],
['Contribuciones y Gastos Notariales','Contribuciones y Gastos Notariales',0],
['Beneficios Entregados Sin Retorno','Beneficio Matrimonio',0],
['Beneficios Entregados Sin Retorno','Beneficio Nacimiento',0],
['Beneficios Entregados Sin Retorno','Beneficio Defuncion',0],
['Beneficios Entregados Sin Retorno','Beneficio Asignacion Escolar Carga',0],
['Beneficios Entregados Sin Retorno','Beneficio Asignacion Escolar Trabajador',0],
['Beneficios Entregados Sin Retorno','Beneficio Gastos Funerales',0],
['Beneficios Entregados Sin Retorno','Aportes',0],
['Beneficios Entregados - Prestamos','Prestamo Auxilio General',0],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Medico',0],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Combinado',0],
['Beneficios Entregados - Prestamos','Prestamo Auxilio Especial',0],
['Cuotas Federacion','Cuotas Federacion',0],
['Conmemoración Giannina Barahona','Conmemoración Giannina Barahona',0],
['Conmemoración Dia de la Mujer','Conmemoración Dia de la Mujer',0],
['Conmemoración 1 de Mayo','Conmemoración 1 de Mayo',0],
['Campeonato Copa Sindicato Unificado','Campeonato Copa Sindicato Unificado',0],
['Fiestas Patrias','Fiestas Patrias',0],
['Aniversario','Aniversario',0],
['Tocata','Tocata',0],
['Navidad','Navidad',0],
['Despedida por Retiros','Despedida por Retiros',0],
['Seminario/Capacitacion','Seminario/Capacitacion',0],
['Seminario Salud Laboral','Seminario Salud Laboral',0],
['Aportes Actividades Socios','Fiestas Patrias',0],
['Aportes Actividades Socios','Fin de Año',0],
['Aportes Actividades Socios','Especiales',0],
['Gastos Bancarios','Gastos Bancarios',0],
['Gastos Eventos y Reuniones (Asambleas)','Gastos Eventos y Reuniones (Asambleas)',0],
['Gastos Representacion y Otros','Gastos Representacion y Otros',0],
['Gastos Oficina (Alimentacion)','Gastos Oficina (Alimentacion)',0],
['Patrimonio','Patrimonio',0],
['Conservacion Patrimonio','Conservacion Patrimonio',0],
['Biblioteca Sindical','Biblioteca Sindical',0],
['Software Contable','Software Contable',0],
['Pre Universitario','Pre Universitario',0],
['Imprevistos','Imprevistos',0],
]

print('populating saldos')

id = 0

for i in saldos:
    id = id+1
    obj = Item.objects.get(id=id)
    saldo = Saldo.objects.get_or_create(item_linked=obj,item=i[0],subitem=i[1],monto=i[2],estado='Vigente',user_creacion='167458262')

print('populating saldos completed')
