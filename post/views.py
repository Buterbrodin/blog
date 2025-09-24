from django.contrib.messages import success
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Post
from .forms import PostForm, CustomLoginForm, CustomRegisterForm, CustomPasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordResetView, LogoutView, PasswordChangeView
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages import get_messages

status = {'info': 'primary', 'success': 'success', 'error': 'danger'}
icons = {'info': 'bi-info-circle',
         'success': 'bi-check-circle',
         'error': 'bi-exclamation-triangle'}


def home(request):
    if request.GET.get('user_posts') == 'true' and request.user.is_authenticated:
        posts = Post.objects.filter(author=request.user)
    elif request.GET.get('tag'):
        tag = request.GET.get('tag')
        posts = Post.objects.filter(tags__name__contains=tag)
    elif request.GET.get('title'):
        posts = Post.objects.filter(title__icontains=request.GET['title'])
    else:
        posts = Post.objects.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'post/home.html', {'posts': posts, 'status': status, 'icons': icons})


def view_user_posts(request):
    posts = Post.objects.filter(author=request.user)


def about(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'post/about.html', {'post': post})


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
    return render(request, 'post/edit.html', {'post': post, 'form': form})


def create(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.add_message(request, messages.SUCCESS, 'The post was successfully created!')
            return redirect('/')
    return render(request, 'post/create.html', {'form': form})


def delete(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        messages.add_message(request, messages.SUCCESS, 'The post was successfully deleted!')
    return redirect('/')


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in!')
        return super().form_valid(form)


class CustomRegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully registered a new account!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out!")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully changed the password!')
        return super().form_valid(form)
