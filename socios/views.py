import datetime
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings

from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.contrib import messages

from .models import User,KerRol, KerSocioRol, KerFun, LogUser, KerCargaSocio,KerEventoPersona
from .forms import UserForm,EditUserForm,RolesForm,SocioForm, CargaSocioForm,EventoPersonaForm
from asistencias.models import AsistenciaDet
from finanzas.models import IngresoEgreso
from sindicato.utils import formatRut,validarRut
from socios.templatetags.poll_extras import rut_format, rut_unformat

# Create your views here.
@login_required
def home_page(request):
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    context = {
        'roles':roles,
    }
    return render(request,'index.html',context)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('socios:user_login'))

def user_login(request):
    if request.method == 'POST':
        username = rut_unformat(request.POST.get('username').upper())
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                # Si el rut y el password son iguales debe cambiarlos
                # Hacer un if si el rut y el password son igual redirigirl a
                # cambiar el password, sino redirigir al home
                if username == password:
                    return HttpResponseRedirect(reverse('change_password2'))
                else:
                    return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse("Account not active")
        else:
            print("Alguien a intentado entrar y fallo")
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("Credenciales invalidas!")
    else:
        return render(request,'socios/login.html',{})

def change_password(request):
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Su contraseña ha sido cambiada exitosamente!')
            # return redirect('change_password')
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.error(request, 'Por favor corriga los errores mencionados.')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'roles':roles,
        'form':form,
    }
    return render(request,'socios/change_password.html',context)

def change_password_mandatory(request):
    # roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Su contraseña ha sido cambiada exitosamente!')
            # return redirect('change_password')
            logout(request)
            # return HttpResponseRedirect(reverse('home'))
        else:
            messages.error(request, 'Por favor corriga los errores mencionados.')
            # logout(request)
            # return HttpResponseRedirect(reverse('socios:user_login'))
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form':form,
    }
    return render(request,'socios/change_password.html',context)

@login_required
def create_socio(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():

            if validarRut(request.POST.getlist('username')[0]) == False:
                return HttpResponse("RUT invalido!")
            else:
                rut = request.POST.getlist('username')[0]
                rut = rut.replace("-","")
                rut = rut.replace(".","")

            user = user_form.save(commit=False)
            user.username = rut.upper()
            user.user_creacion = request.user.username
            user.fec_creacion = datetime.datetime.now()
            user.set_password(user.username)
            user.save()

            if 'foto' in request.FILES:
                user.foto = request.FILES['foto']
                user.save()

            rol = KerRol.objects.get(tipo_rol='Socio')
            sociorol = KerSocioRol.objects.create(socio=user,rol=rol,user_creacion=user.username)
            sociorol.save()

            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    context = {
        'user_form':user_form,
        'roles':roles,
        'registered': registered
    }
    return render(request,'socios/create_socio.html',context)

@login_required
def edit_socio(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    # Traigo al socio con el pk
    socio = User.objects.get(pk=pk)
    img = socio.foto

    rut= str(socio.username)
    # socio.username = formatRut(rut)
    log = LogUser.objects.filter(rut__icontains=rut).order_by('-fec_operacion')
    asistencias = AsistenciaDet.objects.filter(rut_socio=rut).order_by('-fec_evento')
    cargas = KerCargaSocio.objects.filter(socio=socio)
    eventos = KerEventoPersona.objects.filter(socio=socio)
    finanzas = IngresoEgreso.objects.filter(rut_socio_asociado=socio.username)

    # Logica para los checkbox de los roles
    flagradmin = "t"
    flagrsocio = "t"
    flagrmantencion = "t"
    flagrasistencia = "t"
    flagrfinanzas = "t"
    flagrhistorial = "t"
    # flagraprobador = "t"
    flagrcometica = "t"
    flagrcontador = "t"
    flagrverfin = "t"

    if KerSocioRol.objects.filter(socio=pk,rol_id=1) : flagradmin = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=2) : flagrsocio = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=3) : flagrmantencion = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=4) : flagrasistencia = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=5) : flagrfinanzas = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=6) : flagrhistorial = "checked='checked'"
    # if KerSocioRol.objects.filter(socio=pk,rol_id=7) : flagraprobador = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=8) : flagrcometica = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=9) : flagrcontador = "checked='checked'"
    if KerSocioRol.objects.filter(socio=pk,rol_id=10) : flagrverfin = "checked='checked'"

    if socio.fec_nacimiento:
        socio.fec_nacimiento = socio.fec_nacimiento.strftime("%d/%m/%Y")
    if socio.fec_ing_metro:
        socio.fec_ing_metro = socio.fec_ing_metro.strftime("%d/%m/%Y")
    if socio.fec_ing_sindicato:
        socio.fec_ing_sindicato = socio.fec_ing_sindicato.strftime("%d/%m/%Y")

    if request.method == 'POST':
        user_form = EditUserForm(request.POST,instance=socio)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.username = rut_unformat(user.username)
            user.user_ult_modif = request.user.username
            user.fec_ult_modif = datetime.datetime.now()
            user.save()

            if 'foto' in request.FILES:
                user.foto = request.FILES['foto']
                user.save()

            messages.success(request, 'Su ha actualizado la informacion del socio!')
        else:
            print(user_form.errors)
    else:
        socio.username = rut_format(socio.username)
        user_form = EditUserForm(instance=socio)

    context = {
        'flagradmin':flagradmin,
        'flagrsocio':flagrsocio,
        'flagrmantencion':flagrmantencion,
        'flagrasistencia':flagrasistencia,
        'flagrfinanzas':flagrfinanzas,
        'flagrhistorial':flagrhistorial,
        # 'flagraprobador':flagraprobador,
        'flagrcometica':flagrcometica,
        'flagrcontador':flagrcontador,
        'flagrverfin':flagrverfin,
        'user_form':user_form,
        'roles':roles,
        'cargas':cargas,
        'eventos':eventos,
        'log':log,
        'asistencias':asistencias,
        'finanzas':finanzas,
        'socio':socio,
        'foto':img,
    }
    return render(request,'socios/update_socio.html',context)

