from django import forms
from .models import AsistenciaEnc, AsistenciaDet

TIPOS_ASISTENCIA = (
    ('Asamblea de Delegados','Asamblea de Delegados'),
    ('Asamblea de Comision','Asamblea de Comision'),
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

TIPOS_ASISTENCIA_CE = (
    ('Asamblea General Ordinaria','Asamblea General Ordinaria'),
    ('Asamblea General Extraordinaria','Asamblea General Extraordinaria'),
    ('Asamblea de Votación','Asamblea de Votación'),
)

class AsistenciaEncForm(forms.ModelForm):
    usuario = forms.CharField(required=False)
    descripcion = forms.CharField(required=False,widget=forms.Textarea)
    fec_evento = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    class Meta:
        model = AsistenciaEnc
        fields = 'usuario','fec_evento','tipo_evento','descripcion','archivo','acta'
        labels = {
            'username': 'Rut','email':'Correo Electronico'
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['tipo_evento'] = forms.ChoiceField(choices=TIPOS_ASISTENCIA)
        self.fields['tipo_evento'].label = "Tipo Evento"
        self.fields['fec_evento'].label = "Fecha Evento"

class AsistenciaDetForm(forms.ModelForm):
    fec_evento = forms.DateField(widget=forms.DateInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    },format='%d-%m-%Y'),label='Fecha Evento',disabled=True)
    comentario = forms.CharField(widget=forms.Textarea,required=False)

    class Meta:
        model = AsistenciaDet
        fields = ['fec_evento','rut_socio','nombre','apellido','email',
                'est_asistencia','est_notificacion','est_justificacion',
                'est_apelacion','comentario']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['fec_evento'].disabled = True
        self.fields['rut_socio'].label = "Rut Socio"
        self.fields['rut_socio'].disabled = True
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].label = "Email Notificacion"
        self.fields['email'].disabled = True
        self.fields['est_asistencia'].label = "Estado Asistencia"
        self.fields['est_asistencia'].disabled = True
        self.fields['est_notificacion'].label = "Estado Notificacion"
        self.fields['est_notificacion'].disabled = True
        self.fields['est_justificacion'].label = "Estado Justificacion"
        self.fields['est_justificacion'].disabled = True
        self.fields['est_apelacion'].label = "Estado Apelacion"
        self.fields['est_apelacion'].disabled = True

class AsistenciaDetCEForm(forms.ModelForm):
    fec_evento = forms.DateField(widget=forms.DateInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    },format='%d-%m-%Y'),label='Fecha Evento',disabled=True)
    comentario = forms.CharField(widget=forms.Textarea,required=False)

    class Meta:
        model = AsistenciaDet
        fields = ['fec_evento','rut_socio','nombre','apellido','email',
                'est_asistencia','est_notificacion','est_justificacion',
                'est_apelacion','comentario','arc_justificacion']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['fec_evento'].disabled = True
        self.fields['rut_socio'].label = "Rut Socio"
        self.fields['rut_socio'].disabled = True
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].label = "Email Notificacion"
        self.fields['email'].disabled = True
        self.fields['est_asistencia'].label = "Estado Asistencia"
        self.fields['est_asistencia'].disabled = True
        self.fields['est_notificacion'].label = "Estado Notificacion"
        self.fields['est_notificacion'].disabled = True
        self.fields['est_justificacion'].label = "Estado Justificacion"
        self.fields['arc_justificacion'].label = "Archivo Justificacion"
        self.fields['est_apelacion'].label = "Estado Apelacion"        

class AsistenciaEncFormCE(forms.ModelForm):
    usuario = forms.CharField(required=False)
    # tipo_evento = forms.CharField(choices=TIPOS_ASISTENCIA_CE,widget=forms.Select())
    descripcion = forms.CharField(required=False,widget=forms.Textarea)
    fec_evento = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }))
    class Meta:
        model = AsistenciaEnc
        fields = 'usuario','fec_evento','tipo_evento','descripcion','archivo','acta'
        labels = {
            'username': 'Rut','email':'Correo Electronico'
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['tipo_evento'] = forms.ChoiceField(choices=TIPOS_ASISTENCIA_CE)
        self.fields['tipo_evento'].label = "Tipo Evento"
        self.fields['fec_evento'].label = "Fecha Evento"
