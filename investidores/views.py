from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.messages import constants
from django.http import Http404

from empresarios.models import Empresas, Documento
from .models import PropostaInvestimento

def sugestao(req):
    if not req.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    areas = Empresas.area_choices

    if req.method == 'GET':
        return render(req, 'sugestao.html', {'areas': areas})
    elif req.method == "POST":
        tipo = req.POST.get('tipo')
        area = req.POST.getlist('area')
        valor = req.POST.get('valor')

        if tipo == 'C':
            empresas = Empresas.objects.filter(tempo_existencia='+5').filter(estagio="E")
        elif tipo == 'D':
            empresas = Empresas.objects.filter(tempo_existencia__in=['-6', '+6', '+1']).exclude(estagio="E")
        # TODO: Tipo genérico
        empresas = empresas.filter(area__in=area)

        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)

        return render(req, 'sugestao.html', {'areas': areas, 'empresas': empresas_selecionadas})
    
def ver_empresa(req, id):
    empresa = Empresas.objects.get(id=id)
    documentos = Documento.objects.filter(empresa=empresa)
    # TODO: listar as métricas dinamicamente
    return render(req, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos})

def realizar_proposta(req, id):
    valor = req.POST.get('valor')
    percentual = req.POST.get('percentual')
    empresa = Empresas.objects.get(id=id)

    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    total = 0

    for pa in propostas_aceitas:
        total = total + pa.percentual

    if total + float(percentual)  > empresa.percentual_equity:
        messages.add_message(req, constants.WARNING, 'O percentual solicitado ultrapassa o percentual máximo.')
        return redirect(f'/investidores/ver_empresa/{id}')

    valuation = (100 * int(valor)) / int(percentual)

    if valuation < (int(empresa.valuation) / 2):
        messages.add_message(req, constants.WARNING, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo R${empresa.valuation/2}')
        return redirect(f'/investidores/ver_empresa/{id}')

    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=req.user,
    )
    pi.save()
    messages.add_message(req, constants.SUCCESS, f'Proposta enviada com sucesso')
    return redirect(f'/investidores/assinar_contrato/{pi.id}')

def assinar_contrato(request, id):
    pi = PropostaInvestimento.objects.get(id=id)
    
    if pi.status != "AS":
        raise Http404()
    
    if request.method == "GET":
        return render(request, 'assinar_contrato.html', {'id': id, 'pi': pi})
    elif request.method == "POST":
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        # print(request.FILES)

        pi.selfie = selfie
        pi.rg = rg
        pi.status = 'PE'
        pi.save()

        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')
