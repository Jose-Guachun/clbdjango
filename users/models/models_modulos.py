from django.db import models
from utils.models import ModeloBase
from django.contrib.auth.models import Group

class ModuloCategoria(ModeloBase):
    nombre = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Nombre')
    prioridad = models.IntegerField(null=True, blank=True)
    icono = models.CharField(default='', max_length=100, verbose_name=u'Icono')


    def __str__(self):
        return '{} {}'.format(self.nombre, self.prioridad)

    def modulos(self):
        return self.modulo_set.filter(status=True)

    def modulos_slugs(self):
        return self.modulo_set.filter(status=True).values_list('slug',flat=True)

    class Meta:
        verbose_name = 'Categorias de Módulos'
        verbose_name_plural = 'Categorias de Módulos'
        ordering = ('prioridad', 'nombre')


class Modulo(ModeloBase):
    categoria = models.ForeignKey(ModuloCategoria,blank=True, null=True, verbose_name=u'Categorias', on_delete=models.CASCADE)
    url = models.CharField(default='', max_length=100, verbose_name=u'URL')
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    slug = models.CharField(default='', max_length=100, verbose_name=u'Nombre corto sin espacios.')
    icono = models.CharField(default='', max_length=100, verbose_name=u'Icono')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')
    api = models.BooleanField(default=False, verbose_name=u'Activo para API')
    api_key = models.CharField(default='', blank=True, null=True, max_length=100, verbose_name=u'Clave de API')
    roles = models.TextField(default='', blank=True, null=True, verbose_name=u'Roles')
    submodulo = models.BooleanField(default=False, verbose_name=u'¿Es submódulo?')

    def __str__(self):
        return u'%s (/%s)' % (self.nombre, self.url)

    class Meta:
        verbose_name = u"Modulo"
        verbose_name_plural = u"Modulos"
        ordering = ['nombre']
        unique_together = ('url',)

    def save(self, *args, **kwargs):
        self.url = self.url.strip()
        self.nombre = self.nombre.strip()
        self.icono = self.icono.strip()
        self.descripcion = self.descripcion.strip()
        if self.api:
            if not self.api_key:
                raise NameError(u'Ingrese el nombre clave del módulo de la API.')
            self.api_key = self.api_key.strip().upper()
        if self.id:
            if self.api and Modulo.objects.values("id").filter(api_key=self.api_key).exclude(pk=self.id).exists():
                raise NameError(u'Nombre clave del módulo de la API existente.')
        else:
            if self.api and Modulo.objects.values("id").filter(api_key=self.api_key).exists():
                raise NameError(u'Nombre clave del módulo de la API existente.')
        super(Modulo, self).save(*args, **kwargs)


class ModuloGrupo(ModeloBase):
    nombre = models.CharField(default='', max_length=100, verbose_name=u' Nombre')
    descripcion = models.CharField(default='', max_length=200, verbose_name=u'Descripción')
    modulos = models.ManyToManyField(Modulo, verbose_name=u'Modulos')
    grupos = models.ManyToManyField(Group, verbose_name=u'Grupos')
    prioridad = models.IntegerField(default=0, verbose_name=u'Prioridad')

    def __str__(self):
        return u'%s' % self.nombre

    def modulos_activos(self):
        return self.modulos.filter(activo=True)

    def modules(self):
        return self.modulos.all()

    def groups(self):
        return self.grupos.all()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip().capitalize()
        self.descripcion = self.descripcion.strip().capitalize()
        super(ModuloGrupo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Grupo de modulos'
        verbose_name_plural = u"Grupos de modulos"
        ordering = ['nombre']
        unique_together = ('nombre',)
