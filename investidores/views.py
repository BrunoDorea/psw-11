from django.shortcuts import render

from empresarios.models import Empresas

def sugestao(req):
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
        
        empresas = empresas.filter(area__in=area)

        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)

        return render(req, 'sugestao.html', {'areas': areas, 'empresas': empresas_selecionadas})