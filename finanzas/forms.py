from django import forms
from .models import IngresoEgreso, Saldo
from socios.models import KerSocioRol,KerRol,User
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth
from .models import Item
from socios.templatetags.poll_extras import rut_format,rut_unformat
from django.db.models.fields import BLANK_CHOICE_DASH

# TIPOS_ESTADO_MOV = (
#     ('Ingresado','Ingresado'),
#     ('Revisado','Revisado'),
#     ('Cuadratura ','Cuadratura '),
# )

class IngresoEgresoForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    comentario = forms.CharField(required=False,widget=forms.Textarea)
    rut_socio_asociado = forms.ChoiceField(choices = tuple(BLANK_CHOICE_DASH + [(choice.username, choice) for choice in get_user_model().objects.all().order_by('last_name')]), initial='', widget=forms.Select())

    class Meta:
        model = IngresoEgreso
        fields = ['folio','fecha','item_linked','tipo_mov','monto','num_cheque',
            'num_boleta_factura','nombre_proveedor','is_cheque','rut_socio_asociado',
            'estado','adjunto','voucher','comentario']

    def __init__(self,*args,**kwargs):
        # self.user = kwargs.pop('user', None)
        super(IngresoEgresoForm,self).__init__(*args,**kwargs)
        # obj = KerRol.objects.get(tipo_rol='Aprobador')
        # self.fields['rut_aprob'].queryset = obj.roles.all().exclude(socio=self.user)
        # Article.objects.values_list('comment_id', flat=True).distinct()
        self.fields['folio'].required = False
        self.fields['tipo_mov'].label = "Tipo de Movimiento"
        self.fields['item_linked'].label = "Item"
        self.fields['num_cheque'].label = "N° Cheque"
        self.fields['num_boleta_factura'].label = "N° Boleta/Factura"
        self.fields['nombre_proveedor'].label = "Nombre Proveedor"
        self.fields['is_cheque'].label = "Cheque"
        self.fields['rut_socio_asociado'].label = "Socio Asociado"
        self.fields['rut_socio_asociado'].required = False
        self.fields['adjunto'].label = "Respaldo"
        self.fields['estado'].required = False

class MovimientoEditForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    comentario = forms.CharField(required=False,widget=forms.Textarea)
    rut_socio_asociado = forms.ChoiceField(choices = tuple(BLANK_CHOICE_DASH + [(choice.username, choice) for choice in get_user_model().objects.all().order_by('last_name')]), initial='', widget=forms.Select())

    class Meta:
        model = IngresoEgreso
        fields = ['folio','fecha','item_linked','tipo_mov','monto','num_cheque',
            'num_boleta_factura','nombre_proveedor','is_cheque','rut_socio_asociado',
            'estado','adjunto','voucher','caratula','comentario']

    def __init__(self,*args,**kwargs):
        # self.user = kwargs.pop('user', None)
        super(MovimientoEditForm,self).__init__(*args,**kwargs)
        # obj = KerRol.objects.get(tipo_rol='Aprobador')
        # self.fields['rut_aprob'].queryset = obj.roles.all().exclude(socio=self.user)
        # Article.objects.values_list('comment_id', flat=True).distinct()
        # self.fields['estado'] = forms.ChoiceField(choices=TIPOS_ESTADO_MOV)
        self.fields['folio'].required = False
        self.fields['tipo_mov'].label = "Tipo de Movimiento"
        self.fields['item_linked'].label = "Item"
        self.fields['num_cheque'].label = "N° Cheque"
        self.fields['num_boleta_factura'].label = "N° Boleta/Factura"
        self.fields['nombre_proveedor'].label = "Nombre Proveedor"
        self.fields['is_cheque'].label = "Cheque"
        self.fields['rut_socio_asociado'].label = "Socio Asociado"
        self.fields['rut_socio_asociado'].required = False
        self.fields['adjunto'].label = "Respaldo"
        self.fields['estado'].required = False
        self.fields['estado'].disabled = True
        self.fields['folio'].disabled = True

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Saldo
        fields = ['item_linked','monto']

    def __init__(self,*args,**kwargs):
        # self.user = kwargs.pop('user', None)
        super(PresupuestoForm,self).__init__(*args,**kwargs)
        self.fields['item_linked'].label = ""
        self.fields['monto'].label = ""
        self.fields['item_linked'].disabled = True
        # self.fields['año'].label = "Año"
        # self.fields['year'].label = "Año"

class CierreForm(forms.Form):
    mes = forms.ChoiceField(widget=forms.Select())

    def __init__(self,*args,**kwargs):
        super(CierreForm,self).__init__(*args,**kwargs)
        # Traer los meses con movimientos no cerrados
        pendientes  = IngresoEgreso.objects.exclude(estado="Cerrado").annotate(fec_trunc=TruncMonth('fecha')).values('fec_trunc').distinct()
        MESES = []
        for pen in pendientes:
            MESES.append((str(pen['fec_trunc']),pen['fec_trunc'].strftime("%m-%Y")))
        self.fields['mes'].label = "Mes"
        self.fields['mes'].choices = BLANK_CHOICE_DASH + MESES

