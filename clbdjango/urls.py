from django.contrib import admin
from django.urls import path

from django.contrib import admin
#Importacion de settings y static para generar ruta en templates
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

urlpatterns = [
    #ADMIN
    path('admin/', admin.site.urls),

    # CONTROL DE ACCESO USUARIO
    re_path(r'^', include(('users.urls', 'users'), namespace='users')),

    #MODULO CURSOS
    re_path(r'^', include(('cursos.urls', 'cursos'), namespace='cursos'))

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