@login_required
def list_socio(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    socios = User.objects.all()

    for row in socios:
        if validarRut(row.username):
            rut = formatRut(row.username)
            row.username = rut
        else:
            print('no es valido')
    context = {
        'socios':socios,
        'roles':roles,
    }
    return render(request, 'socios/list_socio.html', context)

@login_required
def list_socio_roles(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Administracion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    socios = User.objects.all()
    context = {
        'socios':socios,
        'roles':roles,
    }
    return render(request, 'socios/list_socio_roles.html', context)

@login_required
def editar_roles(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Administracion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    flagradmin = False
    flagrsocio = False
    flagrmantencion = False
    flagrasistencia = False
    flagrfinanzas = False
    flagrhistorial = False
    # flagraprobador = False
    flagrcometica = False
    flagrcontador = False
    flagrverfin = False
    roladmin = False
    rolsocio = False
    rolmantencion = False
    rolasistencia = False
    rolfinanzas = False
    rolhistorial = False
    # rolaprobador = False
    rolcometica = False
    rolcontador = False
    rolverfin = False

    if KerSocioRol.objects.filter(socio=pk,rol_id=1) : flagradmin = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=2) : flagrsocio = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=3) : flagrmantencion = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=4) : flagrasistencia = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=5) : flagrfinanzas = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=6) : flagrhistorial = True
    # if KerSocioRol.objects.filter(socio=pk,rol_id=7) : flagraprobador = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=8) : flagrcometica = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=9) : flagrcontador = True
    if KerSocioRol.objects.filter(socio=pk,rol_id=10) : flagrverfin = True

    socio = User.objects.get(pk=pk)

    if request.method == 'POST':
        if request.POST.getlist('roladmin') : roladmin = True
        if request.POST.getlist('rolsocio') : rolsocio = True
        if request.POST.getlist('rolmantencion') : rolmantencion = True
        if request.POST.getlist('rolasistencia') : rolasistencia = True
        if request.POST.getlist('rolfinanzas') : rolfinanzas = True
        if request.POST.getlist('rolhistorial') : rolhistorial = True
        # if request.POST.getlist('rolaprobador') : rolaprobador = True
        if request.POST.getlist('rolcometica') : rolcometica = True
        if request.POST.getlist('rolcontador') : rolcontador = True
        if request.POST.getlist('rolverfin') : rolverfin = True

        if flagradmin != roladmin:
            if roladmin :
                rol = KerRol.objects.get(tipo_rol='Administracion')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=1).delete()
        if flagrsocio != rolsocio:
            if rolsocio :
                rol = KerRol.objects.get(tipo_rol='Socio')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=2).delete()
        if flagrmantencion != rolmantencion:
            if rolmantencion :
                rol = KerRol.objects.get(tipo_rol='Mantencion')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=3).delete()
        if flagrasistencia != rolasistencia:
            if rolasistencia :
                rol = KerRol.objects.get(tipo_rol='Asistencia')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=4).delete()
        if flagrfinanzas != rolfinanzas:
            if rolfinanzas :
                rol = KerRol.objects.get(tipo_rol='Finanzas')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=5).delete()
        if flagrhistorial != rolhistorial:
            if rolhistorial :
                rol = KerRol.objects.get(tipo_rol='Historial')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=6).delete()
        # if flagraprobador != rolaprobador:
        #     if rolaprobador :
        #         rol = KerRol.objects.get(tipo_rol='Aprobador')
        #         sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
        #         sociorol.save()
        #     else:
        #         KerSocioRol.objects.filter(socio=pk,rol_id=7).delete()
        if flagrcometica != rolcometica:
            if rolcometica :
                rol = KerRol.objects.get(tipo_rol='Comite Etica')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=8).delete()
        if flagrcontador != rolcontador:
            if rolcontador :
                rol = KerRol.objects.get(tipo_rol='Contador')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=9).delete()
        if flagrverfin != rolverfin:
            if rolverfin :
                rol = KerRol.objects.get(tipo_rol='VerFinanzas')
                sociorol = KerSocioRol.objects.create(socio=socio,rol=rol,user_creacion=request.user.username)
                sociorol.save()
            else:
                KerSocioRol.objects.filter(socio=pk,rol_id=10).delete()

        messages.success(request, 'Se han actualizado los roles!')

        socios = User.objects.all()
        context = {
            'roles':roles,
            'socios':socios,
        }
        return redirect(reverse('socios:editar',kwargs={'pk':socio.pk}))

        #age = request.POST['age']
        #print(age)
        #print(roladmin)
    else:
        print("no entro")

