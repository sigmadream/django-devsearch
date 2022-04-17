from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from .utils import search_projects, paginate_projects


def projects(request):
    _projects, _search_query = search_projects(request)
    _custom_range, _projects = paginate_projects(request, _projects, 6)
    context = {'projects': _projects, 'search_query': _search_query, 'custom_range': _custom_range}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    _project = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = _project
        review.owner = request.user.profile
        review.save()

        _project.get_vote_count

        messages.success(request, 'Your review was successfully submitted!')
        return redirect('project', pk=_project.id)

    return render(request, 'projects/single-project.html', {'project': _project, 'form': form})


@login_required(login_url="login")
def create_project(request):
    _profile = request.user.profile
    form = ProjectForm()

    if request.method == 'POST':
        new_tags = request.POST.get('newtags').replace(',', " ").split()
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = _profile
            project.save()

            for tag in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')

    context = {'form': form}
    return render(request, "projects/project_form.html", context)


@login_required(login_url="login")
def update_project(request, pk):
    _profile = request.user.profile
    _project = _profile.project_set.get(id=pk)
    form = ProjectForm(instance=_project)

    if request.method == 'POST':
        new_tags = request.POST.get('newtags').replace(',', " ").split()

        form = ProjectForm(request.POST, request.FILES, instance=_project)
        if form.is_valid():
            _project = form.save()
            for tag in new_tags:
                tag, created = Tag.objects.get_or_create(name=tag)
                _project.tags.add(tag)

            return redirect('account')

    context = {'form': form, 'project': _project}
    return render(request, "projects/project_form.html", context)


@login_required(login_url="login")
def delete_project(request, pk):
    _profile = request.user.profile
    _project = _profile.project_set.get(id=pk)
    if request.method == 'POST':
        _project.delete()
        return redirect('projects')
    context = {'object': _project}
    return render(request, 'delete_template.html', context)
