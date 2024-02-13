from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.postgres.apps import Unaccent
from django.utils.text import slugify
from unidecode import unidecode
from users.models import Profesor
from utils.funciones import colorEstado, text_unnaccent
from utils.models import ModeloBase

#CHOICES
TIPO_CERTIFICADO = (
    (1, 'HORIZONTAL'),
    (2, 'VERTICAL'),
)

FORMATO_CERTIFICADO = (
    (1, 'CON LOGO'),
    (2, 'CON MENCIÓN'),
)
MODALIDAD_CAPACITACION = (
    (1, u'PRESENCIAL'),
    (2, u'SEMIPRESENCIAL'),
    (3, u'VIRTUAL'),
    (4, u'OTRA'),
    (5, u'PRESENCIAL/VIRTUAL'),
)
ESTADO_FINAL_INSCRITO = (
    (1, u'PENDIENTE'),
    (2, u'APROBADO'),
    (3, u'REPROBADO')
)


class Estado(models.Model):
    choices = (
        ('planificado', 'Planificado'),
        ('en_curso', 'En curso'),
        ('finalizado', 'Finalizado'),
    )

class Nivel(models.Model):
    choices = (
        ('basico', 'Basico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    )

class Categoria(ModeloBase):
    titulo = models.CharField(default='', verbose_name=u'Título del curso', max_length=250)
    descripcion = models.TextField(verbose_name=u'Descripción de la categoría')

    def __str__(self):
        return f'{self.titulo}'

    class Meta:
        verbose_name = u"Categoria"
        verbose_name_plural = u"Categorias"
        ordering = ['-fecha_creacion']

class Periodo(ModeloBase):
    descripcion = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Nombre Periodo')
    fechainicio = models.DateField(blank=True, null=True, verbose_name='Fecha Inicio')
    fechafin = models.DateField(blank=True, null=True, verbose_name='Fecha Fin')
    vigente = models.BooleanField(default=False, verbose_name=u"Vigente")

    def idnumber(self):
        anio = ''
        if self.fechainicio and self.fechafin:
            anioini, aniofin = self.fechainicio.year, self.fechafin.year
            anio = f'{anioini}-{aniofin}' if anioini != aniofin else f'{anioini}'
        return f'PERIODO{self.id}-{anio}'

    def totalcursos(self):
        return self.cursoperiodo_set.values('id').filter(status=True).count()

    def __str__(self):
        return "{}".format(self.descripcion)

    class Meta:
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'

class Curso(ModeloBase):
    categoria=models.ForeignKey(Categoria,blank=True, null=True, on_delete=models.CASCADE, verbose_name=u'Categoría al que pertenece el curso')
    profesor=models.ForeignKey(Profesor, blank=True, null=True, on_delete=models.CASCADE, verbose_name=u'Profesor responsable de impartir el curso')
    nivel=models.CharField(max_length=20,default='basico', choices=Nivel.choices, verbose_name=u'Nivel del curso')
    estado=models.CharField(max_length=20,default='planificado', choices=Estado.choices, verbose_name=u'Estado del curso')
    titulo = models.CharField(default='', max_length=250, verbose_name=u'Título del curso')
    descripcion = models.TextField(verbose_name=u'Descripción del curso')
    fecha_inicio=models.DateField(blank=True, null=True, verbose_name='Fecha que inicia el curso')
    fecha_fin=models.DateField(blank=True, null=True, verbose_name='Fecha que finaliza el curso')
    publicado = models.BooleanField(default=False, verbose_name=u"El curso esta publicado")
    duracion_semanas = models.IntegerField(default=0, verbose_name='Duración en semanas del curso a impartir')
    cupos = models.IntegerField(default=0, verbose_name='Cupos ofertados para el curso')
    portada = models.ImageField(upload_to='cursos',blank=True, null=True, verbose_name=u'Portada del curso a impartir')

    def __str__(self):
        return f'{self.titulo} | {self.profesor}'

    def titulo_capitalizado(self):
        return f'{self.titulo.capitalize()}'

    def colorEstado(self):
        return colorEstado(self.estado)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        qs = Curso.objects.annotate(titulo_sin_acentos=Unaccent('titulo')).filter(titulo_sin_acentos__iexact=self.titulo, status=True).exclude(pk=self.pk)
        if qs.exists():
            raise NameError('Ya existe un registro con esta combinación única')

    class Meta:
        verbose_name = u"Curso"
        verbose_name_plural = u"Cursos"
        ordering = ['-fecha_creacion']

class TipoCertificacion(ModeloBase):
    prioridad = models.IntegerField(default=0, verbose_name=u'Prioridades')
    nombre = models.CharField(default='', max_length=200, verbose_name=u"Nombre")
    descripcion = models.TextField(default='', verbose_name='Descripción')
    nomslug = models.SlugField(null=True, blank=True, verbose_name='NombreSlug')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Tipo de certificación"
        verbose_name_plural = u"Tipos de certificaciones"
        ordering = ['nombre']
        unique_together = ('nombre',)

    def save(self, *args, **kwargs):
        self.nomslug = slugify(self.nombre)
        if TipoCertificacion.objects.filter(nomslug=self.nomslug).exclude(pk=self.pk).exists():
            self.nomslug += str(self.pk)
        super(TipoCertificacion, self).save(*args, **kwargs)

class CertificadosFormato(ModeloBase):
    nombre = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u"Nombre")
    tipocertificado = models.IntegerField(choices=TIPO_CERTIFICADO, default=1, verbose_name=u'Tipo Certificado')
    formato = models.IntegerField(choices=FORMATO_CERTIFICADO, default=1, verbose_name=u'Tipo Certificado')
    color = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u"Color")

    def insignias(self):
        return self.tipocertificacionformato_set.filter(status=True).order_by('tipocertificacion__prioridad')

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Formato de certificación"
        verbose_name_plural = u"Formato de certificaciones"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(CertificadosFormato, self).save(*args, **kwargs)

