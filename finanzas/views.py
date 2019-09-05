from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import CreateView
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import StreamingHttpResponse

from .models import IngresoEgreso
from .forms import IngresoEgresoForm, MovimientoEditForm, PresupuestoForm, CierreForm, DesdeHastaForm, MovimientoViewForm, MovimientoEditFullForm
from socios.models import KerSocioRol
from finanzas.models import Item,Saldo,IngresoEgreso,LogMovimientos
import datetime
from django.utils import timezone
import xlwt
import xlsxwriter
import io
from django.forms import modelformset_factory
from calendar import monthrange

from django.template import Context, Template, loader
from django.template.loader import get_template

from xhtml2pdf import pisa
from django import forms
# Create your views here.
@login_required
def ingreso_egreso_create_view(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Finanzas':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    if request.method == 'POST':
        ingresoegreso_form = IngresoEgresoForm(request.POST,request.FILES)
        if ingresoegreso_form.is_valid():
            # Logica para separar item y subitem
            ingresoegreso = ingresoegreso_form.save(commit=False)
            str_item = ingresoegreso.item_linked.__str__().split(' - ')

            # Logica para generar autosecuencia para el folio
            month = ingresoegreso.fecha.strftime("%m")
            if int(month) < 10:
                month = month.replace("0","")
            obj = IngresoEgreso.objects.filter(fecha__month=month).order_by('-folio').first()
            if obj:
                next = obj.folio + 1
                ingresoegreso.folio = next
            else:
                ingresoegreso.folio = int(ingresoegreso.fecha.strftime("%Y%m0001"))

            # ingresoegreso.folio = ingresoegreso.fecha.strftime("%Y%m") + next
            ingresoegreso.item = str_item[0]
            ingresoegreso.subitem = str_item[1]
            ingresoegreso.socio = request.user
            ingresoegreso.estado = 'Ingresado'
            ingresoegreso.user_creacion = request.user.username
            ingresoegreso.fec_creacion = datetime.datetime.now()
            ingresoegreso.save()
            # # Se suma o resta del saldo
            # saldo = Saldo.objects.get(item=ingresoegreso.item,subitem=ingresoegreso.subitem)
            # asienta_ingresoegreso(saldo,ingresoegreso.tipo_mov,ingresoegreso.monto,request.user.username)

            # Generar la caratula en excel, guardarla en la ruta y que aparezca el pop-up para descargar
            output = io.BytesIO()
            nombre_archivo = 'Caratula_' + str(ingresoegreso.folio) + '_' + ingresoegreso.fecha.strftime("%Y%m%d") + '.xlsx'
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Hoja1')
            row = 0
            col = 0

            worksheet.insert_image('E2', 'static/images/logosut.png',{'x_scale': 0.2, 'y_scale': 0.2})

            merge_format = workbook.add_format({'align': 'center'})
            worksheet.merge_range('A9:J9', 'Sindicato Unificado de Trabajadores, Operaciones y Servicios Metro S.A', merge_format)
            merge_format = workbook.add_format({
                'align': 'center',
                'bold': True,
            })
            worksheet.merge_range('A10:J10','AÑO ' + ingresoegreso.fecha.strftime("%Y") , merge_format)
            worksheet.merge_range('A11:J11','REGISTRO DE EGRESO SUT - FOLIO ' + str(ingresoegreso.folio) , merge_format)

            merge_format = workbook.add_format({
                'align': 'center',
                'border':   True,
            })

            merge_format2 = workbook.add_format({
                'align': 'center',
                'border':   True,
                'bold': True,
            })

            full_border = workbook.add_format({
                'border':   1,
            })

            currency_format = workbook.add_format({
                'align': 'center',
                'num_format': '$ #,##0',
                'border':   True,
            })

            worksheet.write('A13', 'Fecha',full_border)
            worksheet.merge_range('B13:J13',ingresoegreso.fecha.strftime("%d-%m-%Y") , merge_format)
            worksheet.write('A14', 'Cuenta',full_border)
            worksheet.merge_range('B14:J14','Sindicato Unificado de Trabajadores, Operaciones y Servicios Metro S.A' , merge_format)
            worksheet.write('A15', 'Pagado a',full_border)
            worksheet.merge_range('B15:J15','Fondo por rendir a Daniel Salvatierra' , merge_format2)
            worksheet.write('A16', 'Cheque',full_border)
            if ingresoegreso.num_cheque:
                worksheet.merge_range('B16:J16',ingresoegreso.num_cheque , merge_format)
            else:
                worksheet.merge_range('B16:J16','' , merge_format)
            worksheet.write('A17', 'Monto',full_border)
            worksheet.merge_range('B17:J17',ingresoegreso.monto , currency_format)
            worksheet.write('A18', 'Banco',full_border)
            worksheet.merge_range('B18:J18','Scotiabank' , merge_format)
            worksheet.merge_range('A19:J19','DETALLE' , workbook.add_format({'align': 'center'}))

            merge_format2 = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border':   True,
            })

            currency_format = workbook.add_format({
                'num_format': '$ #,##0',
                'border':   True,
            })

            worksheet.merge_range('A20:I27','Cheque por fondo por Rendir para Gastos Sindicales.' , merge_format2)
            worksheet.merge_range('A28:I28','Total' , workbook.add_format({'align': 'lef','border':   True,}))
            worksheet.write('J20', '',full_border)
            worksheet.write('J21', '',full_border)
            worksheet.write('J22', '',full_border)
            worksheet.write('J23', '',full_border)
            worksheet.write('J24', '',full_border)
            worksheet.write('J25', '',full_border)
            worksheet.write('J26', '',full_border)
            worksheet.write('J27', '',full_border)
            worksheet.write('J28', ingresoegreso.monto,currency_format)

            currency_format = workbook.add_format({
                'num_format': '$ #,##0',
                'border':   True,
            })

            format_left = workbook.add_format({
                'align': 'center',
                'border':   True,
            })

            worksheet.merge_range('A28:I28','Total', format_left)

            merge_format = workbook.add_format({
                'align': 'center',
                'bold': True,
            })

            worksheet.merge_range('A29:J29','Recibo Conforme',merge_format)

            merge_format = workbook.add_format({
                'align': 'left',
                'border':   True,
            })

            worksheet.merge_range('A30:J30','Nombre: ',merge_format)
            worksheet.merge_range('A31:B31','Rut: ',merge_format)
            worksheet.merge_range('A32:B32','Cargo: ',merge_format)

            merge_format = workbook.add_format({
                'align': 'center',
                'border':   True,
            })
            worksheet.merge_range('C31:J32','Firma --------------------------------------',merge_format)

            merge_format = workbook.add_format({
                'align': 'center',
                'border':   True,
                'text_wrap': 1,
                'bold':True
            })
            worksheet.merge_range('A34:B35','V°B° Presidente',merge_format)
            worksheet.merge_range('C34:D35','V°B° Tesorero',merge_format)
            worksheet.merge_range('E34:H35','V°B° Contador',merge_format)
            worksheet.merge_range('I34:J35','V°B° Comision',merge_format)

            worksheet.merge_range('A36:B40',None,merge_format)
            worksheet.merge_range('C36:D40',None,merge_format)
            worksheet.merge_range('E36:H40',None,merge_format)
            worksheet.merge_range('I36:J40',None,merge_format)

            workbook.close()
            output.seek(0)

            response = StreamingHttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=' + nombre_archivo

            # ingresoegreso.caratula = response
            #
            # ingresoegreso.save()

            messages.success(request,'Se ha ingresado el movimiento correctamente')

            context = {
                'ingresoegreso_form':ingresoegreso_form,
                'roles':roles,
            }
            return response
            # return render(request,'finanzas/ingresoegreso_create.html',context)
        else:
            context = {
                'ingresoegreso_form':ingresoegreso_form,
                'roles':roles,
            }
            return render(request,'finanzas/ingresoegreso_create.html',context)
    else:
        ingresoegreso_form = IngresoEgresoForm()
        context = {
            'ingresoegreso_form':ingresoegreso_form,
            'roles':roles
        }
        return render(request,'finanzas/ingresoegreso_create.html',context)

