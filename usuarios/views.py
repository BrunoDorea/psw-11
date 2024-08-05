from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants

def cadastro(req):
    if req.method == "GET":
        return render(req, 'cadastro.html')
    elif req.method == "POST":
        username = req.POST.get('username')
        senha = req.POST.get('senha')
        confirmar_senha = req.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            # print(1)
            messages.add_message(req, constants.ERROR, 'As senhas não coincidem.')
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            # print(2)
            messages.add_message(req, constants.ERROR, 'A senha deve possuir pelo menos 6 caracteres.')
            return redirect('/usuarios/cadastro')
        
        users = User.objects.filter(username=username)

        if users.exists():
            # print(3)
            messages.add_message(req, constants.ERROR, 'Já existe usuário com este username.')
            return redirect('/usuarios/cadastro')


        user = User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect('/usuarios/logar')
