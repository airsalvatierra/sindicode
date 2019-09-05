import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from socios.models import KerSocioRol
from datetime import datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

TIPOS_ESTADO = (
    ('Vigente','Vigente'),
    ('No Vigente','No Vigente')
)

TIPOS_ESTADO_MOV = (
    ('Ingresado','Ingresado'),
    ('Revisado','Revisado'),
    ('Cuadratura ','Cuadratura '),
    ('Cerrado','Cerrado'),
)

###############################################################################
# Upload Folders
def user_finanzas_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/eventos/username/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    now = datetime.now()
    month = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return 'finanzas/{month}/{basename}_{stamp}{ext}'.format(month=month,basename=basefilename,stamp=stamp,ext=file_extension)

def user_fin_caratula_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/eventos/username/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    now = datetime.now()
    month = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return 'finanzas/caratulas/{month}/{basename}_{stamp}{ext}'.format(month=month,basename=basefilename,stamp=stamp,ext=file_extension)

###############################################################################

class Item(models.Model):
    nombre = models.CharField(max_length=200)
    item = models.CharField(max_length=50)
    subitem = models.CharField(max_length=50)
    estado = models.CharField(max_length=50,choices=TIPOS_ESTADO,default='Vigente')
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.nombre

class Saldo(models.Model):
    item_linked = models.ForeignKey(Item,on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    subitem = models.CharField(max_length=100)
    monto = models.IntegerField()
    # fec_ano = models.CharField(max_length=100,null=True,blank=True)
    # year = models.CharField(max_length=4,null=True,blank=True)
    estado = models.CharField(max_length=50,choices=TIPOS_ESTADO,default='Vigente')
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return '{} - {}'.format(self.item,self.subitem)

class IngresoEgreso(models.Model):
    socio = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    folio = models.IntegerField() # Este debe ser autoincremental con la fecha del
    #año, mes y numero secuencial partiendo desde cero. AAAAMM+NUM_SECUENCIAL
    fecha = models.DateField()
    item_linked = models.ForeignKey(Item,on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    subitem = models.CharField(max_length=100)
    TIPOS_TIPO_MOV = (
        ('Ingreso','Ingreso'),
        ('Egreso','Egreso'),
    )
    tipo_mov = models.CharField(max_length=50,choices=TIPOS_TIPO_MOV)
    monto = models.IntegerField()
    num_cheque = models.IntegerField(null=True,blank=True)
    num_boleta_factura = models.IntegerField(null=True,blank=True)
    nombre_proveedor = models.CharField(max_length=200,null=True,blank=True)
    is_cheque = models.BooleanField(default=False)
    rut_socio_asociado = models.CharField(max_length=50,null=True,blank=True)
    estado = models.CharField(max_length=50,choices=TIPOS_ESTADO_MOV)
    adjunto = models.FileField(upload_to=user_finanzas_directory_path)
    voucher = models.FileField(upload_to=user_finanzas_directory_path,null=True,blank=True)
    comentario = models.CharField(max_length=500,null=True)
    caratula = models.FileField(upload_to=user_finanzas_directory_path,null=True,blank=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.folio,self.tipo_mov,self.monto)

@receiver(pre_save, sender=IngresoEgreso)
def movimiento_change(sender, instance, **kwargs):
    created = IngresoEgreso.objects.filter(pk=instance.id).count()

    if created == 0:
        log = LogMovimientos.objects.create(user_do=instance.user_creacion,folio=instance.folio,fec_operacion=datetime.now(),
            operacion='Se ha generado el movmiento con el Folio a ' + str(instance.folio))
    else:
        original = IngresoEgreso.objects.get(pk=instance.id)
        # 0) verificar si el movimiento original vs el nuevo es diferente en:
        # monto, item_linked o tipo_mov
        # 1) reversar el movimiento del presupuesto
        # 2) registrar en el log de presupuesto
        # 3) agregar/quitar del presupuesto el movimiento modificado
        # 4) registrar los cambios en el log de movimientos

        if (original.folio != instance.folio or original.fecha != instance.fecha or original.item_linked != instance.item_linked
            or original.item != instance.item or original.subitem != instance.subitem or original.tipo_mov != instance.tipo_mov
            or original.monto != instance.monto or original.num_cheque != instance.num_cheque or original.num_boleta_factura != instance.num_boleta_factura
            or original.nombre_proveedor != instance.nombre_proveedor or original.is_cheque != instance.is_cheque or original.rut_socio_asociado != instance.rut_socio_asociado
            or original.estado != instance.estado or original.adjunto != instance.adjunto or original.voucher != instance.voucher
            or original.comentario != instance.comentario or original.caratula != instance.caratula):
            # Registrar el cambio
            # folio
            if original.folio is None:
                if instance.folio is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Folio a ' + str(instance.folio))
            elif original.folio != instance.folio:
                if instance.folio is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Folio: ' + str(original.folio))
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Folio de " + str(original.folio) + " a " + str(instance.folio))
            # fecha:
            if original.fecha is None:
                if instance.fecha is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado la Fecha a ' + instance.fecha.strftime("%d/%m/%Y"))
            elif original.fecha != instance.fecha:
                if instance.fecha is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado la Fecha: ' + original.fecha.strftime("%d/%m/%Y"))
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado la Fecha de " + original.fecha.strftime("%d/%m/%Y") + " a " + instance.fecha.strftime("%d/%m/%Y"))
            # item_linked:
            if original.item_linked is None:
                if instance.item_linked is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Item-SubItem a ' + instance.item_linked.__str__())
            elif original.item_linked != instance.item_linked:
                if instance.item_linked is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Item-SubItem: ' + original.item_linked.__str__())
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Item-SubItem de " + original.item_linked.__str__() + " a " + instance.item_linked.__str__())
            # item:
            # subitem:

            # tipo_mov:
            if original.tipo_mov is None:
                if instance.tipo_mov is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Tipo de Movimiento a ' + instance.tipo_mov)
            elif original.tipo_mov != instance.tipo_mov:
                if instance.tipo_mov is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Tipo de Movimiento: ' + original.tipo_mov)
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Tipo de Movimiento de " + original.tipo_mov + " a " + instance.tipo_mov)
            # monto:
            if original.monto is None:
                if instance.monto is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Monto a ' + str(instance.monto))
            elif original.monto != instance.monto:
                if instance.monto is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Monto: ' + str(original.monto))
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Monto de " + str(original.monto) + " a " + str(instance.monto))
            # num_cheque:
            if original.num_cheque is None:
                if instance.num_cheque is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Numero de Cheque a ' + str(instance.num_cheque))
            elif original.num_cheque != instance.num_cheque:
                if instance.num_cheque is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Numero de Cheque: ' + str(original.num_cheque))
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Numero de Cheque de " + str(original.num_cheque) + " a " + str(instance.num_cheque))
            # num_boleta_factura:
            if original.num_boleta_factura is None:
                if instance.num_boleta_factura is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Numero de Boleta o Factura a ' + str(instance.num_boleta_factura))
            elif original.num_boleta_factura != instance.num_boleta_factura:
                if instance.num_boleta_factura is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Numero de Boleta o Factura: ' + str(original.num_boleta_factura))
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Numero de Boleta o Factura de " + str(original.num_boleta_factura) + " a " + str(instance.num_boleta_factura))
            # nombre_proveedor:
            if original.nombre_proveedor is None:
                if instance.nombre_proveedor is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Nombre del Proveedor a ' + instance.nombre_proveedor)
            elif original.nombre_proveedor != instance.nombre_proveedor:
                if instance.nombre_proveedor is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Nombre del Proveedor: ' + original.nombre_proveedor)
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Nombre del Proveedor de " + original.nombre_proveedor + " a " + instance.nombre_proveedor)
            # is_cheque:
            if original.is_cheque != instance.is_cheque:
                if original.is_cheque == 0 is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Este movimiendo se ha marcado como No Cheque' )
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Este movimiendo ahora esta marcado Cheque' )
            # rut_socio_asociado:
            if original.rut_socio_asociado is None:
                if instance.rut_socio_asociado is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Rut del Socio Asociado a ' + instance.rut_socio_asociado)
            elif original.rut_socio_asociado != instance.rut_socio_asociado:
                if instance.rut_socio_asociado is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Rut del Socio Asociado: ' + original.rut_socio_asociado)
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Rut del Socio Asociado de " + original.rut_socio_asociado + " a " + instance.rut_socio_asociado)
            # estado:
            if original.estado is None:
                if instance.estado is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Estado a ' + instance.estado)
            elif original.estado != instance.estado:
                if instance.estado is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Estado: ' + original.estado)
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Estado de " + original.estado + " a " + instance.estado)
            # adjunto:
            if original.adjunto is None:
                if instance.adjunto is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Archivo Adjunto')
            elif original.adjunto != instance.adjunto:
                if instance.adjunto is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Archivo Adjunto')
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Archivo Adjunto")
            # voucher:
            if original.voucher is None:
                if instance.voucher is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Voucher')
            elif original.voucher != instance.voucher:
                if instance.voucher is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Voucher')
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Voucher")
            # comentario:
            if original.comentario is None:
                if instance.comentario is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado el Folio a ' + instance.comentario)
            elif original.comentario != instance.comentario:
                if instance.comentario is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado el Folio: ' + original.comentario)
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion="Se ha actualizado el Folio de " + original.comentario + " a " + instance.comentario)
            # caratula:
            if original.caratula is None:
                if instance.caratula is not None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado la Caratula')
            elif original.caratula != instance.caratula:
                if instance.caratula is None:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha borrado la Caratula')
                else:
                    log = LogMovimientos.objects.create(user_do=instance.user_ult_modif,folio=instance.folio,fec_operacion=datetime.now(),
                        operacion='Se ha actualizado la Caratula')

            # Actualizar el presupuesto
            if original.item_linked != instance.item_linked or original.monto != instance.monto or original.tipo_mov != instance.tipo_mov:
                saldo = Saldo.objects.get(item_linked=original.item_linked)
                if original.tipo_mov != instance.tipo_mov:
                    if original.tipo_mov == 'Ingreso':
                        saldo.monto = (saldo.monto - original.monto)
                        saldo.save()
                        nuevo = Saldo.objects.get(item_linked=instance.item_linked)
                        nuevo.monto = (nuevo.monto - instance.monto)
                        nuevo.save()
                        # print("N1")
                        # print(instance.tipo_mov)
                        # print(instance.item_linked)
                        # print(saldo.monto)
                        # print(nuevo.monto)
                    else: #Egreso
                        saldo.monto = (saldo.monto + original.monto)
                        saldo.save()
                        nuevo = Saldo.objects.get(item_linked=instance.item_linked)
                        nuevo.monto = (nuevo.monto + instance.monto)
                        nuevo.save()
                        # print("N2")
                        # print(instance.tipo_mov)
                        # print(instance.item_linked)
                        # print(saldo.monto)
                        # print(nuevo.monto)
                else: #original.tipo_mov == instance.tipo_mov
                    if original.tipo_mov == 'Ingreso':
                        # reversar
                        saldo.monto = (saldo.monto - original.monto)
                        saldo.save()
                        # asignar nuevo movimiento a otro item
                        nuevo = Saldo.objects.get(item_linked=instance.item_linked)
                        nuevo.monto = (nuevo.monto + instance.monto)
                        nuevo.save()
                        # print("N3")
                        # print(instance.tipo_mov)
                        # print(instance.item_linked)
                        # print(saldo.monto)
                        # print(nuevo.monto)
                    else: #Egreso
                        # reversar
                        saldo.monto = (saldo.monto + original.monto)
                        saldo.save()
                        # asignar nuevo movimiento a otro item
                        nuevo = Saldo.objects.get(item_linked=instance.item_linked)
                        nuevo.monto = (nuevo.monto - instance.monto)
                        nuevo.save()
                        # print("N4")
                        # print(instance.tipo_mov)
                        # print(instance.item_linked)
                        # print(saldo.monto)
                        # print(nuevo.monto)

# class SubItem(models.Model):
#     item = models.ForeignKey(Item,on_delete=models.CASCADE)
#     nombre = models.CharField(max_length=50)
#     estado = models.CharField(max_length=50,choices=TIPOS_ESTADO,default='Vigente')
#     # campos de control
#     fec_creacion = models.DateTimeField(default=timezone.now)
#     user_creacion = models.CharField(max_length=250)
#     fec_ult_modif = models.DateTimeField(null=True,blank=True)
#     user_ult_modif = models.CharField(max_length=250,blank=True,null=True)
#
#     def __str__(self):
#         return self.nombre

class LogMovimientos(models.Model):
    operacion = models.CharField(max_length=500)
    folio = models.IntegerField(null=True,blank=True)
    user_do = models.CharField(max_length=250)
    fec_operacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.operacion
#
# class LogPresupuesto(models.Model):
#     operacion = models.CharField(max_length=500)
#     item = models.CharField(max_length=100)
#     subitem = models.CharField(max_length=100)
#     user_do = models.CharField(max_length=250)
#     fec_operacion = models.DateTimeField(default=timezone.now)
#
#     def __str__(self):
#         return self.operacion