def lista_ingreso_egreso(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Finanzas':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    movimientos = IngresoEgreso.objects.all().order_by('-fecha')

    if request.method == 'POST':
        form = DesdeHastaForm(request.POST)
        if form.is_valid():
            ind_range = False
            if form.cleaned_data['desde'] and form.cleaned_data['hasta']:
                desde = form.cleaned_data['desde']
                hasta = form.cleaned_data['hasta']
                # format_str = '%d/%m/%Y' # The format
                # desde = datetime.datetime.strptime(desde, format_str)
                # hasta = datetime.datetime.strptime(hasta, format_str)
                ind_range = True
            tipo = form.cleaned_data['tipo']
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if tipo == "Excel":
                # Generacion de Excel
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Movimientos_' + stamp + '.xls"'
                # response['Content-Disposition'] = 'attachment; filename="Movimientos.xlsx"'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Movimientos')

                row_num = 0
                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Folio','Fecha','Item', 'Subitem', 'Tipo', 'Monto', 'N° Cheque',
                    'N° Boletaa/Factura','Nombre Proveedor','Rut Asociado','Estado','Comentario']

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                if ind_range:
                    rows = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')
                else:
                    rows = IngresoEgreso.objects.all().order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')

                for row in rows:
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
                wb.save(response)

                return response
            else:
                # Generacion de PDF
                template = loader.get_template('movimientos.html')
                #template = Template("My name is {{ my_name }}.")
                if ind_range:
                    movimientos = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('folio')
                else:
                    movimientos = IngresoEgreso.objects.all().order_by('folio')

                context = {
                    'movimientos':movimientos,

                }
                html  = template.render(context)
                html2 = ""

                for mov in movimientos:
                    html2 = html2 + "<tr>"
                    html2 = html2 + "<td align='center'>" + str(mov.folio) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.fecha) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.item) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.subitem) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.tipo_mov) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.monto) + "</td>"
                    if mov.num_cheque:
                        html2 = html2 + "<td align='center'>" + str(mov.num_cheque) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.num_boleta_factura:
                        html2 = html2 + "<td align='center'>" + str(mov.num_boleta_factura) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.nombre_proveedor:
                        html2 = html2 + "<td align='center'>" + str(mov.nombre_proveedor) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.rut_socio_asociado:
                        html2 = html2 + "<td align='center'>" + str(mov.rut_socio_asociado) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "<td align='center'>" + str(mov.estado) + "</td>"
                    if mov.comentario:
                        html2 = html2 + "<td align='center'>" + str(mov.comentario) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "</tr>"
                html2 = html2+"</tbody></table>"
                html = html + html2


                file = open('Movimientos_' + stamp + '.pdf', "w+b")
                pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                        encoding='utf-8')

                file.seek(0)
                pdf = file.read()
                file.close()
                return HttpResponse(pdf, 'application/pdf')
        # else:
        #     # messages.info(request,form.errors)
    else:
        form = DesdeHastaForm()

    context = {
        'movimientos':movimientos,
        'roles':roles,
        'form':form,
    }
    return render(request, 'finanzas/list_ingreso_egreso.html', context)

