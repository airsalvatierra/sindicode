import csv
import boto3
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.decorators import login_required

from asistencias.forms import AsistenciaEncForm, AsistenciaDetForm,AsistenciaDetCEForm,AsistenciaEncFormCE
from asistencias.models import AsistenciaEnc, AsistenciaDet, Asistentes
from socios.models import User,KerSocioRol
from django.core.mail import send_mail

from django.views.generic import ListView, UpdateView
import xlwt
from django.template import Context, Template, loader
from django.template.loader import get_template
import datetime
from django.utils import timezone
from xhtml2pdf import pisa
from django import forms

# Create your views here.
@login_required
def crear_asistencia(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Asistencia':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    ############################################################################
    asistenciaenc_form = AsistenciaEncForm()
    # messages.info(request, 'Funcionando!')
    print('Funcionando!')
    if KerSocioRol.objects.filter(socio=request.user).exists():
        if request.method == 'POST':
            # leer el archivo con los ruts que asistieron y guardarlo en variable CSV
            for upfile in request.FILES.getlist('archivo'):
                csv_reader = csv.reader(upfile.read().decode('utf-8').splitlines())
                asistenciaenc_form = AsistenciaEncForm(request.POST,request.FILES)
                if asistenciaenc_form.is_valid():
                    asistencia = asistenciaenc_form.save()
                    # Usar el usuario conectado para grabar el encabezado
                    asistencia.usuario = request.user.username
                    asistencia.save()
                    # Verificar que tipo de Asamblea es, si es General Ordinaria,
                    # General Extraordinaria o de Votación se deben usar todos los socios
                    # si no se deben usar solo los que diga el excel
                    print("Tipo de asistencia: " + asistencia.tipo_evento)
                    if asistencia.tipo_evento == "Asamblea General Ordinaria" or asistencia.tipo_evento == "Asamblea General Extraordinaria" or asistencia.tipo_evento == "Asamblea de Votación":
                        # Guardar temporalmente los rut del csv a una tabla
                        for line in csv_reader:
                            rut = str.strip(line[0].replace('\n', '').replace('\r', ''))
                            asistente = Asistentes()
                            asistente.folio = asistencia.pk
                            asistente.rut_socio = rut
                            asistente.save()
                        # Traer todos los socios activos para verificar la asistencia
                        socios_activos = User.objects.filter(estado_socio='Vigente')
                        # Crear un registros para cada usuario activo en el detalle de la asistencia
                        for socio in socios_activos:
                            asistencia_det = AsistenciaDet()
                            asistencia_det.asistenciaenc = asistencia
                            asistencia_det.fec_evento = asistencia.fec_evento
                            asistencia_det.rut_socio = socio.username
                            asistencia_det.email = socio.email
                            asistencia_det.nombre = socio.first_name
                            asistencia_det.apellido = socio.last_name
                            asistencia_det.save()
                        # Traer todos los registros creados en el detalle de esta asistencia
                        detalle_asis = AsistenciaDet.objects.filter(asistenciaenc=asistencia)
                        # print('marcando asistencia')
                        for det in detalle_asis:
                            # Traer los asistentes de la tabla temporal
                            asistentes = Asistentes.objects.all()
                            for line in asistentes:
                                # buscar el registro del detalle del rut del CSV
                                if det.rut_socio == line.rut_socio:
                                    detalle = AsistenciaDet.objects.get(asistenciaenc=asistencia,rut_socio=line.rut_socio)
                                    # messages.info(request, 'Asistio')
                                    # Si el indicador es verdadero (hizo match) se cuenta como
                                    # asistencia y se marca con Asistio, de lo contrario queda
                                    # como venia (No Asistio) y
                                    # se actualiza el registro con el indicador de asistencia
                                    detalle.est_asistencia = 'Asistio'
                                    detalle.save()
                    else:
                        print("archivo 2")
                        for line in csv_reader:
                            rut = str.strip(line[0].replace('\n', '').replace('\r', ''))
                            asis = str.strip(line[1].replace('\n', '').replace('\r', ''))
                            print("Rut: " + rut)
                            print("Asis: " + asis)
                            asistente = Asistentes()
                            asistente.folio = asistencia.pk
                            asistente.rut_socio = rut
                            asistente.est_asistencia = asis
                            asistente.save()
                        # Traer los asistentes de la tabla temporal
                        socios_archivo = Asistentes.objects.all()
                        # Crear un registros para cada usuario del archivo en el detalle de la asistencia
                        for soc in socios_archivo:
                            socio = User.objects.get(username=soc.rut_socio.upper())
                            asistencia_det = AsistenciaDet()
                            asistencia_det.asistenciaenc = asistencia
                            asistencia_det.fec_evento = asistencia.fec_evento
                            asistencia_det.rut_socio = socio.username
                            asistencia_det.email = socio.email
                            asistencia_det.nombre = socio.first_name
                            asistencia_det.apellido = socio.last_name
                            if soc.est_asistencia.upper() == "SI":
                                asistencia_det.est_asistencia = 'Asistio'
                            asistencia_det.save()
                    # Despues de terminar el ciclo se calculan los totales del
                    # encabezado y se actualiza el encabezado
                    Asistentes.objects.all().delete()
                    print('calculando totaltes')
                    if  asistencia.tipo_evento != "Asamblea General Ordinaria" or asistencia.tipo_evento != "Asamblea General Extraordinaria" or asistencia.tipo_evento != "Asamblea de Votación":
                        # Traer todos los registros creados en el detalle de esta asistencia
                        detalle_asis = AsistenciaDet.objects.filter(asistenciaenc=asistencia)
                    asistencia.cant_total = detalle_asis.count()
                    asistencia.cant_asistencias = detalle_asis.filter(asistenciaenc=asistencia,est_asistencia='Asistio').count()
                    asistencia.cant_ausentes = detalle_asis.filter(asistenciaenc=asistencia,est_asistencia='No Asistio').count()
                    asistencia.save()
                    #Mandar correo a los inasistentes
                    inasistentes = AsistenciaDet.objects.filter(asistenciaenc=asistencia,est_asistencia='No Asistio')
                    # Plantilla de mensaje al sindicato sin los notificados
                    notificacion_al_sindicato = 'Estimados administradores del Sindicato:\n\nSe ha notificado la inasistencia a: %s - %s a los siguientes socios\n\n'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y"))
                    # Plantilla de notificacion al socio
                    mensaje = 'Estimado(a): Socio(a)\n\nMediante este correo se le notifica su inasistencia a %s - %s\n\nPuede presentar justificativo respondiendo y adjunto lo correspondiente a este correo\n\nSinceramente, Sindicato Unificado Metro'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y"))
                    # Se recorre a los inasistentes para rellenar el mensaje de correo al sindicato
                    for inasistente in inasistentes:
                        notificacion_al_sindicato = notificacion_al_sindicato + '%s %s - %s\n'%(inasistente.nombre,inasistente.apellido,inasistente.email)
                    # Enviar notificacion a los inasistentes
                    send_mail(
                        'Notificacion de Inasistencia a %s - %s'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y")),
                        mensaje,
                        'info.intrasut@gmail.com',
                        [ina.email for ina in inasistentes],
                        fail_silently=True,
                    )
                    # Se recorren los inasistentes y se marca la notificacion
                    for inasistente in inasistentes:
                        inasistente.est_notificacion = 'Notificado'
                        inasistente.save()
                    #Enviar correo de notificacion al sindicato indicando lo informado
                    send_mail(
                        'Generacion de Asistencia - %s - %s'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y")),
                        notificacion_al_sindicato,
                        'info.intrasut@gmail.com',
                        ['info.intrasut@gmail.com',]
                    )
                    messages.success(request, 'Proceso Terminado!')
            context = {
                'asistenciaenc_form':asistenciaenc_form,
                'roles':roles,
            }
            print('terminando proceso')
            return render(request,'asistencias/crear_asistencia.html',context)
        else:
            asistenciaenc_form = AsistenciaEncForm()
        context = {
            'asistenciaenc_form':asistenciaenc_form,
            'roles':roles,
        }
        return render(request,'asistencias/crear_asistencia.html',context)
    else:
        return render(request,'index.html',context)

class AsistenciaEncListView(LoginRequiredMixin,ListView):
    # template_name = 'asistencias/lista_asistencia.html'
    context_object_name = 'lista_asistencia'
    model = AsistenciaEnc

    # def get(self, request, *args, **kwargs):
    #     form = DesdeHastaForm()
    #
    # def post(self, request, *args, **kwargs):
    #     form = DesdeHastaForm(request.POST)
    #     if form.is_valid():
    #         ind_range = False
    #         if form.cleaned_data['desde'] and form.cleaned_data['hasta']:
    #             desde = form.cleaned_data['desde']
    #             hasta = form.cleaned_data['hasta']
    #             # format_str = '%d/%m/%Y' # The format
    #             # desde = datetime.datetime.strptime(desde, format_str)
    #             # hasta = datetime.datetime.strptime(hasta, format_str)
    #             ind_range = True
    #         tipo = form.cleaned_data['tipo']
    #         stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #         if tipo == "Excel":
    #             # Generacion de Excel
    #             response = HttpResponse(content_type='application/ms-excel')
    #             response['Content-Disposition'] = 'attachment; filename="Asistencias_' + stamp + '.xls"'
    #             # response['Content-Disposition'] = 'attachment; filename="Movimientos.xlsx"'
    #             wb = xlwt.Workbook(encoding='utf-8')
    #             ws = wb.add_sheet('Movimientos')
    #
    #             row_num = 0
    #             font_style = xlwt.XFStyle()
    #             font_style.font.bold = True
    #
    #             columns = ['Folio','Fecha','Item', 'Subitem', 'Tipo', 'Monto', 'N° Cheque',
    #                 'N° Boletaa/Factura','Nombre Proveedor','Rut Asociado','Estado','Comentario']
    #
    #             for col_num in range(len(columns)):
    #                 ws.write(row_num, col_num, columns[col_num], font_style)
    #
    #             if ind_range:
    #                 rows = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('-fecha').values_list('folio',
    #                     'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
    #                     'nombre_proveedor','rut_socio_asociado','estado','comentario')
    #             else:
    #                 rows = IngresoEgreso.objects.all().order_by('-fecha').values_list('folio',
    #                     'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
    #                     'nombre_proveedor','rut_socio_asociado','estado','comentario')
    #
    #             for row in rows:
    #                 row_num += 1
    #                 for col_num in range(len(row)):
    #                     ws.write(row_num, col_num, row[col_num], font_style)
    #             wb.save(response)
    #
    #             return response
    #         else:
    #             # Generacion de PDF
    #             template = loader.get_template('asistencias.html')
    #             #template = Template("My name is {{ my_name }}.")
    #             if ind_range:
    #                 movimientos = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('folio')
    #             else:
    #                 movimientos = IngresoEgreso.objects.all().order_by('folio')
    #
    #             context = {
    #                 'movimientos':movimientos,
    #
    #             }
    #             html  = template.render(context)
    #             html2 = ""
    #
    #             for mov in movimientos:
    #                 html2 = html2 + "<tr>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.folio) + "</td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.fecha) + "</td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.item) + "</td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.subitem) + "</td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.tipo_mov) + "</td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.monto) + "</td>"
    #                 if mov.num_cheque:
    #                     html2 = html2 + "<td align='center'>" + str(mov.num_cheque) + "</td>"
    #                 else:
    #                     html2 = html2 + "<td align='center'></td>"
    #                 if mov.num_boleta_factura:
    #                     html2 = html2 + "<td align='center'>" + str(mov.num_boleta_factura) + "</td>"
    #                 else:
    #                     html2 = html2 + "<td align='center'></td>"
    #                 if mov.nombre_proveedor:
    #                     html2 = html2 + "<td align='center'>" + str(mov.nombre_proveedor) + "</td>"
    #                 else:
    #                     html2 = html2 + "<td align='center'></td>"
    #                 if mov.rut_socio_asociado:
    #                     html2 = html2 + "<td align='center'>" + str(mov.rut_socio_asociado) + "</td>"
    #                 else:
    #                     html2 = html2 + "<td align='center'></td>"
    #                 html2 = html2 + "<td align='center'>" + str(mov.estado) + "</td>"
    #                 if mov.comentario:
    #                     html2 = html2 + "<td align='center'>" + str(mov.comentario) + "</td>"
    #                 else:
    #                     html2 = html2 + "<td align='center'></td>"
    #                 html2 = html2 + "</tr>"
    #             html2 = html2+"</tbody></table>"
    #             html = html + html2
    #
    #
    #             file = open('Movimientos_' + stamp + '.pdf', "w+b")
    #             pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
    #                     encoding='utf-8')
    #
    #             file.seek(0)
    #             pdf = file.read()
    #             file.close()
    #             return HttpResponse(pdf, 'application/pdf')

    def get_queryset(self):
        return AsistenciaEnc.objects.all().order_by('-pk')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

class AsistenciaDetListView(LoginRequiredMixin,ListView):
    # template_name = 'asistencias/asistencia_detalle.html'
    context_object_name = 'lista_detalle'
    model = AsistenciaDet

    def get_queryset(self):
        obj = AsistenciaEnc.objects.get(id=self.kwargs['pk'])
        return AsistenciaDet.objects.filter(asistenciaenc=obj)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

class AsistenciaDetUpdateView(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'asistencias/asistenciadet_edit.html'
    model = AsistenciaDet
    form_class = AsistenciaDetForm
    success_message = 'Se ha actualizado correctamente la asistencia'
    # fields = ['fec_evento','rut_socio','email','nombre','apellido',
    #         'est_asistencia','est_notificacion','comentario',
    #         'est_justificacion','arc_justificacion']

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

class AsistenciaEncListViewCE(LoginRequiredMixin,ListView):
    template_name = 'asistencias/asistenciaenc_list_CE.html'
    context_object_name = 'lista_asistencia'
    model = AsistenciaEnc

    def get_queryset(self):
        return AsistenciaEnc.objects.all().order_by('-pk')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

class AsistenciaDetListViewCE(LoginRequiredMixin,ListView):
    template_name = 'asistencias/asistenciadet_list_CE.html'
    context_object_name = 'lista_detalle'
    model = AsistenciaDet

    def get_queryset(self):
        obj = AsistenciaEnc.objects.get(id=self.kwargs['pk'])
        return AsistenciaDet.objects.filter(asistenciaenc=obj)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

class AsistenciaDetUpdateViewCE(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'asistencias/asistenciadet_edit_CE.html'
    model = AsistenciaDet
    form_class = AsistenciaDetCEForm
    success_message = 'Se ha actualizado correctamente el registro'
    # fields = ['fec_evento','rut_socio','email','nombre','apellido',
    #         'est_asistencia','est_notificacion','comentario',
    #         'est_justificacion','arc_justificacion']

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = KerSocioRol.objects.filter(socio=self.request.user).order_by('rol')
        return context

def export_asistencias_xls(request,pk):
    print('Prueba')
    # print('Prueba xls: ' + request.get)
    obj = AsistenciaEnc.objects.get(id=pk)
    print(obj)
    stamp = obj.tipo_evento + '_' + obj.fec_evento.strftime("%Y%m%d")

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Asistencia_' + stamp + '.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Asistencias')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Fec Evento','Socio','Nombre', 'Apellido', 'Email','Est. Asistencia',
        'Est. Notificacion','Est. Justificacion','Est. Apelacion','Comentario']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    rows = AsistenciaDet.objects.filter(asistenciaenc=obj).order_by('apellido').values_list('fec_evento',
        'rut_socio','nombre', 'apellido', 'email','est_asistencia','est_notificacion','est_justificacion','est_apelacion','comentario')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)

    return response

def export_asistencias_pdf(request,pk):
    print('Prueba')
    # print('Prueba pdf: ' + request.get)
    obj = AsistenciaEnc.objects.get(id=pk)
    stamp = obj.tipo_evento + '_' + obj.fec_evento.strftime("%Y%m%d")

    template = loader.get_template('asistencias.html')
    #template = Template("My name is {{ my_name }}.")
    asistencias = AsistenciaDet.objects.filter(asistenciaenc=obj).order_by('apellido')
    #print(saldos)
    context = {
        'asistencias':asistencias,

    }
    html  = template.render(context)
    html2 = ""

    for asi in asistencias:
        html2 = html2 + "<tr>"
        html2 = html2 + "<td align='center'>" + str(asi.fec_evento) + "</td>"
        html2 = html2 + "<td align='center'>" + str(asi.rut_socio) + "</td>"
        html2 = html2 + "<td align='center'>" + str(asi.nombre) + "</td>"
        html2 = html2 + "<td align='center'>" + str(asi.apellido) + "</td>"
        html2 = html2 + "<td align='center'>" + str(asi.email) + "</td>"
        html2 = html2 + "<td align='center'>" + str(asi.est_asistencia) + "</td>"
        if asi.est_notificacion:
            html2 = html2 + "<td align='center'>" + str(asi.est_notificacion) + "</td>"
        else:
            html2 = html2 + "<td align='center'></td>"
        if asi.est_justificacion:
            html2 = html2 + "<td align='center'>" + str(asi.est_notificacion) + "</td>"
        else:
            html2 = html2 + "<td align='center'></td>"
        if asi.est_apelacion:
            html2 = html2 + "<td align='center'>" + str(asi.est_apelacion) + "</td>"
        else:
            html2 = html2 + "<td align='center'></td>"
        if asi.comentario:
            html2 = html2 + "<td align='center'>" + str(asi.est_notificacion) + "</td>"
        else:
            html2 = html2 + "<td align='center'></td>"
        html2 = html2 + "</tr>"
    html2 = html2+"</tbody></table>"
    html = html + html2


    file = open('Asistencias_' + stamp + '.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required
def crear_asistencia_CE(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Asistencia':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    ############################################################################
    asistenciaenc_form = AsistenciaEncFormCE()
    # messages.info(request, 'Funcionando!')
    print('Funcionando!')
    if KerSocioRol.objects.filter(socio=request.user).exists():
        if request.method == 'POST':
            # leer el archivo con los ruts que asistieron y guardarlo en variable CSV
            for upfile in request.FILES.getlist('archivo'):
                csv_reader = csv.reader(upfile.read().decode('utf-8').splitlines())
                asistenciaenc_form = AsistenciaEncFormCE(request.POST,request.FILES)
                if asistenciaenc_form.is_valid():
                    asistencia = asistenciaenc_form.save()
                    # Usar el usuario conectado para grabar el encabezado
                    asistencia.usuario = request.user.username
                    asistencia.save()
                    # Guardar temporalmente los rut del csv a una tabla
                    for line in csv_reader:
                        rut = str.strip(line[0].replace('\n', '').replace('\r', ''))
                        asistente = Asistentes()
                        asistente.folio = asistencia.pk
                        asistente.rut_socio = rut
                        asistente.save()
                    # Traer todos los socios activos para verificar la asistencia
                    socios_activos = User.objects.filter(estado_socio='Vigente')
                    # Crear un registros para cada usuario activo en el detalle de la asistencia
                    for socio in socios_activos:
                        asistencia_det = AsistenciaDet()
                        asistencia_det.asistenciaenc = asistencia
                        asistencia_det.fec_evento = asistencia.fec_evento
                        asistencia_det.rut_socio = socio.username
                        asistencia_det.email = socio.email
                        asistencia_det.nombre = socio.first_name
                        asistencia_det.apellido = socio.last_name
                        asistencia_det.save()
                    # Traer todos los registros creados en el detalle de esta asistencia
                    detalle_asis = AsistenciaDet.objects.filter(asistenciaenc=asistencia)
                    # print('marcando asistencia')
                    for det in detalle_asis:
                        # Traer los asistentes de la tabla temporal
                        asistentes = Asistentes.objects.all()
                        for line in asistentes:
                            # buscar el registro del detalle del rut del CSV
                            if det.rut_socio == line.rut_socio:
                                detalle = AsistenciaDet.objects.get(asistenciaenc=asistencia,rut_socio=line.rut_socio)
                                # messages.info(request, 'Asistio')
                                # Si el indicador es verdadero (hizo match) se cuenta como
                                # asistencia y se marca con Asistio, de lo contrario queda
                                # como venia (No Asistio) y
                                # se actualiza el registro con el indicador de asistencia
                                detalle.est_asistencia = 'Asistio'
                                detalle.save()
                    # Despues de terminar el ciclo se calculan los totales del
                    # encabezado y se actualiza el encabezado
                    Asistentes.objects.all().delete()
                    print('calculando totaltes')
                    asistencia.cant_total = detalle_asis.count()
                    asistencia.cant_asistencias = detalle_asis.filter(asistenciaenc=asistencia,est_asistencia='Asistio').count()
                    asistencia.cant_ausentes = detalle_asis.filter(asistenciaenc=asistencia,est_asistencia='No Asistio').count()
                    asistencia.save()
                    #Mandar correo a los inasistentes
                    inasistentes = AsistenciaDet.objects.filter(asistenciaenc=asistencia,est_asistencia='No Asistio')
                    # Plantilla de mensaje al sindicato sin los notificados
                    notificacion_al_sindicato = 'Estimados administradores del Sindicato:\n\nSe ha notificado la inasistencia a: %s - %s a los siguientes socios\n\n'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y"))
                    # Plantilla de notificacion al socio
                    mensaje = 'Estimado(a): Socio(a)\n\nMediante este correo se le notifica su inasistencia a %s - %s\n\nPuede presentar justificativo respondiendo y adjunto lo correspondiente a este correo\n\nSinceramente, Sindicato Unificado Metro'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y"))
                    # Se recorre a los inasistentes para rellenar el mensaje de correo al sindicato
                    for inasistente in inasistentes:
                        notificacion_al_sindicato = notificacion_al_sindicato + '%s %s - %s\n'%(inasistente.nombre,inasistente.apellido,inasistente.email)
                    # Enviar notificacion a los inasistentes
                    # send_mail(
                    #     'Notificacion de Inasistencia a %s - %s'%(asistencia.tipo_evento,asistencia.fec_evento),
                    #     mensaje,
                    #     'info.intrasut@gmail.com',
                    #     [ina.email for ina in inasistentes],
                    #     fail_silently=True,
                    # )
                    # Se recorren los inasistentes y se marca la notificacion
                    for inasistente in inasistentes:
                        inasistente.est_notificacion = 'Notificado'
                        inasistente.save()
                    #Enviar correo de notificacion al sindicato indicando lo informado
                    send_mail(
                        'Generacion de Asistencia - %s - %s'%(asistencia.tipo_evento,asistencia.fec_evento.strftime("%d/%m/%Y")),
                        notificacion_al_sindicato,
                        'info.intrasut@gmail.com',
                        ['info.intrasut@gmail.com',]
                    )
                    messages.success(request, 'Proceso Terminado!')
            context = {
                'asistenciaenc_form':asistenciaenc_form,
                'roles':roles,
            }
            print('terminando proceso')
            return render(request,'asistencias/crear_asistencia.html',context)
        else:
            asistenciaenc_form = AsistenciaEncFormCE()
        context = {
            'asistenciaenc_form':asistenciaenc_form,
            'roles':roles,
        }
        return render(request,'asistencias/crear_asistencia_CE.html',context)
    else:
        return render(request,'index.html',context)