class DesdeHastaForm(forms.Form):
    TIPO_GENERACION = (
        ('Excel','Excel'),
        ('PDF','PDF')
    )
    tipo = forms.ChoiceField(choices=TIPO_GENERACION,widget=forms.Select())
    desde = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    hasta = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))

    def clean(self):
        cleaned_data = super(DesdeHastaForm, self).clean()
        inicio = cleaned_data.get("desde")
        fin = cleaned_data.get("hasta")

        if inicio and fin:
            if fin < inicio:
                # raise forms.ValidationError("La fecha Hasta no puede ser anterior la fecha Desde")
                self.add_error('desde', "La fecha Hasta no puede ser anterior la fecha Desde")
        return cleaned_data

    def __init__(self,*args,**kwargs):
        super(DesdeHastaForm,self).__init__(*args,**kwargs)
        self.fields['tipo'].label = "Tipo"
        self.fields['desde'].label = "Desde"
        self.fields['hasta'].label = "Hasta"
        self.fields['desde'].required = False
        self.fields['hasta'].required = False

class MovimientoViewForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    comentario = forms.CharField(required=False,widget=forms.Textarea)
    rut_socio_asociado = forms.ChoiceField(choices = tuple(BLANK_CHOICE_DASH + [(choice.username, choice) for choice in get_user_model().objects.all().order_by('last_name')]), initial='', widget=forms.Select())

    class Meta:
        model = IngresoEgreso
        fields = ['folio','fecha','item_linked','tipo_mov','monto','num_cheque',
            'num_boleta_factura','nombre_proveedor','is_cheque','rut_socio_asociado',
            'estado','adjunto','voucher','caratula','comentario']

    def __init__(self,*args,**kwargs):
        # self.user = kwargs.pop('user', None)
        super(MovimientoViewForm,self).__init__(*args,**kwargs)
        # obj = KerRol.objects.get(tipo_rol='Aprobador')
        # self.fields['rut_aprob'].queryset = obj.roles.all().exclude(socio=self.user)
        # Article.objects.values_list('comment_id', flat=True).distinct()
        self.fields['folio'].required = False
        self.fields['tipo_mov'].label = "Tipo de Movimiento"
        self.fields['item_linked'].label = "Item"
        self.fields['num_cheque'].label = "N° Cheque"
        self.fields['num_boleta_factura'].label = "N° Boleta/Factura"
        self.fields['nombre_proveedor'].label = "Nombre Proveedor"
        self.fields['is_cheque'].label = "Cheque"
        self.fields['rut_socio_asociado'].label = "Socio Asociado"
        self.fields['rut_socio_asociado'].required = False
        self.fields['adjunto'].label = "Respaldo"
        self.fields['estado'].required = False
        self.fields['folio'].disabled = True
        self.fields['fecha'].disabled = True
        self.fields['item_linked'].disabled = True
        self.fields['tipo_mov'].disabled = True
        self.fields['num_cheque'].disabled = True
        self.fields['monto'].disabled = True
        self.fields['num_boleta_factura'].disabled = True
        self.fields['nombre_proveedor'].disabled = True
        self.fields['is_cheque'].disabled = True
        self.fields['rut_socio_asociado'].disabled = True
        self.fields['estado'].disabled = True
        self.fields['adjunto'].disabled = True
        self.fields['voucher'].disabled = True
        self.fields['caratula'].disabled = True
        self.fields['comentario'].disabled = True

class MovimientoEditFullForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    comentario = forms.CharField(required=False,widget=forms.Textarea)
    rut_socio_asociado = forms.ChoiceField(choices = tuple(BLANK_CHOICE_DASH + [(choice.username, choice) for choice in get_user_model().objects.all().order_by('last_name')]), initial='', widget=forms.Select())

    class Meta:
        model = IngresoEgreso
        fields = ['folio','fecha','item_linked','tipo_mov','monto','num_cheque',
            'num_boleta_factura','nombre_proveedor','is_cheque','rut_socio_asociado',
            'estado','adjunto','voucher','caratula','comentario']

    def __init__(self,*args,**kwargs):
        # self.user = kwargs.pop('user', None)
        super(MovimientoEditFullForm,self).__init__(*args,**kwargs)
        # obj = KerRol.objects.get(tipo_rol='Aprobador')
        # self.fields['rut_aprob'].queryset = obj.roles.all().exclude(socio=self.user)
        # Article.objects.values_list('comment_id', flat=True).distinct()
        self.fields['folio'].required = False
        self.fields['tipo_mov'].label = "Tipo de Movimiento"
        self.fields['item_linked'].label = "Item"
        self.fields['num_cheque'].label = "N° Cheque"
        self.fields['num_boleta_factura'].label = "N° Boleta/Factura"
        self.fields['nombre_proveedor'].label = "Nombre Proveedor"
        self.fields['is_cheque'].label = "Cheque"
        self.fields['rut_socio_asociado'].label = "Socio Asociado"
        self.fields['rut_socio_asociado'].required = False
        self.fields['adjunto'].label = "Respaldo"
        self.fields['estado'].required = False
        self.fields['folio'].disabled = True