def lista_saldos(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Finanzas':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    saldos = Saldo.objects.filter(estado='Vigente').order_by('item','subitem')
    context = {
        'saldos':saldos,
        'roles':roles,
    }
    return render(request, 'finanzas/list_saldos.html', context)

def lista_pendientes(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Aprobador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    pendientes = IngresoEgreso.objects.filter(socio=request.user).exclude(est_aprob=True)
    context = {
        'pendientes':pendientes,
        'roles':roles,
    }
    return render(request, 'finanzas/list_pendientes.html', context)

def aprobar_pendientes(request,pk):

    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')

    mov = IngresoEgreso.objects.get(pk=pk)
    mov.est_aprob = True
    # Aqui se debe agregar la logica para modificar los saldos
    # llamando a asienta_ingresoegreso()
    mov.save()
    return redirect('finanzas:pendientes')

def asienta_ingresoegreso(obj,tipo_mov,monto,username):
    if tipo_mov == 'Ingreso':
        obj.monto = obj.monto + monto
        obj.fec_ult_modif = datetime.datetime.now()
        obj.user_ult_modif = username
        obj.save()
    else:
        obj.monto = obj.monto - monto
        obj.fec_ult_modif = datetime.datetime.now()
        obj.user_ult_modif = username
        obj.save()

@login_required
def list_log_finanzas(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Historial':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    movimientos = LogMovimientos.objects.all().order_by('-fec_operacion')

    context = {
        'movimientos':movimientos,
        'roles':roles
    }
    return render(request, 'finanzas/list_log_finanzas.html', context)

def export_saldos_xls(request):
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Saldos_' + stamp + '.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Saldos')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Item', 'Subitem', 'Monto', 'Estado']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    rows = Saldo.objects.filter(estado='Vigente').order_by('item','subitem').values_list('item', 'subitem', 'monto', 'estado')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)

    return response

def export_saldos_pdf(request):
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    template = loader.get_template('saldos.html')
    #template = Template("My name is {{ my_name }}.")
    saldos = Saldo.objects.filter(estado='Vigente').order_by('item','subitem')
    context = {
        'saldos':saldos,

    }
    html  = template.render(context)
    html2 = ""

    for sal in saldos:
        html2 = html2 + "<tr>"
        html2 = html2 + "<td align='center'>" + str(sal.item) + "</td>"
        html2 = html2 + "<td align='center'>" + str(sal.subitem) + "</td>"
        html2 = html2 + "<td align='center'>" + str(sal.monto) + "</td>"
        html2 = html2 + "<td align='center'>" + str(sal.estado) + "</td>"
        html2 = html2 + "</tr>"
    html2 = html2+"</tbody></table>"
    html = html + html2


    file = open('Saldos_' + stamp + '.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

def export_movimientos_xls(request):

    if request.method == 'POST':
        form = DesdeHastaForm(request.POST)
        if form.is_valid():
            ind_range = False
            if form.cleaned_data['desde'] and form.cleaned_data['hasta']:
                desde = form.cleaned_data['desde']
                hasta = form.cleaned_data['hasta']
                # format_str = '%d/%m/%Y' # The format
                # desde = datetime.datetime.strptime(desde, format_str)
                # hasta = datetime.datetime.strptime(hasta, format_str)
                ind_range = True
            tipo = form.cleaned_data['tipo']
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if tipo == "Excel":
                # Generacion de Excel
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Movimientos_' + stamp + '.xls"'
                # response['Content-Disposition'] = 'attachment; filename="Movimientos.xlsx"'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Movimientos')

                row_num = 0
                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Folio','Fecha','Item', 'Subitem', 'Tipo', 'Monto', 'N° Cheque',
                    'N° Boletaa/Factura','Nombre Proveedor','Rut Asociado','Estado','Comentario']

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                if ind_range:
                    rows = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')
                else:
                    rows = IngresoEgreso.objects.all().order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')

                for row in rows:
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
                wb.save(response)

                return response
            else:
                # Generacion de PDF
                template = loader.get_template('movimientos.html')
                #template = Template("My name is {{ my_name }}.")
                if ind_range:
                    movimientos = IngresoEgreso.objects.filter(fecha__range=(desde, hasta)).order_by('folio')
                else:
                    movimientos = IngresoEgreso.objects.all().order_by('folio')

                context = {
                    'movimientos':movimientos,

                }
                html  = template.render(context)
                html2 = ""

                for mov in movimientos:
                    html2 = html2 + "<tr>"
                    html2 = html2 + "<td align='center'>" + str(mov.folio) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.fecha) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.item) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.subitem) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.tipo_mov) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.monto) + "</td>"
                    if mov.num_cheque:
                        html2 = html2 + "<td align='center'>" + str(mov.num_cheque) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.num_boleta_factura:
                        html2 = html2 + "<td align='center'>" + str(mov.num_boleta_factura) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.nombre_proveedor:
                        html2 = html2 + "<td align='center'>" + str(mov.nombre_proveedor) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.rut_socio_asociado:
                        html2 = html2 + "<td align='center'>" + str(mov.rut_socio_asociado) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "<td align='center'>" + str(mov.estado) + "</td>"
                    if mov.comentario:
                        html2 = html2 + "<td align='center'>" + str(mov.comentario) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "</tr>"
                html2 = html2+"</tbody></table>"
                html = html + html2


                file = open('Movimientos_' + stamp + '.pdf', "w+b")
                pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                        encoding='utf-8')

                file.seek(0)
                pdf = file.read()
                file.close()
                return HttpResponse(pdf, 'application/pdf')
        # else:
        #     messages.info(request,form.errors)
        #     return redirect(reverse('finanzas:movimientos'))
    else:
        form = DesdeHastaForm()

