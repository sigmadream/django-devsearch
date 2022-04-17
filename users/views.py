from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import search_profiles, paginate_profiles


def login_user(request):
    # page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')

        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'users/login_register.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


def register_user(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('edit-account')

        else:
            messages.success(
                request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    _profiles, _search_query = search_profiles(request)
    _custom_range, _profiles = paginate_profiles(request, _profiles, 3)
    context = {'profiles': _profiles, 'search_query': _search_query, 'custom_range': _custom_range}
    return render(request, 'users/profiles.html', context)


def user_profile(request, pk):
    _profile = Profile.objects.get(id=pk)
    _top_skills = _profile.skill_set.exclude(description__exact="")
    _other_skills = _profile.skill_set.filter(description="")
    context = {'profile': _profile, 'topSkills': _top_skills, "otherSkills": _other_skills}
    return render(request, 'users/user-profile.html', context)


@login_required(login_url='login')
def user_account(request):
    _profile = request.user.profile
    _skills = _profile.skill_set.all()
    _projects = _profile.project_set.all()
    context = {'profile': _profile, 'skills': _skills, 'projects': _projects}
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def edit_account(request):
    _profile = request.user.profile
    form = ProfileForm(instance=_profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=_profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def create_skill(request):
    _profile = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = _profile
            skill.save()
            messages.success(request, 'Skill was added successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def update_skill(request, pk):
    _profile = request.user.profile
    _skill = _profile.skill_set.get(id=pk)
    form = SkillForm(instance=_skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=_skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully!')
            return redirect('account')
    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def delete_skill(request, pk):
    _profile = request.user.profile
    _skill = _profile.skill_set.get(id=pk)
    if request.method == 'POST':
        _skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('account')
    context = {'object': _skill}
    return render(request, 'delete_template.html', context)


@login_required(login_url='login')
def inbox(request):
    _profile = request.user.profile
    _message_requests = _profile.messages.all()
    _unread_count = _message_requests.filter(is_read=False).count()
    context = {'messageRequests': _message_requests, 'unreadCount': _unread_count}
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def view_message(request, pk):
    _profile = request.user.profile
    _message = _profile.messages.get(id=pk)
    if not _message.is_read:
        _message.is_read = True
        _message.save()
    context = {'message': _message}
    return render(request, 'users/message.html', context)


def create_message(request, pk):
    _recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = _recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, 'Your message was successfully sent!')
            return redirect('user-profile', pk=_recipient.id)

    context = {'recipient': _recipient, 'form': form}
    return render(request, 'users/message_form.html', context)
