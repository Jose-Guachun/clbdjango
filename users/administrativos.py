import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View

from users.forms import DocenteForm, GestionUsuarioForm, AdministrativoForm
from users.models import Persona, Administrativo
from users.templatetags.extra_tags import encrypt
from utils.funciones import Paginacion, filtro_persona_generico
from utils.generic_save import add_user_with_profile, edit_persona_with_profile, gestionarusuario


class ViewSet(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['action'] = action = request.GET.get('action')
        request.session['viewactivo'] = 'administrativos'
        if action:
            if action == 'addadministrativo':
                try:
                    context['title'] = 'Adicionar administrativo'
                    context['form']=AdministrativoForm()
                    template_name = 'administrativos/formularios/formadministrativo.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    messages.error(request,f'{ex}')

            if action == 'editadministrativo':
                try:
                    context['title'] = 'Adicionar docente'
                    context['id']=id=int(encrypt(request.GET['id']))
                    d_iniciales={}
                    administrativo=Administrativo.objects.select_related('persona').get(id=id)
                    persona=administrativo.persona
                    d_iniciales.update(model_to_dict(administrativo))
                    d_iniciales.update(model_to_dict(persona))
                    context['form']=form=AdministrativoForm(instancia=administrativo.persona,initial=d_iniciales)
                    form.edit()
                    template_name = 'administrativos/formadministrativo.html'
                    return render(request, template_name, context)
                except Exception as ex:
                    messages.error(request,f'{ex}')

            if action == 'gestionarusuario':
                try:
                    id=int(encrypt(request.GET['id']))
                    instancia=Administrativo.objects.select_related().get(id=id)
                    datos=instancia.perfil_usuario_activo()
                    form = GestionUsuarioForm(initial={'perfilactivo':datos['perfilactivo'],
                                                       'usuarioactivo':datos['usuarioactivo']})
                    context['persona_s'] = instancia.persona
                    context['id']=id
                    context['form'] = form
                    template = get_template("docentes/formularios/formgestionusuario.html")
                    return JsonResponse({"result": True, 'data': template.render(context)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': f'{ex}'})
            messages.error(request, f'Solicitud incorrecta')
            return HttpResponseRedirect(request.path)
        else:
            try:
                context['title'] = 'Administrativos'
                filtro, url_vars, search=Q(status=True), f'', request.GET.get('s')
                if search:
                    context['s']=search
                    url_vars += '&s=' + search
                    filtro = filtro_persona_generico(filtro, search)

                cursos=Administrativo.objects.filter(filtro)
                #PAGINADOR
                paginator=Paginacion(cursos,10)
                page=int(request.GET.get('page',1))
                paginator.rangos_paginado(page)
                context['paging'] = paging =paginator.get_page(page)
                context['listado']=paging.object_list
                template_name = 'administrativos/view.html'
                return render(request, template_name, context)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        persona = request.session['persona']
        if action == 'addadministrativo':
            try:
                form = AdministrativoForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data=add_user_with_profile(request,form,'administrativo')
                return JsonResponse({"result": True, "url_redirect":request.path})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        if action == 'editadministrativo':
            try:
                administrativo=Administrativo.objects.get(id=int(encrypt(request.POST['id'])))
                form = DocenteForm(request.POST, instancia=administrativo.persona)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                data=edit_persona_with_profile(request,form,'docente', administrativo.persona.id)
                return JsonResponse({"result": True, "url_redirect":request.path})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        if action == 'gestionarusuario':
            try:
                form = GestionUsuarioForm(request.POST)
                if not form.is_valid():
                    form_e = [{k: v[0]} for k, v in form.errors.items()]
                    return JsonResponse({"result": False, "mensaje": 'Conflicto con formulario', "form": form_e})
                instancia = Administrativo.objects.get(pk=int(encrypt(request.POST['id'])))
                gestionarusuario(request,form,instancia)
                return JsonResponse({"result": True, "url_redirect":request.path})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": str(ex)})

        return JsonResponse({"result": False, "mensaje": u"Solicitud Incorrecta."})