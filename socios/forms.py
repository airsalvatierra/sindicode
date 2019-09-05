from django import forms
from django.conf import settings
from socios.models import User,KerSocioRol,Comuna,KerRol,KerCargaSocio,KerEventoPersona

class UserForm(forms.ModelForm):
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all().order_by('comuna'),to_field_name="comuna")
    username = forms.CharField(label='Rut')
    fec_nacimiento = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }),label='Fecha de Nacimiento',required=False)
    fec_ing_metro = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es'
                                    }))
    fec_ing_sindicato = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es'
                                    }))
    user_creacion = forms.CharField(label='',required=False,widget=forms.TextInput(attrs={'hidden': 'true'}))

    class Meta:
        model = User
        fields = [
            'username', # --> Rut del socio
            'first_name', # --> Primer Nombre
            'nom_adicional',
            'last_name', # --> Segundo Nombre
            'ape_materno',
            'email',
            'fec_nacimiento',
            'foto',
            'estado_civil',
            'dir_domicilio',
            'comuna',
            'tel_celular',
            'for_contacto',
            'num_hijos',
            'fec_ing_metro',
            'fec_ing_sindicato',
            'cargo',
            'lug_trabajo',
            'turno',
            'car_sindical',
            'is_office',
            'estado_socio',
            'user_creacion',
        ]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['last_name'].label = "Apellido Paterno"
        self.fields['email'].label = "Correo Electronico"
        self.fields['nom_adicional'].label = "Nombre(s) Adicional(es)"
        self.fields['ape_materno'].label = "Apellido Materno"
        self.fields['foto'].label = "Foto de Perfil"
        self.fields['estado_civil'].label = "Estado Civil"
        self.fields['dir_domicilio'].label = "Direccion"
        self.fields['comuna'].required = False
        self.fields['tel_celular'].label = "Telefono Celular"
        self.fields['for_contacto'].label = "Forma de Contacto Preferido"
        self.fields['num_hijos'].label = "Numero de Hijos"
        self.fields['fec_ing_metro'].label = "Fecha de Ingreso al Metro"
        self.fields['fec_ing_metro'].required = False
        self.fields['fec_ing_sindicato'].label = "Fecha de Ingreso al Sindicato"
        self.fields['fec_ing_sindicato'].required = False
        self.fields['cargo'].label = "Cargo Laboral"
        self.fields['lug_trabajo'].label = "Lugar de Trabajo"
        self.fields['turno'].label = "Turno de Trabajo"
        self.fields['car_sindical'].label = "Cargo Sindical"
        self.fields['car_sindical'].required = False
        self.fields['is_office'].label = "Personal Administrativo del Sindicato"

class EditUserForm(forms.ModelForm):
    username = forms.CharField(label='Rut')
    fec_nacimiento = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }),label='Fecha de Nacimiento',required=False)
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all().order_by('comuna'),to_field_name="comuna")
    fec_ing_metro = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es'
                                    }))
    fec_ing_sindicato = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es'
                                    }))
    # estado_socio = forms.CharField(label='',required=False,widget=forms.TextInput(attrs={'hidden': 'true'}))

    class Meta:
        model = User
        fields = [
            'username', # --> Rut del socio
            'first_name', # --> Primer Nombre
            'nom_adicional',
            'last_name', # --> Segundo Nombre
            'ape_materno',
            'email',
            'fec_nacimiento',
            'foto',
            'estado_civil',
            'dir_domicilio',
            'comuna',
            'tel_celular',
            'for_contacto',
            'num_hijos',
            'fec_ing_metro',
            'fec_ing_sindicato',
            'cargo',
            'lug_trabajo',
            'turno',
            'car_sindical',
            'is_office',
            'estado_socio',
        ]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['last_name'].label = "Apellido Paterno"
        self.fields['email'].label = "Correo Electronico"
        self.fields['nom_adicional'].label = "Nombre(s) Adicional(es)"
        self.fields['ape_materno'].label = "Apellido Materno"
        self.fields['foto'].label = "Foto de Perfil"
        self.fields['estado_civil'].label = "Estado Civil"
        self.fields['dir_domicilio'].label = "Direccion"
        self.fields['comuna'].required = False
        self.fields['tel_celular'].label = "Telefono Celular"
        self.fields['for_contacto'].label = "Forma de Contacto Preferido"
        self.fields['num_hijos'].label = "Numero de Hijos"
        self.fields['fec_ing_metro'].label = "Fecha de Ingreso al Metro"
        self.fields['fec_ing_metro'].required = False
        self.fields['fec_ing_sindicato'].label = "Fecha de Ingreso al Sindicato"
        self.fields['fec_ing_sindicato'].required = False
        self.fields['cargo'].label = "Cargo Laboral"
        self.fields['lug_trabajo'].label = "Lugar de Trabajo"
        self.fields['turno'].label = "Turno de Trabajo"
        self.fields['car_sindical'].label = "Cargo Sindical"
        self.fields['car_sindical'].required = False
        self.fields['is_office'].label = "Personal Administrativo del Sindicato"