def export_movimientos_pdf(request):

    template = loader.get_template('movimientos.html')
    #template = Template("My name is {{ my_name }}.")
    movimientos = IngresoEgreso.objects.all().order_by('-fecha').values_list('num_documento','rut_asociado', 'item', 'subitem', 'tipo_mov', 'monto', 'rut_aprob_id', 'est_aprob')

    #print(saldos)
    context = {
        'movimientos':movimientos,

    }
    html  = template.render(context)

    for mov in movimientos:
        messages.debug(request,mov)
        # messages.debug(request,mov.num_documento)
        # if mov.est_aprob is None:
        #     mov.est_aprob = False

    for mov in movimientos:
        html2 = "<tr><td align='center'>"+ str(mov[0])+" </td><td align='center'>"+mov[1]+"</td><td align='center'>"+mov[2]+"</td><td align='center'>"+mov[3]+"</td><td align='center'>"+str(mov[4])+"</td><td align='center'>"+str(mov[5])+"</td><td align='center'>"+str(mov[6])+"</td><td align='center'>"+str(mov[7])+"</td></tr>"
    html2 = html2+"</tbody></table>"
    html = html + html2


    file = open('movimientos.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')
#     return render(request,'finanzas/subitems_dropdowm_list.html',{'subitems':subitems})

