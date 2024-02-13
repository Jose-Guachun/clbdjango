from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models.models_modulos import Modulo, ModuloGrupo, ModuloCategoria
from utils.models import ModeloBaseAdmin
# Register your models here.
from users.models import User, Persona, Pais, Provincia, Ciudad, Sexo, Profesor, TipoProfesor


class UserAdmin(ModeloBaseAdmin):
    list_display=(
        'username',
        'email',
        'first_name',
        'last_name',
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',

    )
    list_filter=('is_staff',)
    filter_horizontal = ()

class ModuloAdmin(ModeloBaseAdmin):
    list_display = ('url', 'nombre', 'icono', 'descripcion', 'activo')
    ordering = ('url',)
    search_fields = ('url', 'nombre', 'descripcion', 'categorias')
    list_filter = ('activo',)

class ModuloGrupoAdmin(ModeloBaseAdmin):
    list_display = ('nombre', 'prioridad', 'descripcion')
    ordering = ('prioridad', 'nombre')
    search_fields = ('nombre', 'descripcion')

class ModuloCategoriaAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class PersonaAdmin(ModeloBaseAdmin):
    list_display = ('nombres',)
    ordering = ('nombres',)
    search_fields = ('nombres',)

class PaisAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class ProvinciaAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class CiudadAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class SexoAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

class ProfesorAdmin(ModeloBaseAdmin):
    list_display = ('persona',)
    ordering = ('persona',)
    search_fields = ('persona',)

class TipoProfesorAdmin(ModeloBaseAdmin):
    list_display = ('nombre',)
    ordering = ('nombre',)
    search_fields = ('nombre',)

admin.site.register(User, UserAdmin,)
# admin.site.unregister(Group)
admin.site.register(Modulo, ModuloAdmin)
admin.site.register(ModuloGrupo, ModuloGrupoAdmin)
admin.site.register(ModuloCategoria, ModuloCategoriaAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Sexo, SexoAdmin)
admin.site.register(Profesor, ProfesorAdmin)
admin.site.register(TipoProfesor, TipoProfesorAdmin)