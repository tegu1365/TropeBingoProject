import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from base.forms import RegisterUserForm, BingoForm, BingoSettingsForm, UserForm
from gui.models import BingoSheet, Genre, Trope


def index(request):
    """Welcome page."""
    return render(request, 'index.html')


# ------------------------------------USER------------------------------------

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
    return render(request, 'user/registration.html', context)


@login_required(login_url='/login')
def default(request):
    return render(request, 'default.html')


@login_required(login_url='/login')
def profile(request):
    context = {
        'BingoSheet': BingoSheet.objects.filter(owner=request.user)
    }
    return render(request, 'user/profile.html', context)


@login_required(login_url='/login')
def edit_profile(request):
    try:
        user = User.objects.get(pk=request.GET['id'])
    except (KeyError, User.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')

    if request.method == 'POST':
        form = UserForm(request.POST or None, instance=user)
        if form.is_valid():
            form.save()
            return redirect(f'/profile?id={user.pk}')
    else:
        form = UserForm(instance=user)
    return render(request, 'user/user_edit.html', {'user': user, 'form': form})


# ------------------------------------BINGO------------------------------------

def generate_code(genre):
    tropes = Trope.objects.filter(genres=genre)
    random_tropes = random.sample(list(tropes), min(25, len(tropes)))
    code = ''
    for trope in random_tropes:
        code += (str(trope.id) + '|')
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
            return redirect(f'/bingo?id={bingo_sheet.pk}')
    else:
        form = BingoForm()
    return render(request, 'bingo/create_bingo.html', {'form': form})


def get_tropes(code):
    code_splited = code.split("|")
    trope_ids = [int(i) for i in code_splited[:len(code_splited) - 1]]
    tropes = []
    for i in trope_ids:
        tropes.append(Trope.objects.get(pk=i))

    table_of_tropes = []
    for i in range(0, len(tropes), 5):
        table_of_tropes.append(tropes[i:i + 5])
    return table_of_tropes


def get_checked(checked, tropes):
    checked_tropes = []
    tropes_splited = tropes.split("|")
    for i in range(0, len(tropes_splited) - 1):
        if checked[i] == '1':
            checked_tropes.append(Trope.objects.get(pk=int(tropes_splited[i])))
    return checked_tropes


@login_required(login_url='/login')
def bingo(request):
    try:
        bingo_sheet = BingoSheet.objects.get(pk=request.GET['id'])
    except (KeyError, BingoSheet.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')
    tropes = get_tropes(bingo_sheet.code)
    context = {
        'name': bingo_sheet.name,
        'private': bingo_sheet.private,
        'tropes': tropes,
        'checked_tropes': get_checked(bingo_sheet.checked, bingo_sheet.code),
        'bingo_done': bingo_sheet.bingo_done,
        'bingo': bingo_sheet
    }
    return render(request, 'bingo/bingo.html', context)


@login_required(login_url='/login')
def play_bingo(request):
    try:
        bingo_sheet = BingoSheet.objects.get(pk=request.GET['id'])
    except (KeyError, BingoSheet.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')
    tropes = get_tropes(bingo_sheet.code)
    if request.method == 'POST':
        bingo_sheet.bingo_done = request.POST.get('bingo_done', False)
        checked = ''
        for row in tropes:
            for trope in row:
                checked += '1' if request.POST.get(f'trope_{trope.id}') else '0'
        bingo_sheet.checked = checked
        bingo_sheet.save()
        return redirect(f'/bingo?id={bingo_sheet.pk}')

    tropes = get_tropes(bingo_sheet.code)

    context = {
        'name': bingo_sheet.name,
        'private': bingo_sheet.private,
        'tropes': tropes,
        'checked_tropes': get_checked(bingo_sheet.checked, bingo_sheet.code),
        'bingo_done': bingo_sheet.bingo_done,
        'bingo': bingo_sheet
    }
    return render(request, 'bingo/play_bingo.html', context)


@login_required(login_url='/login')
def bingo_settings(request):
    try:
        bingo_sheet = BingoSheet.objects.get(pk=request.GET['id'])
    except (KeyError, BingoSheet.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')

    if request.method == 'POST':
        form = BingoSettingsForm(request.POST or None, instance=bingo_sheet)
        if form.is_valid():
            form.save()
            return redirect(f'/bingo?id={bingo_sheet.pk}')
    else:
        form = BingoSettingsForm(instance=bingo_sheet)
    return render(request, 'bingo/bingo_settings.html', {'bingo': bingo_sheet, 'form': form})


@login_required(login_url='/login')
def bingo_delete(request):
    try:
        bingo_sheet = BingoSheet.objects.get(pk=request.GET['id'])
    except (KeyError, BingoSheet.DoesNotExist):
        return HttpResponseNotFound('Invalid link. No ID found.')
    if request.method == 'POST':
        bingo_sheet.delete()
        return redirect('/profile')
    return render(request, 'bingo/bingo_delete.html', {'bingo': bingo_sheet})
