import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from base.forms import RegisterUserForm, BingoForm
from gui.models import BingoSheet, Genre, Trope


def index(request):
    """Welcome page."""
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(index)
    else:
        form = RegisterUserForm()
    context = {
        'form': form
    }
    return render(request, 'registration/registration.html', context)


@login_required(login_url='/login')
def default(request):
    return render(request, 'default.html')


@login_required(login_url='/login')
def profile(request):
    context = {
        'BingoSheet': BingoSheet.objects.filter(owner=request.user)
    }
    return render(request, 'registration/profile.html', context)


def generate_code(genre):
    tropes = Trope.objects.filter(genres=genre)
    random_tropes = random.sample(list(tropes), min(25, len(tropes)))
    code = ''
    for trope in random_tropes:
        code += (str(trope.id)+'|')
    return code


def generate_checked():
    return "0" * 25


@login_required(login_url='/login')
def create_bingo(request):
    if request.method == 'POST':
        form = BingoForm(request.POST)
        if form.is_valid():
            bingo_sheet = form.save(commit=False)
            bingo_sheet.code = generate_code(bingo_sheet.genre)
            bingo_sheet.checked = generate_checked()
            bingo_sheet.owner = request.user
            bingo_sheet.save()
            return redirect('profile/')
    else:
        form = BingoForm()
    return render(request, 'create_bingo.html', {'form': form})


def getTropes(code):
    code_splited = code.split("|")
    trope_ids = [int(i) for i in code_splited[:len(code_splited)-1]]
    tropes =[]
    for i in trope_ids:
        tropes.append(Trope.objects.get(pk=i))

    table_of_tropes = []
    for i in range(0, len(tropes), 5):
        table_of_tropes.append(tropes[i:i + 5])
    return table_of_tropes


@login_required(login_url='/login')
def bingo(request):
    try:
        bingoSheet = BingoSheet.objects.get(pk=request.GET['id'])
    except (KeyError, BingoSheet.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')
    context = {
        'name': bingoSheet.name,
        'private': bingoSheet.private,
        'tropes': getTropes(bingoSheet.code)
    }
    return render(request, 'bingo.html', context)
