from django.contrib.messages import success
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Post
from .forms import PostForm


def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})


def about(request):
    slug = request.GET.get('slug')
    posts = Post.objects.filter(slug=slug)
    return render(request, 'about.html', {'posts': posts})


def edit(request, slug):
    post = Post.objects.get(slug=slug)
    success = False
    if request.method == 'GET':
        form = PostForm(instance=post)
    else:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            success = True
    return render(request, 'edit.html', {'post': post, 'form': form, 'success': success})


def create(request):
    success = False
    if request.method == 'GET':
        form = PostForm()
    else:
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
    return render(request, 'create.html', {'form': form, 'success': success})


def delete(request, slug):
    post = Post.objects.get(slug=slug)
    post.delete()
    return render(request, 'delete.html')