class TipoCertificacionFormato(ModeloBase):
    formato = models.ForeignKey(CertificadosFormato, blank=True, null=True, verbose_name=u"Formato Certificado", on_delete=models.CASCADE)
    tipocertificacion = models.ForeignKey(TipoCertificacion, blank=True, null=True, verbose_name=u"Tipo Certificación", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.formato.__str__()} - {self.tipocertificacion.__str__()}'

    class Meta:
        verbose_name = u"Formato de Insignia para certificados"
        verbose_name_plural = u"Formato de Insignia para certificados"

class CursoPeriodo(ModeloBase):
    periodo = models.ForeignKey(Periodo, verbose_name=u"Periodo", on_delete=models.CASCADE)
    tipocertificacion = models.ForeignKey(TipoCertificacion, blank=True, null=True, verbose_name=u"Tipo Certificación", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=2000, blank=True, null=True, verbose_name='Nombre')
    brevedescripcion = models.TextField(blank=True, null=True, verbose_name='Breve Descripción')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripcion')
    fechainicio = models.DateField(blank=True, null=True, verbose_name='Fecha Inicio Curso')
    fechafin = models.DateField(blank=True, null=True, verbose_name='Fecha Fin Curso')
    fechaemision = models.DateField(blank=True, null=True, verbose_name='Fecha Emisión de Certificado')
    semanas = models.IntegerField(default=0, verbose_name=u'Semana')
    horas = models.IntegerField(default=0, verbose_name=u'Dedicación (Horas)')
    cupo = models.IntegerField(default=0, verbose_name=u'Cupo')
    modalidad = models.IntegerField(choices=MODALIDAD_CAPACITACION, blank=True, null=True,verbose_name=u'Modalidad Capacitacion')
    publicar = models.BooleanField(default=False, verbose_name=u"Públicado")
    inscripcion = models.BooleanField(default=False, verbose_name=u"Habilitar Inscripcion")
    tienepromo = models.BooleanField(default=False, verbose_name=u"Tiene Promo?")
    precioanterior = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Precio Anterior")
    precio = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name=u"Precio")
    formatocertificacion = models.ForeignKey(CertificadosFormato, blank=True, null=True, verbose_name=u"Formato Certificados", on_delete=models.CASCADE)
    banner = models.FileField(upload_to='curso/banner', blank=True, null=True, verbose_name=u'Banner 1800x500px')
    portada = models.FileField(upload_to='curso/portada', blank=True, null=True, verbose_name=u'Portada')
    brochure = models.FileField(upload_to='curso/brochure', blank=True, null=True, verbose_name=u'Brochure')
    cronograma = models.FileField(upload_to='curso/cronograma', blank=True, null=True, verbose_name=u'Cronograma')
    nomslug = models.SlugField(null=True, blank=True, max_length=1000, verbose_name='NombreSlug')

    def planestudio(self):
        return self.cursoplanestudio_set.filter(status=True).order_by('descripcion')

    def planestudiocount(self):
        return self.cursoplanestudio_set.values('id').filter(status=True).count()

    def dirigidoa(self):
        return self.cursodirigidoa_set.filter(status=True).order_by('descripcion')

    def dirigidoacount(self):
        return self.cursodirigidoa_set.values('id').filter(status=True).count()

    def inscritos(self):
        return self.cursoinscrito_set.filter(status=True).order_by('-id')

    def totalinscritos(self):
        return self.cursoinscrito_set.values('id').filter(status=True).count()

    def cupolleno(self):
        return self.totalinscritos() >= self.cupo

    def docentes(self):
        return self.cursodocente_set.filter(status=True).order_by('id')

    def totaldocentes(self):
        return self.cursodocente_set.filter(status=True).count()

    def docentes_principal(self):
        return self.cursodocente_set.filter(status=True, instructorprincipal=True).order_by('id')

    def __str__(self):
        return u'%s - [%s]' % (self.nombre, self.tipocertificacion.__str__())

    class Meta:
        verbose_name = u"Curso"
        verbose_name_plural = u"Cursos"
        ordering = ('nombre',)

    def save(self, *args, **kwargs):
        self.nomslug = slugify(self.nombre)
        if CursoPeriodo.objects.filter(nomslug=self.nomslug).exclude(pk=self.pk).exists():
            self.nomslug += str(self.pk)
        super(CursoPeriodo, self).save(*args, **kwargs)

