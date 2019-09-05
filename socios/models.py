import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from socios.templatetags import poll_extras
from datetime import datetime
################# PARA LOS CHOICES #############################################

TIPOS_ESTADO_CIVIL = (
    ('Hijo/a','Hijo/a'),
    ('Padre/Madre','Padre/Madre'),
    ('Soltero/a','Soltero/a'),
    ('Casado/a','Casado/a'),
    ('Viudo/a','Viudo/a'),
    ('Divorciado/a','Divorciado/a'),
    ('Separado/a','Separado/a'),
    ('Conviviente','Conviviente')
)

TIPOS_FORMA_CONTACTO = (
    ('Email','Email'),
    ('Llamada Celular','Llamada Celular'),
    ('Mensaje de Whatsapp','Mensaje de Whatsapp'),
    ('SMS','SMS')
)

TIPOS_CARGOS = (
    ('Conductor','Conductor'),
    ('Control Cocheras','Control Cocheras'),
    ('Coordinador Operación Tráfico (COT)','Coordinador Operación Tráfico (COT)'),
    ('Regulador de PMT (Puesto Maniobra Talleres)','Regulador de PMT (Puesto Maniobra Talleres)'),
    ('Supervisor de Gestión de Operaciones (SGO)','Supervisor de Gestión de Operaciones (SGO)'),
    ('Jefe de Linea','Jefe de Linea'),
    ('Inspector Intermodal','Inspector Intermodal'),
    ('Vigilantes Privado (VVPP)','Vigilantes Privado (VVPP)'),
    ('Inspector de Seguridad (ISS)','Inspector de Seguridad (ISS)'),
    ('Regulador de PCC (Puesto de Comando Central)','Regulador de PCC (Puesto de Comando Central)'),
    ('ALA (Asistente de Lineas Automáticas)','ALA (Asistente de Lineas Automáticas)'),
    ('Analista de Capacitación','Analista de Capacitación'),
    ('Instructor de Capacitación','Instructor de Capacitación'),
    ('Analista de Mantenimiento','Analista de Mantenimiento'),
    ('Administrador de Contratos','Administrador de Contratos'),
    ('Otro','Otro'),
)

TIPOS_LUGAR_TRABAJO = (
    ('Linea 1','Linea 1'),
    ('Linea 1 - PML SP','Linea 1 - Puesto de Maniobra Local SP'),
    ('Linea 1 - PML PJ','Linea 1 - Puesto de Maniobra Local PJ'),
    ('Linea 1 - PML MQ','Linea 1 - Puesto de Maniobra Local MQ'),
    ('Linea 1 - PML LD','Linea 1 - Puesto de Maniobra Local LD'),
    ('Linea 1 - CPS','Linea 1 - Acopio Vigilante Privado'),
    ('Linea 2','Linea 2'),
    ('Linea 1 - Cochera o Taller Neptuno','Linea 1 - Cochera o Taller Neptuno'),
    ('Linea 2 - PML LC','Linea 2 - Puesto de Maniobra Local LC'),
    ('Linea 2 - PML VN','Linea 2 - Puesto de Maniobra Local VN'),
    ('Linea 2 - CPS ZP','Linea 2 - Acopio Vigilante Privado ZP'),
    ('Linea 2 - CPS LC','Linea 2 - Acopio Vigilante Privado LC'),
    ('Linea 2 - Cochera o Taller Lo Ovalle','Linea 2 - Cochera o Taller Lo Ovalle'),
    ('Linea 3','Linea 3'),
    ('Linea 4','Linea 4'),
    ('Linea 4 - PML TOB','Linea 4 - Puesto de Maniobra Local TOB'),
    ('Linea 4 - PPA','Linea 4 - PPA'),
    ('Linea 4 - Cochera o Taller Puente Alto','Linea 4 - Cochera o Taller Puente Alto'),
    ('Linea 4 - Cochera o Taller Intermedio Quilín','Linea 4 - Cochera o Taller Intermedio Quilín'),
    ('Linea 4a','Linea 4a'),
    ('Linea 4a - PML LCI','Linea 4a - Puesto de Maniobra Local LCI'),
    ('Linea 4a - PML VIM','Linea 4a - Puesto de Maniobra Local VIM'),
    ('Linea 5','Linea 5'),
    ('Linea 5 - PML PM','Linea 5 - Puesto de Maniobra Local PM'),
    ('Linea 5 - PML VV','Linea 5 - Puesto de Maniobra Local VV'),
    ('Linea 5 - Cochera o Taller San Eugenio','Linea 5 - Cochera o Taller San Eugenio'),
    ('Linea 6','Linea 6',),
    ('Edifico SEAT PCC','Edifico SEAT PCC'),
    ('Sede Sindical','Sede Sindical'),
)

