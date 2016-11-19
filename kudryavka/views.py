from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils.http import urlencode
from kudryavka.models import (
    Post, Project, PostTag, ProjectCategory,
    State, PostType, Priority, Setting, Archive
)
from django.db.models import F, Q
from django.utils import timezone
from kudryavka.forms import PostInlineForm, NoteForm, TodoForm, inlineformset_factory
from django.forms import inlineformset_factory
from django.core.urlresolvers import reverse

def index(request):

    title = "Kudryavka"
    text = "Welcome to Kudryavka, a project management application"
    return render(request, 'kudryavka/index.html', {
        'text': text,
        'title': title
    })

def project_index(request):

    title = "Projects"
    text = "List of projects"
    projects = Project.objects.active()

    for project in projects:
        project.notes = Post.objects.notes().by_project(project.pk).count()
        project.todos = Post.objects.todos().by_project(project.pk).count()
        project.total = Post.objects.by_project(project.pk).count()

    return render(request, 'kudryavka/projects.html', {
        'projects': projects,
        'title': title,
        'text': text
    })

def project_view(request, project_id):
    project = Project.objects.get(pk=project_id)
    if project:
        root = Post.objects.by_project(project.pk).filter(level=0).first()
        if root:
            children = root.get_descendants(include_self=True).order_by('lft')
            for child in children:
                child.child_count = child.children.count()
                child.done_count = Post.objects.todos().done().filter(parent=child).count()
        else:
            children = root

    return render(request, 'kudryavka/notebook.html', {
        'project': project,
        'posts': children,
    })

