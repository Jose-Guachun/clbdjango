
# Django
from django.urls import path, re_path
from cursos import adm_cursos

urlpatterns = [
    #PANTALLAS PRINCIPALES
    re_path(r'^adm_cursos$',adm_cursos.ViewSet.as_view(), name='adm_cursos'),
]