TURNOS_CHOICES = (
    ('Turno 1','Turno 1 - Jornada AM'),
    ('Turno 2','Turno 2 - Jornada PM'),
    ('Flex','Flex (Rota entre AM, PM, MN y Noche)'),
    ('Fase','Fase - 2 Tardes, 2 Mañanas, 2 Noches'),
    ('HN','HN - Horario Normal de Oficina, 9 a 18 hrs')
)

TIPOS_CARGO_SINDICAL = (
    ('Socio','Socio'),
    ('Dirigente','Dirigente'),
    ('Delegado','Delegado'),
    ('Comision de Etica y Disciplina','Comision de Etica y Disciplina'),
    ('Comision Revisora de Cuentas','Comision Revisora de Cuentas'),
    ('Comision Bienestar Sindical','Comision Bienestar Sindical'),
    ('Comision Deportes y Cultura','Comision Deportes y Cultura'),
    ('Comision Eventos','Comision Eventos'),
    ('Comision Comunicaciones','Comision Comunicaciones'),
    ('Comision Salud Laboral','Comision Salud Laboral'),
    ('Tricel Sindical','Tricel Sindical')
)

TIPOS_ESTADOS_SOCIO = (
    ('Vigente','Vigente'),
    ('No Vigente','No Vigente'),
)

TIPOS_CARGA_SOCIO = (
    ('Legal','Hijo'),
    ('No Legal','Otro'),
)

###############################################################################
# Upload Folders
def user_evento_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/eventos/username/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    now = datetime.now()
    month = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return '{socio}/eventos/{month}/{basename}_{stamp}{ext}'.format(socio=instance.socio.username,month=month,basename=basefilename,stamp=stamp,ext=file_extension)

def user_profile_picture_directory_path(instance, filename):
    return '{socio}/profile_pic/{filename}'.format(socio=instance.username, filename= filename)

###############################################################################

# User = Socio
class User(AbstractUser):
    # ***CAMPOS QUE VIENEN HEREDADOS EN EL MODELO DE USER DE DJANGO***
    # username --> rut del socio
    # first_name --> Primer Nombre
    # last_name --> Segundo Nombre
    # email --> Correo electronico (obligatorio)
    # password
    # groups
    # user_permissions
    # is_staff
    # is_active
    # is_superuser
    # last_login
    # date_joined
    nom_adicional = models.CharField(max_length=50,blank=True,null=True)
    ape_materno = models.CharField(max_length=50,blank=True,null=True)
    fec_nacimiento = models.DateField(blank=True,null=True)
    foto = models.ImageField(upload_to=user_profile_picture_directory_path,blank=True,null=True)
    estado_civil = models.CharField(max_length=20,blank=True,null=True,choices=TIPOS_ESTADO_CIVIL)
    dir_domicilio = models.CharField(max_length=300,blank=True,null=True)
    # region =  models.ForeignKey('Region',on_delete=models.CASCADE)
    comuna =  models.CharField(max_length=100,blank=True,null=True)
    tel_celular = models.IntegerField(blank=True,null=True)
    for_contacto = models.CharField(max_length=50,choices=TIPOS_FORMA_CONTACTO,blank=True,null=True)
    num_hijos = models.IntegerField(blank=True,default=0,null=True)
    fec_ing_metro = models.DateField(blank=True,null=True)
    fec_ing_sindicato = models.DateField(blank=True, null=True)
    cargo =   models.CharField(max_length=50,blank=True,null=True,choices=TIPOS_CARGOS)
    lug_trabajo = models.CharField(max_length=100,blank=True,null=True,choices=TIPOS_LUGAR_TRABAJO)
    turno = models.CharField(max_length=50,blank=True,null=True,choices=TURNOS_CHOICES)
    car_sindical = models.CharField(max_length=50,choices=TIPOS_CARGO_SINDICAL,default='Socio')
    is_office = models.BooleanField(default=False)
    estado_socio = models.CharField(max_length=40,choices=TIPOS_ESTADOS_SOCIO,default='Vigente')
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return "{} - {} {}".format(poll_extras.rut_format(self.username),self.first_name,self.last_name)

