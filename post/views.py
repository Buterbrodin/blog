from django.contrib.messages import success
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Post
from .forms import PostForm


def home(request):
    posts = Post.objects.all()
    status = {'info': 'primary', 'success': 'success', 'error': 'danger'}
    icons = {'info': 'bi-info-circle',
             'success': 'bi-check-circle',
             'error': 'bi-exclamation-triangle'}
    return render(request, 'home.html', {'posts': posts, 'status': status, 'icons': icons})


def about(request):
    slug = request.GET.get('slug')
    posts = Post.objects.filter(slug=slug)
    return render(request, 'about.html', {'posts': posts})


def edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'GET':
        form = PostForm(instance=post)
    else:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'The post was successfully edited!')
            return redirect('/')
    return render(request, 'edit.html', {'post': post, 'form': form})


def create(request):
    if request.method == 'GET':
        form = PostForm()
    else:
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'The post was successfully created!')
            return redirect('/')
    return render(request, 'create.html', {'form': form})


def delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    messages.add_message(request, messages.SUCCESS, 'The post was successfully deleted!')
    return redirect('/')
