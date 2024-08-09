from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.messages import constants

from .models import Empresas

def cadastrar_empresa(req):
    # print(req.user.is_authenticated)
    if not req.user.is_authenticated:
        return redirect('/usuarios/login')

    if req.method == "GET":
        return render(
            req,
            'cadastrar_empresa.html',
            {
                'tempo_existencia': Empresas.tempo_existencia_choices,
                'areas': Empresas.area_choices 
            }
        )

    elif req.method == "POST":
        nome = req.POST.get('nome')
        cnpj = req.POST.get('cnpj')
        site = req.POST.get('site')
        tempo_existencia = req.POST.get('tempo_existencia')
        descricao = req.POST.get('descricao')
        data_final = req.POST.get('data_final')
        percentual_equity = req.POST.get('percentual_equity')
        estagio = req.POST.get('estagio')
        area = req.POST.get('area')
        publico_alvo = req.POST.get('publico_alvo')
        valor = req.POST.get('valor')
        pitch = req.FILES.get('pitch')
        logo = req.FILES.get('logo')

    # TODO: Realizar validação de campos

    try:
            empresa = Empresas(
                user=req.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )

            empresa.save()
    except:
        messages.add_message(req, constants.ERROR, 'Erro interno do sistema.')
        return redirect('/empresarios/cadastrar_empresa')
            
    messages.add_message(req, constants.SUCCESS, 'Empresa criada com sucesso.')
    return redirect('/empresarios/cadastrar_empresa')

def listar_empresas(req):
    if not req.user.is_authenticated:
        return redirect('/usuarios/login')
    
    if req.method == "GET":
        # TODO: Realizar os filtros das empresas
        empresas = Empresas.objects.filter(user=req.user)
        return render(req, 'listar_empresas.html', {'empresas': empresas})
    

    