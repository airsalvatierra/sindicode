import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from datetime import datetime

# Create your models here.

###############################################################################
# Upload Folders
def user_asistencias_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/eventos/username/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    now = datetime.now()
    month = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return 'asistencias/{month}/{basename}_{stamp}{ext}'.format(month=month,basename=basefilename,stamp=stamp,ext=file_extension)

###############################################################################

class AsistenciaEnc(models.Model):
    TIPOS_ASISTENCIA = (
        ('Asamblea General Ordinaria','Asamblea General Ordinaria'),
        ('Asamblea General Extraordinaria','Asamblea General Extraordinaria'),
        ('Asamblea de Delegados','Asamblea de Delegados'),
        ('Asamblea de Comision','Asamblea de Comision'),
        ('Asamblea de Votación','Asamblea de Votación'),
        ('Asamblea Flex','Asamblea Flex'),
        ('Asamblea 6x2','Asamblea 6x2'),
        ('Asamblea Intermodal','Asamblea Intermodal'),
        ('Asamblea VVPP','Asamblea VVPP'),
        ('Asamblea PCC','Asamblea PCC'),
        ('Asamblea Control Cocheras','Asamblea Control Cocheras'),
        ('Asamblea Reguladores PMT','Asamblea Reguladores PMT'),
        ('Paseo Familiar de Fin de Año','Paseo Familiar de Fin de Año'),
        ('Fiesta Aniversario','Fiesta Aniversario')
    )
    fec_evento = models.DateField()
    usuario = models.CharField(max_length=50)
    tipo_evento = models.CharField(max_length=50, choices=TIPOS_ASISTENCIA)
    descripcion = models.CharField(max_length=500,null=True,blank=True)
    cant_asistencias = models.IntegerField(null=True)
    cant_ausentes = models.IntegerField(null=True)
    cant_total = models.IntegerField(null=True)
    archivo = models.FileField(upload_to=user_asistencias_directory_path)
    acta = models.FileField(upload_to=user_asistencias_directory_path)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return str(self.id)

class AsistenciaDet(models.Model):
    asistenciaenc = models.ForeignKey(AsistenciaEnc,on_delete=models.CASCADE,related_name='encabezado')
    fec_evento = models.DateField()
    rut_socio = models.CharField(max_length=50)
    email = models.EmailField()
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=100)
    TIPOS_ESTADO_ASISTENCIA = (
        ('Asistio','Asistio'),
        ('No Asistio','No Asistio'),
    )
    est_asistencia = models.CharField(max_length=50,choices=TIPOS_ESTADO_ASISTENCIA,default='No Asistio',null=True)
    TIPOS_ESTADO_NOTIFICACION = (
        ('Notificado','Notificado'),
        ('No Notificado','No Notificado'),
    )
    est_notificacion = models.CharField(max_length=50,choices=TIPOS_ESTADO_NOTIFICACION,null=True,blank=True)
    comentario = models.CharField(max_length=500,null=True,blank=True)
    TIPOS_ESTADO_JUSTIFICACION = (
        ('Justificado','Justificado'),
        ('No Justificado','No Justificado'),
    )
    #campos para el futuro de la aplicacion
    est_justificacion = models.CharField(max_length=50,choices=TIPOS_ESTADO_JUSTIFICACION,null=True,blank=True)
    arc_justificacion = models.FileField(upload_to=user_asistencias_directory_path,null=True,blank=True)
    TIPOS_ESTADO_APELACION = (
        ('Aceptada','Aceptada'),
        ('Rechazada','Rechazada'),
    )
    est_apelacion = models.CharField(max_length=50,choices=TIPOS_ESTADO_APELACION,null=True,blank=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.rut_socio

    def get_absolute_url(self):
        return reverse('asistencias:updatedet',kwargs={'pk':self.pk})

class Asistentes(models.Model):
    folio = models.IntegerField()
    rut_socio = models.CharField(max_length=50)
    est_asistencia = models.CharField(max_length=50,blank=True,null=True)
