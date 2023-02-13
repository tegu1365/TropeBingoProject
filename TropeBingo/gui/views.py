import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.template import loader

from base.forms import RegisterUserForm, BingoForm, BingoSettingsForm, UserForm
from gui.models import BingoSheet, Genre, Trope, FriendRequest, Friends


def index(request):
    """Welcome page."""
    if request.user.is_authenticated:
        return render(request, 'default.html')
    else:
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
    all_users = get_user_model().objects.all()
    all_requests = FriendRequest.objects.filter(receiver=request.user)

    try:
        friends_list = Friends.objects.get(owner=request.user)
    except Friends.DoesNotExist:
        friends_list = None

    if friends_list:
        fr = friends_list.friends.all()
    else:
        fr = None

    context = {
        'users': all_users,
        'friend_requests': all_requests,
        'friends': fr,
        'have_fq': [user.sender for user in all_requests],
        'current_user': User.objects.get(pk=request.user.pk)
    }

    return render(request, 'default.html', context)


@login_required(login_url='/login')
def view_profile(request):
    v_user = User.objects.get(pk=request.GET['id'])
    try:
        friends_list = Friends.objects.get(owner=request.user)
    except Friends.DoesNotExist:
        friends_list = None

    fr = False
    if friends_list:
        friends = friends_list.friends.all()
        if v_user in friends:
            fr = True

    try:
        fq = FriendRequest.objects.get(sender=v_user, receiver=request.user)
    except FriendRequest.DoesNotExist:
        fq = None

    context = {
        'view_user': v_user,
        'BingoSheet': BingoSheet.objects.filter(owner=v_user),
        'friend_request': fq,
        'friends': fr
    }
    return render(request, 'user/view_profile.html', context)


@login_required(login_url='/login')
def profile(request):
    try:
        friends_list = Friends.objects.get(owner=request.user)
    except Friends.DoesNotExist:
        friends_list = None
    if friends_list:
        fr = friends_list.friends.all()
    else:
        fr = None

    context = {
        'BingoSheet': BingoSheet.objects.filter(owner=request.user),
        'friends_list': fr
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


def search(request):
    query = request.GET.get('q')
    all_requests = FriendRequest.objects.filter(receiver=request.user)

    try:
        friends_list = Friends.objects.get(owner=request.user)
    except Friends.DoesNotExist:
        friends_list = None

    if friends_list:
        fr = friends_list.friends.all()
    else:
        fr = None

    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()

    context = {
        'users': users,
        'friends': fr,
        'have_fq': [user.sender for user in all_requests],
        'current_user': User.objects.get(pk=request.user.pk)
    }
    return render(request, 'search.html', context)


# ------------------------------------BINGO------------------------------------

def generate_code(genre):
    tropes = Trope.objects.filter(genres=genre)
    random_tropes = random.sample(list(tropes), min(25, len(tropes)))
    code = ''
    for trope in random_tropes:
        code += (str(trope.id) + '|')
    return code


@login_required(login_url='/login')
def create_bingo(request):
    if request.method == 'POST':
        form = BingoForm(request.POST)
        if form.is_valid():
            bingo_sheet = form.save(commit=False)
            bingo_sheet.code = generate_code(bingo_sheet.genre)
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
def view_bingo(request):
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
    return render(request, 'bingo/view_bingo.html', context)


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


# ------------------------------------Friends------------------------------------

def sent(request):
    return render(request, 'requests/sent.html')


def already_sent(request):
    return render(request, 'requests/already_sent.html')


@login_required(login_url='/login')
def friend_request(request):
    sender = request.user
    recipient = User.objects.get(id=request.GET['id'])
    request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=recipient)
    if created:
        return HttpResponseRedirect('/sent')
    else:
        return HttpResponseRedirect('/already_sent')


@login_required(login_url='/login')
def accept_request(request):
    fq = FriendRequest.objects.get(id=request.GET['id'])
    if fq.receiver == request.user:
        Friends.make_friend(request.user, fq.sender)
        Friends.make_friend(fq.sender, fq.receiver)
        fq.delete()
        return render(request, 'requests/accept.html')
    else:
        return render(request, 'default.html')


@login_required(login_url='/login')
def delete_request(request):
    fq = FriendRequest.objects.get(id=request.GET['id'])
    if fq.receiver == request.user or fq.sender == request.user:
        fq.delete()
        return render(request, 'requests/deleted.html')
    else:
        return render(request, 'default.html')


@login_required(login_url='/login')
def remove_friend(request):
    friend = User.objects.get(pk=request.GET['id'])
    Friends.lose_friend(current_user=request.user, remove_friend=friend)
    Friends.lose_friend(current_user=friend, remove_friend=request.user)
    return render(request, 'user/remove_friend.html')


@login_required(login_url='/login')
def get_image(request):
    pass