@login_required
def lista_movimientos(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    movimientos = IngresoEgreso.objects.exclude(estado='Cerrado').order_by('-fecha')
    context = {
        'movimientos':movimientos,
        'roles':roles,
    }
    return render(request, 'finanzas/list_movimientos.html', context)

@login_required
def edit_movimiento(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    movimiento = IngresoEgreso.objects.get(pk=pk)

    if movimiento.fecha:
        movimiento.fecha = movimiento.fecha.strftime("%d/%m/%Y")

    if request.method == 'POST':
        mov_form = MovimientoEditForm(request.POST,instance=movimiento)
        if mov_form.is_valid():
            mov = mov_form.save(commit=False)
            str_item = mov.item_linked.__str__().split(' - ')
            mov.item = str_item[0]
            mov.subitem = str_item[1]
            mov.user_ult_modif = request.user.username
            mov.fec_ult_modif = datetime.datetime.now()
            mov.save()

            if 'adjunto' in request.FILES:
                mov.adjunto = request.FILES['adjunto']
                mov.save()

            if 'voucher' in request.FILES:
                mov.voucher = request.FILES['voucher']
                mov.save()

            if 'caratula' in request.FILES:
                mov.caratula = request.FILES['caratula']
                mov.save()

            messages.success(request, 'Su ha actualizado el movimiento!')
        else:
            print(mov_form.errors)
    else:
        # movimiento.item = movimiento.item + ' - ' + movimiento.subitem
        mov_form = MovimientoEditForm(instance=movimiento)

    context = {
        'mov_form':mov_form,
        'roles':roles,
        'pk':movimiento.pk,
    }
    return render(request,'finanzas/update_movimiento.html',context)

@login_required
def add_presupuesto_masivo(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    SaldoFormSet = modelformset_factory(Saldo,form=PresupuestoForm,fields=('item_linked','monto'),extra=0)

    if request.method == 'POST':
        formset = SaldoFormSet(request.POST)
        if formset.is_valid():
            instance = formset.save()

            messages.success(request, 'Su ha actualizado el Presupuesto!')
        else:
            print(formset.errors)
            messages.info(request, formset.errors)
    else:
        formset = SaldoFormSet()

    context = {
        'formset':formset,
        'roles':roles,
    }
    return render(request,'finanzas/add_presupuesto_masivo.html',context)

@login_required
def cerrar_mes(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    if request.method == 'POST':
        form = CierreForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            mes = datetime.datetime.strptime(form.cleaned_data['mes'],"%Y-%m-%d")
            mes = mes.strftime("%m-%Y")
            ini_mes = datetime.datetime.strptime(form.cleaned_data['mes'],"%Y-%m-%d").replace(day=1)
            cant_dias_mes = monthrange(ini_mes.year,ini_mes.month)
            fin_mes = datetime.datetime.strptime(form.cleaned_data['mes'],"%Y-%m-%d").replace(day=cant_dias_mes[1])
            pendientes = IngresoEgreso.objects.filter(fecha__range=(ini_mes,fin_mes)).exclude(estado="Cerrado")
            # messages.debug(request,'ini_mes: ' + ini_mes)
            # messages.debug(request,'cant_dias_mes: ' + cant_dias_mes[1])
            # messages.debug(request,'fin_mes: ' + fin_mes)
            # messages.debug(request,'PENDIENTES: ' + pendientes)
            for pen in pendientes:
                pen.estado = 'Cerrado'
                pen.fec_ult_modif = datetime.datetime.now()
                pen.user_ult_modif = request.user.username
                pen.save()
            messages.success(request,"Se han cerrado todos los movimientos del periodo: " + mes)
        else:
            form = CierreForm()
    else:
        form = CierreForm()

    context = {
        'form':form,
        'roles':roles,
    }
    return render(request,'finanzas/cerrar_mes.html',context)

def export_movimientos(request):

    if request.method == 'POST':
        form = DesdeHastaForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['desde']:
                desde = form.cleaned_data['desde']
            if form.cleaned_data['hasta']:
                hasta = form.cleaned_data['desde']
            tipo = form.cleaned_data['tipo']
            if tipo == "Excel":
                # Generacion de Excel
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Movimientos.xls"'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Movimientos')

                row_num = 0
                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Folio','Fecha','Item', 'Subitem', 'Tipo', 'Monto', 'N° Cheque',
                    'N° Boletaa/Factura','Nombre Proveedor','Rut Asociado','Estado','Comentario']

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                if desde and hasta:
                    rows = IngresoEgreso.objects.all().order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')
                else:
                    rows = IngresoEgreso.objects.all().order_by('-fecha').values_list('folio',
                        'fecha','item','subitem','tipo_mov','monto','num_cheque','num_boleta_factura',
                        'nombre_proveedor','rut_socio_asociado','estado','comentario')

                for row in rows:
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
                wb.save(response)

                return response
            else:
                # Generacion de PDF
                template = loader.get_template('movimientos.html')
                #template = Template("My name is {{ my_name }}.")
                movimientos = IngresoEgreso.objects.all().order_by('folio')

                context = {
                    'movimientos':movimientos,

                }
                html  = template.render(context)
                html2 = ""

                for mov in movimientos:
                    html2 = html2 + "<tr>"
                    html2 = html2 + "<td align='center'>" + str(mov.folio) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.fecha) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.item) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.subitem) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.tipo_mov) + "</td>"
                    html2 = html2 + "<td align='center'>" + str(mov.monto) + "</td>"
                    if mov.num_cheque:
                        html2 = html2 + "<td align='center'>" + str(mov.num_cheque) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.num_boleta_factura:
                        html2 = html2 + "<td align='center'>" + str(mov.num_boleta_factura) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.nombre_proveedor:
                        html2 = html2 + "<td align='center'>" + str(mov.nombre_proveedor) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    if mov.rut_socio_asociado:
                        html2 = html2 + "<td align='center'>" + str(mov.rut_socio_asociado) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "<td align='center'>" + str(mov.estado) + "</td>"
                    if mov.comentario:
                        html2 = html2 + "<td align='center'>" + str(mov.comentario) + "</td>"
                    else:
                        html2 = html2 + "<td align='center'></td>"
                    html2 = html2 + "</tr>"
                html2 = html2+"</tbody></table>"
                html = html + html2


                file = open('movimientos.pdf', "w+b")
                pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                        encoding='utf-8')

                file.seek(0)
                pdf = file.read()
                file.close()
                return HttpResponse(pdf, 'application/pdf')
        else:
            messages.info(request,form.errors)
    else:
        form = DesdeHastaForm()