# @receiver(pre_save, sender=settings.AUTH_USER_MODEL)
@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    # print("Michael Jordan Funcionando")
    created = User.objects.filter(pk=instance.id).count()
    if created > 0:
        original = User.objects.get(pk=instance.id)

    if created > 0:
        # username
        if original.username != instance.username:
            log = LogUser.objects.create(
                user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha actualizado el Rut de " + original.username + " a " + instance.username)
        # first_name
        if original.first_name != instance.first_name:
            log = LogUser.objects.create(
                user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha actualizado el Nombre de " + original.first_name + " a " + instance.first_name)
        # last_name
        if original.last_name != instance.last_name:
            log = LogUser.objects.create(
                user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha actualizado el Apellido Paterno de " + original.last_name + " a " + instance.last_name)
        # email
        if original.email != instance.email:
            log = LogUser.objects.create(
                user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha actualizado el Nombre de " + original.email + " a " + instance.email)
        # nom_adicional
        if original.nom_adicional is None:
            if instance.nom_adicional is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se han actualizado el(los) Nombre(s) Adicional(es) a " + instance.nom_adicional)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.nom_adicional != instance.nom_adicional:
            if instance.nom_adicional is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha(n) borrado el(los) Nombre(s) Adicional(es) de ")
            # print("Se ha actualizado el nombre adicional de " + original.nom_adicional + " a " + instance.nom_adicional)
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha(n) actualizado el(los) Nombre(s) Adicional(es) de " + original.nom_adicional + " a " + instance.nom_adicional)
        # ape_materno
        if original.ape_materno is None:
            if instance.ape_materno is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Apellido Materno a " + instance.ape_materno)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.ape_materno != instance.ape_materno:
            if instance.ape_materno is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha borrado el Apellido Materno")
            else:
            # print("Se ha actualizado el nombre adicional de " + original.nom_adicional + " a " + instance.nom_adicional)
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Apellido Materno de " + original.ape_materno + " a " + instance.ape_materno)
        # fec_nacimiento
        if original.fec_nacimiento is None:
            if instance.fec_nacimiento is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Nacimiento a " + instance.fec_nacimiento.strftime("%d/%m/%Y"))
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.fec_nacimiento != instance.fec_nacimiento:
            if instance.fec_nacimiento is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se han borrado la Fecha de Nacimiento")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Nacimiento de " + original.fec_nacimiento.strftime("%d/%m/%Y") + " a " + instance.fec_nacimiento.strftime("%d/%m/%Y"))
        # foto
        if original.foto is None:
            if instance.foto is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Foto de Perfil")
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.foto != instance.foto:
            if instance.foto is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Foto de Perfil")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Foto de Perfil")
        # estado_civil
        if original.estado_civil is None:
            if instance.estado_civil is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Estado Civil a " + instance.estado_civil)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.estado_civil != instance.estado_civil:
            if instance.estado_civil is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Estado Civil")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Estado Civil de " + original.estado_civil + " a " + instance.estado_civil)
        # dir_domicilio
        if original.dir_domicilio is None:
            if instance.dir_domicilio is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Direccion a " + instance.dir_domicilio)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.dir_domicilio != instance.dir_domicilio:
            if instance.dir_domicilio is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Direccion")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Direccion de " + original.dir_domicilio + " a " + instance.dir_domicilio)
        # comuna
        if original.comuna is None:
            if instance.comuna is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Comuna a " + instance.comuna)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.comuna != instance.comuna:
            if instance.comuna is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Comuna")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Comuna de " + original.comuna + " a " + instance.comuna)
        # tel_celular
        if original.tel_celular is None:
            if instance.tel_celular is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Telefono Celular a " + str(instance.tel_celular))
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.tel_celular != instance.tel_celular:
            if instance.tel_celular is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Telefono Celular")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Telefono Celular de " + tr(original.tel_celular) + " a " + str(instance.tel_celular))
        # for_contacto
        if original.for_contacto is None:
            if instance.for_contacto is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Forma de Contacto Preferida a " + instance.for_contacto)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.for_contacto != instance.for_contacto:
            if instance.for_contacto is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Forma de Contacto Preferida")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Forma de Contacto Preferida de " + original.for_contacto + " a " + instance.for_contacto)
        # num_hijos
        if original.num_hijos is None:
            if instance.num_hijos is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Cantidad de Hijos a " + str(instance.num_hijos))
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.num_hijos != instance.num_hijos:
            if instance.num_hijos is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Cantidad de Hijos")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Cantidad de Hijos de " + str(original.num_hijos) + " a " + str(instance.num_hijos))
        # fec_ing_metro
        if original.fec_ing_metro is None:
            if instance.fec_ing_metro is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Ingreso al Metro a " + instance.fec_ing_metro.strftime("%d/%m/%Y"))
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.fec_ing_metro != instance.fec_ing_metro:
            if instance.fec_ing_metro is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Fecha de Ingreso al Metro")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Ingreso al Metro de " + original.fec_ing_metro.strftime("%d/%m/%Y") + " a " + instance.fec_ing_metro.strftime("%d/%m/%Y"))
        # fec_ing_sindicato
        if original.fec_ing_sindicato is None:
            if instance.fec_ing_sindicato is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Ingreso al Sindicato a " + instance.fec_ing_sindicato.strftime("%d/%m/%Y"))
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.fec_ing_sindicato != instance.fec_ing_sindicato:
            if instance.fec_ing_sindicato is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado la Fecha de Ingreso al Sindicato")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado la Fecha de Ingreso al Sindicato de " + original.fec_ing_sindicato.strftime("%d/%m/%Y") + " a " + instance.fec_ing_sindicato.strftime("%d/%m/%Y"))
        # cargo
        if original.cargo is None:
            if instance.cargo is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Cargo Laboral a " + instance.cargo)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.cargo != instance.cargo:
            if instance.cargo is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Cargo Laboral")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Cargo Laboral de " + original.cargo + " a " + instance.cargo)
        # lug_trabajo
        if original.lug_trabajo is None:
            if instance.lug_trabajo is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Lugar de Trabajo a " + instance.lug_trabajo)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.lug_trabajo != instance.lug_trabajo:
            if instance.lug_trabajo is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Lugar de Trabajo")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Lugar de Trabajo de " + original.lug_trabajo + " a " + instance.lug_trabajo)
        # turno
        if original.turno is None:
            if instance.turno is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Turno de Trabajo a " + instance.turno)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.turno != instance.turno:
            if instance.turno is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Turno de Trabajo")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Turno de Trabajo de " + original.turno + " a " + instance.turno)
        # car_sindical
        if original.car_sindical is None:
            if instance.car_sindical is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Cargo Sindical a " + instance.car_sindical)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.car_sindical != instance.car_sindical:
            if instance.car_sindical is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Cargo Sindical")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Cargo Sindical de " + original.car_sindical + " a " + instance.car_sindical)
        # is_office
        # estado_socio
        if original.estado_socio is None:
            if instance.estado_socio is not None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Estado del Socio a " + instance.estado_socio)
                # print("Se ha actualizado el nombre adicional a " + instance.nom_adicional)
        elif original.estado_socio != instance.estado_socio:
            if instance.estado_socio is None:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se borrado el Estado del Socio")
            else:
                log = LogUser.objects.create(
                    user_do=instance.user_ult_modif, rut=instance.username, fec_operacion=datetime.now(),
                    operacion="Se ha actualizado el Estado del Socio de " + original.estado_socio + " a " + instance.estado_socio)

