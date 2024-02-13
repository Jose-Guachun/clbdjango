import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from users.models import User
from users.models.models_address import Pais, Provincia, Ciudad
from utils.funciones import ruta_foto
from utils.models import ModeloBase
from django.forms import model_to_dict

class TipoPerfil(models.Model):
    choices = (
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
        ('estudiante', 'Estudiante'),
    )

class Sexo(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')

    def __str__(self):
        return f'{self.nombre.capitalize()}'

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Sexo.objects.filter(nombre=self.nombre,status=True).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('Ya existe un registro con esta combinación única')

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        super(Sexo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Sexo"
        verbose_name_plural = u"Sexos"

class TipoProfesor(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')

    def __str__(self):
        return u'%s' % self.nombre.capitalize()

    class Meta:
        verbose_name = u"Tipo profesor"
        verbose_name_plural = u"Tipo de profesores"
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(TipoProfesor, self).save(*args, **kwargs)

#TABLAS DEBILES
class Persona(ModeloBase):
    usuario = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    nombres = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    apellido1 = models.CharField(default='', max_length=50, verbose_name=u"1er Apellido")
    apellido2 = models.CharField(default='', max_length=50, verbose_name=u"2do Apellido")
    cedula = models.CharField(default='', max_length=20, verbose_name=u"Cedula", blank=True, db_index=True)
    pasaporte = models.CharField(default='', max_length=20, blank=True, verbose_name=u"Pasaporte", db_index=True)
    fecha_nacimiento = models.DateField(verbose_name=u"Fecha de nacimiento o constitución", blank=True, null=True,)
    sexo = models.ForeignKey(Sexo, verbose_name=u'Sexo', blank=True, null=True, on_delete=models.CASCADE)
    celular = models.CharField(default='', max_length=50, verbose_name=u"Telefono movil")
    telefono = models.CharField(default='', max_length=50, verbose_name=u"Telefono fijo")
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electrónico personal")
    nacionalidad = models.ForeignKey(Pais,blank=True, null=True,related_name='nacionalidades', on_delete=models.CASCADE, verbose_name="Nacionalidad que tiene el usuario")
    pais = models.ForeignKey(Pais, blank=True, null=True, related_name='+', verbose_name=u'País residencia', on_delete=models.CASCADE)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, related_name='+',verbose_name=u"Provincia de residencia", on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, blank=True, null=True, related_name='+', verbose_name=u"Ciudad de residencia", on_delete=models.CASCADE)
    direccion = models.CharField(default='', max_length=300, verbose_name=u"Calle principal")
    direccion2 = models.CharField(default='', max_length=300, verbose_name=u"Calle secundaria")
    num_direccion = models.CharField(default='', max_length=15, verbose_name=u"Numero")
    referencia = models.CharField(default='', max_length=100, verbose_name=u"Referencia")
    foto = models.ImageField(upload_to=ruta_foto, verbose_name=u'Foto',blank=True, null=True)

    def __str__(self):
        return self.nombres_completos_inverso()

    def nombres_completos_inverso(self):
        nombre_completo = f"{self.apellido1} {self.apellido2} {self.nombres}"
        return nombre_completo.title()

    def nombres_completos_lienal(self):
        nombre_completo = f"{self.nombres} {self.apellido1} {self.apellido2}"
        return nombre_completo.title()

    def nombres_simple(self):
        nombre_completo = self.nombres.split()[0].title()
        apellido1 = self.apellido1.title()
        return f"{nombre_completo} {apellido1}"

    def get_avatar_html_40px(self):
        if self.foto:
            return f'<div class="avatar avatar-md avatar-indicators avatar-online"><img alt="avatar" src="{self.foto.url}"class="rounded-circle"/></div>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-md mt-0 ml-1"> <span class="mt-0">{siglas}</span></div>'

    def get_avatar_img_md(self):
        if self.foto:
            return f'<img src="{self.foto.url}" class="rounded-circle avatar-md me-2"/>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-md mt-0 ml-1 me-2"> <span class="mt-0">{siglas}</span></div>'

    def get_avatar_img_sm(self):
        if self.foto:
            return f'<img src="{self.foto.url}" class="rounded-circle avatar-sm me-2"/>'
        else:
            siglas=self.nombres[0].upper()+self.apellido1[0].upper()
            return f'<div class="siglas-sm mt-0 ml-1 me-2"> <span class="mt-0">{siglas}</span></div>'

    def get_foto(self):
        return self.foto.url if self.foto else ''

    def mis_perfilesusuarios(self):
        return self.perfilusuario_set.filter(status=True,activo=True)

    def mi_perfil_principal(self):
        perfiles_p=self.mis_perfilesusuarios().filter(perfilprincipal=True)
        if perfiles_p.exists():
            return perfiles_p.first()
        return self.mis_perfilesusuarios().first()

    def to_dict(self):
        persona_dict=model_to_dict(self)
        for key, value in persona_dict.items():
            if isinstance(value, datetime.date):
                persona_dict[key] = value.strftime('%Y-%m-%d')
        return persona_dict

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Persona.objects.filter((Q(cedula=self.cedula) |
                                    Q(cedula=self.pasaporte) |
                                    Q(pasaporte=self.pasaporte) |
                                    Q(pasaporte=self.cedula) |
                                    Q(usuario__email=self.email) |
                                    Q(email=self.email)), status=True).exclude(pk=self.pk).exclude(pasaporte='',pasaporte__isnull=False).exclude(cedula__isnull=False, cedula='')
        if qs.exists():
            raise NameError('Ya existe un registro con los datos que intenta registrar.')

    class Meta:
        verbose_name = u"Persona"
        verbose_name_plural = u"Personas"
        ordering = ['apellido1', 'apellido2', 'nombres']

class Profesor(ModeloBase):
    persona = models.ForeignKey(Persona, verbose_name=u"Persona", on_delete=models.CASCADE)
    fechaingreso = models.DateField( null=True, blank=True,verbose_name=u'Fecha ingreso')
    tipoprofesor = models.ForeignKey(TipoProfesor, null=True, blank=True, verbose_name=u"Tipo de profesor", on_delete=models.CASCADE)
    contrato = models.CharField(default='', max_length=50, null=True, blank=True, verbose_name=u"Contrato")
    activo = models.BooleanField(default=True, verbose_name=u"Activo")

    def perfil_usuario_activo(self):
        perfil_activo=self.perfilusuario_set.get(status=True).activo
        usuario_activo=self.persona.usuario.is_active
        return {'perfilactivo':perfil_activo,'usuarioactivo':usuario_activo}

    def __str__(self):
        return f'{self.persona}'

    class Meta:
        verbose_name = u"Profesor"
        verbose_name_plural = u"Profesores"
        ordering = ['persona']
        unique_together = ('persona',)

class Administrativo(ModeloBase):
    persona = models.ForeignKey(Persona, verbose_name=u"Persona", on_delete=models.CASCADE)
    contrato = models.CharField(default='', max_length=50, null=True, blank=True, verbose_name=u"Contrato")
    fechaingreso = models.DateField(verbose_name=u'Fecha ingreso', null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name=u"Activo")

    def perfil_usuario_activo(self):
        perfil_activo=self.perfilusuario_set.get(status=True).activo
        usuario_activo=self.persona.usuario.is_active
        return {'perfilactivo':perfil_activo,'usuarioactivo':usuario_activo}

    def __str__(self):
        return u'%s' % self.persona

    class Meta:
        verbose_name = u"Administrativo"
        verbose_name_plural = u"Administrativos"
        ordering = ['persona']
        unique_together = ('persona',)

class Estudiante(ModeloBase):
    persona = models.ForeignKey(Persona, verbose_name=u"Persona", on_delete=models.CASCADE)

    def __str__(self):
        return u'%s' % self.persona

    def perfil_usuario_activo(self):
        perfil_activo=self.perfilusuario_set.get(status=True).activo
        usuario_activo=self.persona.usuario.is_active
        return {'perfilactivo':perfil_activo,'usuarioactivo':usuario_activo}

    class Meta:
        verbose_name = u"Estudiante"
        verbose_name_plural = u"Estudiantes"
        ordering = ['persona']
        unique_together = ('persona',)

    def save(self, *args, **kwargs):
        super(Estudiante, self).save(*args, **kwargs)

class PerfilUsuario(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    administrativo = models.ForeignKey(Administrativo, blank=True, null=True, verbose_name=u'Administrativo', on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, blank=True, null=True, verbose_name=u'Profesor', on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, blank=True, null=True, verbose_name=u'Estudiante', on_delete=models.CASCADE)
    perfilprincipal = models.BooleanField(default=False, verbose_name=u'Perfil principal')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
       return f'{self.persona}'

    class Meta:
        ordering = ['persona', 'estudiante', 'administrativo', 'profesor']
        unique_together = ('persona', 'estudiante', 'administrativo', 'profesor')

    def save(self, *args, **kwargs):
        super(PerfilUsuario, self).save(*args, **kwargs)