import random

from django import forms

from users.models import Profesor
from utils.forms import FormBase
from cursos.models import Curso, Nivel, Categoria


class CursoForm(FormBase):
    titulo = forms.CharField(label=u'Titulo', max_length=100,required=True,
                             help_text='Escriba un título de curso de mínimo 60 caracteres.',
                             widget=forms.TextInput(attrs={'placeholder': 'Ejem. Programación en python',}))
    profesor = forms.ModelChoiceField(label=u'Profesor', required=True,
                              queryset=Profesor.objects.filter(status=True),
                              help_text='Profesor a impartir el curso',
                              widget=forms.Select(attrs={'col': '12','select2':True}))
    fecha_inicio = forms.DateField(label=u'Fecha Inicio',required=True,
                                 help_text='Seleccione la fecha de inicio del curso.',
                                 widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'col':'6'}))
    fecha_fin = forms.DateField(label=u'Fecha Fin',required=True,
                                 help_text='Seleccione la fecha que finaliza el curso',
                                 widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'col':'6'}))
    nivel = forms.ChoiceField(label=u'Nivel del curso', required=True,
                              choices=Nivel.choices,
                              help_text='Nivel de capacidad del curso',
                              widget=forms.Select(attrs={'col': '6'}))
    categoria = forms.ModelChoiceField(label=u'Categoría del curso', required=True,
                              queryset=Categoria.objects.filter(status=True),
                              help_text='Categoría al que pertenece el curso',
                              widget=forms.Select(attrs={'col': '6'}))
    descripcion = forms.CharField(label=u'Descripción', required=True,
                                  help_text='Escriba una descripción del curso a impartir.',
                                  widget=forms.Textarea(attrs={'editor': True}))
    duracion_semanas = forms.IntegerField(label=u'Duración del curso',required=True,initial=0,
                                        help_text='Cantidad de duración del curso en semanas',
                                        widget=forms.NumberInput(attrs={'col': '4'}))
    cupos = forms.IntegerField(label=u'Cupos', required=True,initial=0,
                                          help_text='Cantidad de cupos disponibles para el curso',
                                          widget=forms.NumberInput(attrs={'col': '4'}))
    publicado = forms.BooleanField(label=u'Publicado',required=False,
                                   widget=forms.CheckboxInput(attrs={'col': '4','switch':True}))

class CategoriaForm(FormBase):
    titulo = forms.CharField(label=u'Titulo', max_length=100, required=True,
                             help_text='Escriba un título de la categoría de mínimo 60 caracteres.',
                             widget=forms.TextInput(attrs={'placeholder': 'Ejem. Programación en python', }))
    descripcion = forms.CharField(label=u'Descripción', required=True,
                                  help_text='Escriba una descripción de la categoría.',
                                  widget=forms.Textarea(attrs={'rows': '4'}))
