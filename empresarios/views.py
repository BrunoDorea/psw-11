from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.messages import constants

from investidores.models import PropostaInvestimento
from .models import Empresas, Documento, Metricas

def cadastrar_empresa(req):
    # print(req.user.is_authenticated)
    if not req.user.is_authenticated:
        return redirect('/usuarios/logar')

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
        return redirect('/usuarios/logar')
    
    if req.method == "GET":
        # TODO: Realizar os filtros das empresas
        empresas = Empresas.objects.filter(user=req.user)
        return render(req, 'listar_empresas.html', {'empresas': empresas})
    
def empresa(req, id):
    empresa = Empresas.objects.get(id = id)
    
    if empresa.user != req.user:
        messages.add_message(req, constants.ERROR, "Essa empresa não é de sua responsabilidade")
        return redirect(f'/empresarios/listar_empresas/')
    
    if req.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)

        percentual_vendido = 0
        for pi in proposta_investimentos:
            if pi.status == 'PA':
                percentual_vendido = percentual_vendido + pi.percentual

        total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))
        valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0

        proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')
        return render(req, 'empresa.html', {
            'empresa': empresa,
            'documentos': documentos,
            'proposta_investimentos_enviada': proposta_investimentos_enviada,
            'percentual_vendido': int(percentual_vendido),
            'total_captado': total_captado,
            'valuation_atual': valuation_atual
        })
    
def add_doc(req, id):
    empresa = Empresas.objects.get(id=id)
    titulo = req.POST.get('titulo')
    arquivo = req.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    if empresa.user != req.user:
        messages.add_message(req, constants.ERROR, "Essa empresa não é de sua responsabilidade")
        return redirect(f'/empresarios/listar_empresas/')

    if extensao[1] != 'pdf':
        messages.add_message(req, constants.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/empresa/{id}')
    
    if not arquivo:
        messages.add_message(req, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{id}')
        
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )

    documento.save()
    messages.add_message(req, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{id}')

def excluir_dc(req, id):
    documento = Documento.objects.get(id=id)
    if documento.empresa.user != req.user:
        messages.add_message(req, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{empresa.id}')

    documento.delete()
    messages.add_message(req, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(req, id):
    empresa = Empresas.objects.get(id=id)
    titulo = req.POST.get('titulo')
    valor = req.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()

    messages.add_message(req, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def gerenciar_proposta(req, id):
    if not req.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    acao = req.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(req, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(req, constants.WARNING, 'Proposta recusada')
        pi.status = 'PR'

    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')