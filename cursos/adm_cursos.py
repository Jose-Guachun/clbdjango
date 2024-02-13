import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views import View

from cursos.forms import CursoForm, CategoriaForm
from cursos.models import Curso, Categoria
from users.models import Profesor
from users.templatetags.extra_tags import encrypt
from utils.funciones import Paginacion


class ViewSet(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action')
        request.session['viewactivo'] = 'cursos'
        if action:
            if action == 'addcurso':
                try:
                    context['title'] = 'Adicionar curso'
                    context['form']=form=CursoForm()
                    template_name = 'adm_cursos/formularios/formcurso.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": str(ex)})

            if action == 'editcurso':
                try:
                    #PARAMETROS DE CABECERA
                    context['id']=id=int(encrypt(request.GET['id']))
                    curso=Curso.objects.get(pk=id)
                    context['title'] = f'Editar Curso'
                    context['form']=CursoForm(initial=model_to_dict(curso))
                    context['head_title']=curso.titulo
                    template_name = 'adm_cursos/formcurso.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": str(ex)})

            if action == 'buscarprofesor':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    qsprofesor = Profesor.objects.filter(status=True, activo=True)
                    if len(s) == 1:
                        qsprofesor = qsprofesor.filter((Q(persona__nombres__icontains=q) |
                                                        Q(persona__apellido1__icontains=q) |
                                                        Q(persona__cedula__icontains=q) |
                                                        Q(persona__apellido2__icontains=q) |
                                                        Q(persona__cedula__contains=q)),
                                                        Q(persona__status=True)).distinct()[:15]
                    elif len(s) == 2:
                        qsprofesor = qsprofesor.filter((Q(persona__apellido1__contains=s[0]) & Q(persona__apellido2__contains=s[1])) |
                                                     (Q(persona__nombres__icontains=s[0]) & Q(persona__nombres__icontains=s[1])) |
                                                     (Q(persona__nombres__icontains=s[0]) & Q(persona__apellido1__contains=s[1]))).filter(
                            profesor__status=True).distinct()[:15]
                    else:
                        qsprofesor = qsprofesor.filter(
                            (Q(persona__nombres__contains=s[0]) & Q(persona__apellido1__contains=s[1]) & Q(persona__apellido2__contains=s[2])) |
                            (Q(persona__nombres__contains=s[0]) & Q(persona__nombres__contains=s[1]) & Q(
                                persona__apellido1__contains=s[2]))).filter(persona__status=True).distinct()[:15]

                    resp = [{'id': qs.pk, 'text': f"{qs.persona.nombres_completos_inverso()}",
                             'documento': qs.persona.cedula,
                             'foto': qs.persona.get_foto()} for qs in qsprofesor]
                    return HttpResponse(json.dumps({'status': True, 'results': resp}))
                except Exception as ex:
                    return JsonResponse({"result": False, "mensaje": str(ex)})

            if action == 'categorias':
                try:
                    context['title'] = 'Categorias'
                    filtro, url_vars, search = Q(status=True), f'', request.GET.get('s')
                    if search:
                        context['s'] = search
                        url_vars += '&s=' + search
                        filtro = filtro & Q(titulo__icontains=search)

                    categorias = Categoria.objects.filter(filtro)
                    # PAGINADOR
                    paginator = Paginacion(categorias, 10)
                    page = int(request.GET.get('page', 1))
                    paginator.rangos_paginado(page)
                    context['paging'] = paging = paginator.get_page(page)
                    context['listado'] = paging.object_list
                    template_name = 'adm_cursos/categorias.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"result": "bad", "mensaje": str(ex)})

            #MODALES
            if action == 'addcategoria':
                try:
                    form = CategoriaForm()
                    context['form'] = form
                    template = get_template("adm_cursos/formularios/formcategoria.html")
                    return JsonResponse({"result": True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje':f'{ex}'})

            if action == 'editcategoria':
                try:
                    context['id']=id=int(encrypt(request.GET['id']))
                    categoria=Categoria.objects.get(pk=id)
                    form = CategoriaForm(initial=model_to_dict(categoria))
                    context['form'] = form
                    template = get_template("adm_cursos/formularios/formcategoria.html")
                    return JsonResponse({"result": True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje':f'{ex}'})

            return HttpResponseRedirect(request.path)
        else:
            try:
                context['title'] = 'Cursos'
                filtro, url_vars, search=Q(status=True), f'', request.GET.get('s')
                if search:
                    context['s']=search
                    url_vars += '&s=' + search
                    filtro = filtro & Q(titulo__icontains=search)

                cursos=Curso.objects.filter(filtro)
                #PAGINADOR
                paginator=Paginacion(cursos,10)
                page=int(request.GET.get('page',1))
                paginator.rangos_paginado(page)
                context['paging'] = paging =paginator.get_page(page)
                context['listado']=paging.object_list
                template_name = 'adm_cursos/cursos.html'
                return render(request, template_name, context)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})


    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        persona = request.session['persona']
        if action == 'addcurso':
            try:
                form = CursoForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                curso=Curso(titulo=form.cleaned_data['titulo'],
                            descripcion=form.cleaned_data['descripcion'],
                            fecha_inicio=form.cleaned_data['fecha_inicio'],
                            fecha_fin=form.cleaned_data['fecha_fin'],
                            duracion_semanas=form.cleaned_data['duracion_semanas'],
                            cupos=form.cleaned_data['cupos'],
                            categoria=form.cleaned_data['categoria'],
                            nivel=form.cleaned_data['nivel'],
                            publicado=form.cleaned_data['publicado'],
                            profesor=form.cleaned_data['profesor'],
                            )
                curso.save(request)
                url_redirect = reverse('cursos:adm_cursos')
                return JsonResponse({"result": True, "url_redirect":url_redirect})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        if action == 'editcurso':
            try:
                form = CursoForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                curso=Curso.objects.get(pk=int(encrypt(request.POST['id'])))
                curso.titulo=form.cleaned_data['titulo']
                curso.descripcion=form.cleaned_data['descripcion']
                curso.fecha_inicio=form.cleaned_data['fecha_inicio']
                curso.fecha_fin=form.cleaned_data['fecha_fin']
                curso.duracion_semanas=form.cleaned_data['duracion_semanas']
                curso.cupos=form.cleaned_data['cupos']
                curso.categoria=form.cleaned_data['categoria']
                curso.nivel=form.cleaned_data['nivel']
                curso.publicado=form.cleaned_data['publicado']
                curso.profesor=form.cleaned_data['profesor']
                curso.save(request)
                url_redirect = reverse('cursos:adm_cursos')
                return JsonResponse({"result": True, "url_redirect":url_redirect})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        if action == 'delcurso':
            try:
                instancia = Curso.objects.get(pk=int(encrypt(request.POST['id'])))
                instancia.status = False
                instancia.save(request)
                res_json = {"result": True}
            except Exception as ex:
                res_json = {'result': False, "mensaje": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        if action == 'addcategoria':
            try:
                form = CategoriaForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    f_error=[{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': False, "form": f_error,"mensaje": "Error en el formulario"})

                instancia = Categoria(titulo=form.cleaned_data['titulo'],
                                      descripcion=form.cleaned_data['descripcion'])
                instancia.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, "mensaje": 'Error: {}'.format(ex)})

        if action == 'editcategoria':
            try:
                form = CategoriaForm(request.POST)
                if not form.is_valid():
                    transaction.set_rollback(True)
                    f_error=[{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({'result': False, "form": f_error,"mensaje": "Error en el formulario"})
                instancia= Categoria.objects.get(pk=int(encrypt(request.POST['id'])))
                instancia.titulo = form.cleaned_data['titulo']
                instancia.descripcion= form.cleaned_data['descripcion']
                instancia.save(request)
                return JsonResponse({"result": True}, safe=False)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, "mensaje": 'Error: {}'.format(ex)})

        if action == 'delcategoria':
            try:
                instancia = Categoria.objects.get(pk=int(encrypt(request.POST['id'])))
                instancia.status = False
                instancia.save(request)
                res_json = {"error": False}
            except Exception as ex:
                res_json = {'error': True, "message": "Error: {}".format(ex)}
            return JsonResponse(res_json, safe=False)

        return JsonResponse({"result": False, "mensaje": u"Solicitud Incorrecta."})