class SocioForm(forms.ModelForm):
    username = forms.CharField(label='Rut',required=False,disabled=True)
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all().order_by('comuna'),to_field_name="comuna",required=False)
    fec_nacimiento = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }),required=False,label="Fecha Nacimiento")
    fec_ing_metro = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es'
                                    }),disabled=True,required=False,label="Fecha Ingreso al Metro")
    fec_ing_sindicato = forms.DateField(widget=forms.TextInput(attrs=
                                    {
                                        'class':'form-control',
                                        'data-provide':'datepicker',
                                        'data-date-language':'es',
                                    }),disabled=True,required=False,label="Fecha Ingreo al Sindicato")

    class Meta:
        model = User
        fields = [
            'username', # --> Rut del socio
            'first_name', # --> Primer Nombre
            'nom_adicional',
            'last_name', # --> Segundo Nombre
            'ape_materno',
            'email',
            'fec_nacimiento',
            'foto',
            'estado_civil',
            'dir_domicilio',
            'comuna',
            'tel_celular',
            'for_contacto',
            'num_hijos',
            'fec_ing_metro',
            'fec_ing_sindicato',
            'cargo',
            'lug_trabajo',
            'turno',
            'car_sindical',
        ]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['last_name'].label = "Apellido Paterno"
        self.fields['email'].label = "Correo Electronico"
        self.fields['nom_adicional'].label = "Nombre(s) Adicional(es)"
        self.fields['ape_materno'].label = "Apellido Materno"
        self.fields['foto'].label = "Foto de Perfil"
        self.fields['estado_civil'].label = "Estado Civil"
        self.fields['dir_domicilio'].label = "Direccion"
        self.fields['comuna'].required = False
        self.fields['tel_celular'].label = "Telefono Celular"
        self.fields['for_contacto'].label = "Forma de Contacto Preferido"
        self.fields['num_hijos'].label = "Numero de Hijos"
        self.fields['num_hijos'].disabled = True
        self.fields['fec_ing_metro'].label = "Fecha de Ingreso al Metro"
        self.fields['fec_ing_metro'].disabled = True
        self.fields['fec_ing_metro'].required = False
        self.fields['fec_ing_sindicato'].label = "Fecha de Ingreso al Sindicato"
        self.fields['fec_ing_sindicato'].disabled = True
        self.fields['fec_ing_sindicato'].required = False
        self.fields['cargo'].label = "Cargo Laboral"
        self.fields['cargo'].disabled = True
        self.fields['lug_trabajo'].label = "Lugar de Trabajo"
        self.fields['lug_trabajo'].disabled = True
        self.fields['turno'].label = "Turno de Trabajo"
        self.fields['turno'].disabled = True
        self.fields['car_sindical'].label = "Cargo Sindical"
        self.fields['car_sindical'].disabled = True
        self.fields['car_sindical'].required = False

class RolesForm(forms.ModelForm):
    socio = forms.CharField()
    # nombre = forms.CharField()
    # ape_paterno = forms.CharField(widget=forms.TextInput(attrs={'label': 'Apellido Paterno'}))
    # ape_materno = forms.CharField(widget=forms.TextInput(attrs={'label': 'Apellido Materno'}))
    # roles = forms.MultipleChoiceField(choices=ROLES,required=False,widget=forms.CheckboxSelectMultiple)
    rol = forms.ModelMultipleChoiceField(queryset=KerRol.objects.all().order_by('tipo_rol'),to_field_name="tipo_rol")

    class Meta:
        model = KerSocioRol
        fields = ['socio','rol']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        obj = KerRol.objects.get(tipo_rol='Administracion')
        self.fields['socio'].queryset = obj.roles.all()

class CargaSocioForm(forms.ModelForm):
    comentario = forms.CharField(required=False,widget=forms.Textarea)

    class Meta:
        model = KerCargaSocio
        fields = ['socio','tipo_carga','nombre','ape_paterno','ape_materno','edad','comentario']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['socio'].hidden = True
        self.fields['tipo_carga'].label = 'Tipo de Carga'
        self.fields['ape_paterno'].label = 'Apellido Paterno'
        self.fields['ape_materno'].label = 'Apellido Materno'

class EventoPersonaForm(forms.ModelForm):
    class Meta:
        model = KerEventoPersona
        fields = ['socio','tipo_evento','fec_evento','detalle','adjunto','rut_usuario','nombre_usuario']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['socio'].hidden = True
        self.fields['tipo_evento'].label = 'Tipo de Evento'
        self.fields['fec_evento'].label = 'Fecha Evento'
        self.fields['rut_usuario'].required = False
        self.fields['nombre_usuario'].required = False