@receiver(post_save , sender=User)
def log_new_user(sender, instance, created, **kwargs):
    if created:
        if instance.user_creacion is None:
            log = LogUser.objects.create(
                user_do='-', rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha creado un nuevo socio: " + instance.__str__())
        else:
            log = LogUser.objects.create(
                user_do=instance.user_creacion, rut=instance.username, fec_operacion=datetime.now(),
                operacion="Se ha creado un nuevo socio: " + instance.__str__())
    else:
        print(instance)

class KerCargaSocio(models.Model):
    socio = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    tipo_carga = models.CharField(max_length=50,choices=TIPOS_CARGA_SOCIO,default='Legal')
    nombre = models.CharField(max_length=50,null=True)
    ape_paterno = models.CharField(max_length=50,null=True)
    ape_materno = models.CharField(max_length=50,null=True,blank=True)
    edad = models.IntegerField(null=True,blank=True)
    comentario = models.CharField(max_length=300,null=True,blank=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

# class KerLugarTrabajo(models.Model):
#     LINEAS_METRO = (
#         ('Linea 1','Linea 1'),
#         ('Cochera o Talleres Neptuno','Cochera o Talleres Neptuno'),
#         ('Linea 2','Linea 2'),
#         ('Linea 4','Linea 4'),
#         ('Linea 4a','Linea 4a'),
#         ('Linea 5','Linea 5'),
#         ('Linea 6','Linea 6'),
#         ('Edificio SEAT PCC','Edificio SEAT PCC'),
#     )
#     linea = models.CharField(max_length=30,choices=LINEAS_METRO)
#     lugar = models.CharField(max_length=50)
#     nombre_corto = models.CharField(max_length=200,null=True)
#     nombre_largo = models.CharField(max_length=200,null=True)
#     # campos de control
#     fec_creacion = models.DateTimeField(default=timezone.now)
#     user_creacion = models.CharField(max_length=250)
#     fec_ult_modif = models.DateTimeField(null=True,blank=True)
#     user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

# Modelo de roles
class KerRol(models.Model):
    tipo_rol = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=150,null=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.tipo_rol

class KerSocioRol(models.Model):
    socio = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    rol = models.ForeignKey('KerRol',on_delete=models.CASCADE,related_name='roles')
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return str(self.socio)

class KerFun(models.Model):
    rol = models.ForeignKey('KerRol',on_delete=models.CASCADE)
    fun = models.CharField(max_length=30)
    app = models.CharField(max_length=10)
    url = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50,blank=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.fun

class KerEvento(models.Model):
    tipo_evento = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50,null=True)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.tipo_evento

class KerEventoPersona(models.Model):
    socio = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey('KerEvento',on_delete=models.CASCADE)
    fec_evento = models.DateField()
    detalle = models.TextField(max_length=500)
    adjunto = models.FileField(upload_to=user_evento_directory_path,null=True,blank=True)
    rut_usuario = models.CharField(max_length=50) #el usuario que crea el evento
    nombre_usuario = models.CharField(max_length=50) #el usuario que crea el evento
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

# Comunas, ciudades y regiones
class Comuna(models.Model):
    comuna = models.CharField(max_length=50)
    region = models.ForeignKey('Region',on_delete=models.CASCADE)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.comuna

# class Ciudad(models.Model):
#     ciudad = models.CharField(max_length=50)
#     region = models.ForeignKey('Region',on_delete=models.CASCADE)
#     # campos de control
#     fec_creacion = models.DateTimeField(default=timezone.now)
#     user_creacion = models.CharField(max_length=250)
#     fec_ult_modif = models.DateTimeField(null=True,blank=True)
#     user_ult_modif = models.CharField(max_length=250,blank=True,null=True)
#
#     def __str__(self):
#         return self.ciudad

class Region(models.Model):
    num_region = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    cod_iso = models.CharField(max_length=250)
    # campos de control
    fec_creacion = models.DateTimeField(default=timezone.now)
    user_creacion = models.CharField(max_length=250)
    fec_ult_modif = models.DateTimeField(null=True,blank=True)
    user_ult_modif = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return self.region

class LogUser(models.Model):
    operacion = models.CharField(max_length=250)
    rut = models.CharField(max_length=250)
    user_do = models.CharField(max_length=250)
    fec_operacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.operacion

###############################################################################
# Upload Folders
def user_evento_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/eventos/username/<filename>
    basefilename, file_extension= os.path.splitext(filename)
    now = datetime.now()
    month = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%d_%H%M%S")
    return '{socio}/eventos/{month}/{basename}_{stamp}{ext}'.format(socio=instance.socio.username,month=month,basename=basefilename,stamp=stamp,ext=file_extension)

def user_profile_picture_directory_path(instance, filename):
    return '{socio}/profile_pic/{filename}'.format(socio=instance.socio.username, filename= filename)