def lista_movimientos_socios(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')

    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    movimientos = IngresoEgreso.objects.all().order_by('-fecha')

    context = {
        'movimientos':movimientos,
        'roles':roles,
        # 'form':form,
    }
    return render(request, 'finanzas/list_movimientos_socios.html', context)

@login_required
def delete_movimiento(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Finanzas':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    if request.method == 'POST':
        mov = IngresoEgreso.objects.get(pk=pk)
        mov.delete()
        return HttpResponseRedirect(reverse('finanzas:movimientos_edit'))
    else:
        mov = IngresoEgreso.objects.get(pk=pk)

    context = {
        'mov':mov,
        'roles':roles,
    }
    return render(request,'finanzas/delete_movimiento.html',context)

@login_required
def view_movimiento(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    movimiento = IngresoEgreso.objects.get(pk=pk)

    if movimiento.fecha:
        movimiento.fecha = movimiento.fecha.strftime("%d/%m/%Y")

    if request.method == 'POST':
        str_item = movimiento.item_linked.__str__().split(' - ')
        mov_form = MovimientoViewForm(request.POST,instance=movimiento)
        if mov_form.is_valid():
            mov = mov_form.save(commit=False)
            mov.item = str_item[0]
            mov.subitem = str_item[1]
            mov.user_ult_modif = request.user.username
            mov.fec_ult_modif = datetime.datetime.now()
            mov.save()

            if 'adjunto' in request.FILES:
                mov.adjunto = request.FILES['adjunto']
                mov.save()

            if 'voucher' in request.FILES:
                mov.voucher = request.FILES['voucher']
                mov.save()

            if 'caratula' in request.FILES:
                mov.caratula = request.FILES['caratula']
                mov.save()

            messages.success(request, 'Su ha actualizado el movimiento!')
        else:
            print(mov_form.errors)
    else:
        # movimiento.item = movimiento.item + ' - ' + movimiento.subitem
        mov_form = MovimientoViewForm(instance=movimiento)

    context = {
        'mov_form':mov_form,
        'roles':roles,
        'pk':movimiento.pk,
    }
    return render(request,'finanzas/view_movimiento.html',context)

@login_required
def edit_movimiento_full(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Contador':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    movimiento = IngresoEgreso.objects.get(pk=pk)

    if movimiento.fecha:
        movimiento.fecha = movimiento.fecha.strftime("%d/%m/%Y")

    if request.method == 'POST':
        str_item = movimiento.item_linked.__str__().split(' - ')
        mov_form = MovimientoEditFullForm(request.POST,instance=movimiento)
        if mov_form.is_valid():
            mov = mov_form.save(commit=False)
            mov.item = str_item[0]
            mov.subitem = str_item[1]
            mov.user_ult_modif = request.user.username
            mov.fec_ult_modif = datetime.datetime.now()
            mov.save()

            if 'adjunto' in request.FILES:
                mov.adjunto = request.FILES['adjunto']
                mov.save()

            if 'voucher' in request.FILES:
                mov.voucher = request.FILES['voucher']
                mov.save()

            if 'caratula' in request.FILES:
                mov.caratula = request.FILES['caratula']
                mov.save()

            messages.success(request, 'Su ha actualizado el movimiento!')
        else:
            print(mov_form.errors)
    else:
        # movimiento.item = movimiento.item + ' - ' + movimiento.subitem
        mov_form = MovimientoEditFullForm(instance=movimiento)

    context = {
        'mov_form':mov_form,
        'roles':roles,
        'pk':movimiento.pk,
    }
    return render(request,'finanzas/update_movimiento_full.html',context)