@login_required
def mi_informacion(request):
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))

    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')

    socio = User.objects.get(pk=request.user.pk)
    img = socio.foto

    if request.user.fec_nacimiento:
        request.user.fec_nacimiento = request.user.fec_nacimiento.strftime("%d/%m/%Y")
    if request.user.fec_ing_metro:
        request.user.fec_ing_metro = request.user.fec_ing_metro.strftime("%d/%m/%Y")
    if request.user.fec_ing_sindicato:
        request.user.fec_ing_sindicato = request.user.fec_ing_sindicato.strftime("%d/%m/%Y")

    if request.method == 'POST':
        user_form = SocioForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.username = rut_unformat(user.username)
            user.user_ult_modif = request.user.username
            user.fec_ult_modif = datetime.datetime.now()

            if 'foto' in request.FILES:
                user.foto = request.FILES['foto']

            user.save()

            messages.success(request, 'Su actualizado su informacion correctamente!')
        else:
            print(user_form.errors)
    else:
        request.user.username = rut_format(request.user.username)
        user_form = SocioForm(instance=request.user)

    context = {
        'roles':roles,
        'user_form':user_form,
        'foto':img,
    }
    return render(request, 'socios/mi_informacion.html', context)

@login_required
def list_log_socio(request):
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
    logs = LogUser.objects.all().order_by('fec_operacion')

    context = {
        'logs':logs,
        'roles':roles,
    }
    return render(request, 'socios/list_log_socio.html', context)

@login_required
def list_socios_cargas(request):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    socios = User.objects.all()
    context = {
        'socios':socios,
        'roles':roles,
    }
    return render(request, 'socios/list_socio_cargas.html', context)

@login_required
def list_cargas(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################
    socio = User.objects.get(pk=pk)
    cargas = KerCargaSocio.objects.filter(socio=socio)

    context = {
        'cargas':cargas,
        'roles':roles,
        'socio':socio
    }
    return render(request, 'socios/list_cargas.html', context)

@login_required
def crear_carga(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    socio = User.objects.get(pk=pk)
    cargas = KerCargaSocio.objects.filter(socio=socio)

    if request.method == 'POST':
        carga_form = CargaSocioForm(request.POST)
        if carga_form.is_valid():
            user = carga_form.save()

            messages.success(request, 'Su creado correctamente la carga!')
            return redirect(reverse('socios:editar',kwargs={'pk':socio.pk}))
        else:
            print(carga_form.errors)
    else:
        carga_form = CargaSocioForm(initial={'socio':socio})

    context = {
        'carga_form':carga_form,
        'roles':roles,
        'socio':socio
    }
    return render(request, 'socios/crear_carga.html', context)

@login_required
def delete_carga(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    carga = KerCargaSocio.objects.get(pk=pk)
    socio = User.objects.get(username=carga.socio.username)
    KerCargaSocio.objects.get(pk=pk).delete()
    # socio = User.objects.get(pk=pk)

    return redirect(reverse('socios:editar',kwargs={'pk':socio.pk}))

@login_required
def crear_evento(request,pk):
    ############################################################################
    #Agregar validacion de rol, si el rol no corresponde, redirigirlo al home o
     # a pagina que indique acceso denegado se traen los roles que tiene asignado el usuario
    roles = KerSocioRol.objects.filter(socio=request.user).order_by('rol')
    allow = False
    for rol in roles:
        if rol.rol.tipo_rol == 'Mantencion':
            allow = True
    if not allow:
        return HttpResponseRedirect(reverse('home'))
    if request.user.last_login is None:
        return HttpResponseRedirect(reverse('change_password2'))
    ############################################################################

    socio = User.objects.get(pk=pk)
    eventos = KerEventoPersona.objects.filter(socio=socio)

    if request.method == 'POST':
        evento_form = EventoPersonaForm(request.POST,request.FILES)
        if evento_form.is_valid():
            user = evento_form.save(commit=False)

            if 'adjunto' in request.FILES:
                user.adjunto = request.FILES['adjunto']

            user.rut_usuario = request.user.username
            user.nombre_usuario = request.user.first_name + ' ' + request.user.last_name
            user.user_creacion = request.user.username

            user.save()

            messages.success(request, 'Su creado correctamente el evento!')
            return redirect(reverse('socios:editar',kwargs={'pk':socio.pk}))
        else:
            print(evento_form.errors)
    else:
        evento_form = EventoPersonaForm(initial={'socio':socio})

    context = {
        'evento_form':evento_form,
        'roles':roles,
        'socio':socio
    }
    return render(request, 'socios/crear_evento.html', context)