class CursoPlanEstudio(ModeloBase):
    curso = models.ForeignKey(CursoPeriodo, blank=True, null=True, verbose_name=u"Curso", on_delete=models.CASCADE)
    # titulo = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    def __str__(self):
        return u'%s - [%s]' % (self.descripcion, self.curso.__str__())

    class Meta:
        verbose_name = u"Capacitación Curso Plan de Estudio"
        verbose_name_plural = u"Capacitaciones Cursos Plan de Estudio"

    def save(self, *args, **kwargs):
        super(CursoPlanEstudio, self).save(*args, **kwargs)

class CursoDirigidoA(ModeloBase):
    curso = models.ForeignKey(CursoPeriodo, blank=True, null=True, verbose_name=u"Curso", on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    def __str__(self):
        return u'%s - [%s]' % (self.descripcion, self.curso.__str__())

    class Meta:
        verbose_name = u"Capacitación Curso Dirigido a"
        verbose_name_plural = u"Capacitaciones Cursos Dirigido a"

    def save(self, *args, **kwargs):
        super(CursoDirigidoA, self).save(*args, **kwargs)

class CursoDocente(ModeloBase):
    banner = models.FileField(upload_to='curso/docente/banner', blank=True, null=True, verbose_name=u'Banner 1800x500px')
    curso = models.ForeignKey(CursoPeriodo, verbose_name=u"Curso", on_delete=models.CASCADE)
    instructor = models.ForeignKey('users.Profesor', blank=True, null=True, verbose_name=u"Instructor", on_delete=models.CASCADE)
    nombrecurso = models.CharField(max_length=1000, default='', blank=True, null=True, verbose_name=u'Nombre de materia moodle')
    instructorprincipal = models.BooleanField(default=False, verbose_name=u"Instructor Principal")
    idcursomoodle = models.IntegerField(default=0, blank=True, null=True, verbose_name=u'Id Moodle')
    codigonumber = models.CharField(default='', blank=True, null=True, max_length=100, verbose_name=u'Codigo Moodle')

    def __str__(self):
        return u'%s' % self.instructor

    class Meta:
        verbose_name = u"Curso Docentes"
        verbose_name_plural = u"Curso Docente"

    def save(self, *args, **kwargs):
        super(CursoDocente, self).save(*args, **kwargs)

class CursoInscrito(ModeloBase):
    curso = models.ForeignKey(CursoPeriodo, verbose_name=u'Capacitación', on_delete=models.CASCADE)
    participante = models.ForeignKey('users.Persona', verbose_name=u"Persona", on_delete=models.CASCADE)
    observacion = models.TextField(default='', blank=True, null=True, verbose_name=u'Observación')
    notafinal = models.FloatField(blank=True, null=True, verbose_name=u'Nota Final')
    estado = models.IntegerField(choices=ESTADO_FINAL_INSCRITO, default=1, verbose_name=u'Estado del curso')
    rutapdf = models.FileField(upload_to='certificados', blank=True, null=True, verbose_name=f'Archivo Certificado')
    fecha_certificado = models.DateTimeField(blank=True, null=True, verbose_name='Fecha Certificado')
    codcertificado = models.CharField(max_length=1000, blank=True, null=True, verbose_name=f'Codigo de Certificado')
    emailnotificado = models.BooleanField(default=False, verbose_name=u'Notificar Email')
    fecha_emailnotifica = models.DateTimeField(blank=True, null=True, verbose_name='Fecha Email')
    generadopdf = models.BooleanField(default=False, verbose_name='Certificado Generado')
    fgeneracion = models.DateField(blank=True, null=True, verbose_name='Fecha de Generación Certificado')
    usergeneracion = models.ForeignKey('users.User', blank=True, null=True, on_delete=models.PROTECT, verbose_name=u'Usuario Generación', related_name='+')
    urlhtmlinsignia = models.CharField(blank=True, null=True, max_length=200, verbose_name=u'Url Insignia')
    namehtmlinsignia = models.CharField(blank=True, null=True, max_length=100, verbose_name=u'Html Insignia')
    encursomoodle = models.BooleanField(default=False, verbose_name=u"Enrolado Moodle?")

    def traerPago(self):
        return self.pedidodetalle_set.filter(status=True).first()

    def estado_label(self):
        if self.estado == 1:
            return 'label label-primary'
        elif self.estado == 2:
            return 'label label-success'
        elif self.estado == 3:
            return 'label label-danger'

    def __str__(self):
        return u'%s' % self.participante

    class Meta:
        verbose_name = u"Curso Inscritos"
        verbose_name_plural = u"Curso Inscritos"
        ordering = ['participante']

    def download_link(self):
        return self.rutapdf.url

    def save(self, *args, **kwargs):
        super(CursoInscrito, self).save(*args, **kwargs)

class InteresadoCurso(ModeloBase):
    curso = models.ForeignKey(CursoPeriodo, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Curso')
    first_name = models.CharField(max_length=1000, default='', blank=True, null=True, verbose_name='Nombres')
    last_name = models.CharField(max_length=1000, default='', blank=True, null=True, verbose_name='Apellidos')
    email = models.EmailField(default='', blank=True, null=True, verbose_name='Email')
    telefono = models.CharField(max_length=10, null=True, blank=True, verbose_name='Teléfonos')
    ciudad = models.ForeignKey('users.Ciudad', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Ciudad')
    mensaje = models.TextField(default='', verbose_name='Mensaje')
    atendido = models.BooleanField(default=False, verbose_name='Fue atendido?')
    fatendido = models.DateField(blank=True, null=True, verbose_name='Fecha de Atención')
    obsatendido = models.TextField(default='', verbose_name='Observación de atención', blank=True, null=True)
    formacionprofesional = models.CharField(default='', max_length=1000, blank=True, null=True,verbose_name=u"Formación profesiomal")
    # nivelinstruccion = models.ForeignKey('autenticacion.NivelInstruccion', on_delete=models.PROTECT, blank=True, null=True,verbose_name='Nivel instruccion')


    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return "{} {}".format(self.last_name, self.first_name).title()

    def telefono_formateado(self):
        telf = f'+{self.ciudad.provincia.pais.codigotelefono} {self.telefono}'
        return telf

    class Meta:
        verbose_name = u"Interesado en Curso"
        verbose_name_plural = u"Interesado en Curso"
