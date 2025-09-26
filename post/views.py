from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CustomLoginForm, CustomRegisterForm, CustomPasswordChangeForm, CommentForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login

status = {'info': 'primary', 'success': 'success', 'error': 'danger'}
icons = {'info': 'bi-info-circle',
         'success': 'bi-check-circle',
         'error': 'bi-exclamation-triangle'}


class HomeView(ListView):
    '''Home page view'''
    model = Post
    template_name = 'post/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        qs = Post.objects.all()
        if self.request.GET.get('user_posts') == 'true':
            if self.request.user.is_authenticated:
                qs = qs.filter(author=self.request.user)
            else:
                qs = Post.objects.none()
        elif self.request.GET.get('tag'):
            tag = self.request.GET.get('tag')
            qs = qs.filter(tags__name__icontains=tag)
        elif self.request.GET.get('content'):
            content = self.request.GET.get('content')
            qs = qs.filter(
                Q(content__icontains=content) | Q(title__icontains=content) | Q(tags__name__icontains=content))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = status
        context['icons'] = icons
        return context


# def home(request):
#     if request.GET.get('user_posts') == 'true' and request.user.is_authenticated:
#         posts = Post.objects.filter(author=request.user)
#     elif request.GET.get('tag'):
#         tag = request.GET.get('tag')
#         posts = Post.objects.filter(tags__name__contains=tag)
#     elif request.GET.get('title'):
#         posts = Post.objects.filter(title__icontains=request.GET['title'])
#     else:
#         posts = Post.objects.all()
#     paginator = Paginator(posts, 5)
#     page_number = request.GET.get('page')
#     posts = paginator.get_page(page_number)
#     return render(request, 'post/home.html', {'posts': posts, 'status': status, 'icons': icons})


class PostDetailView(LoginRequiredMixin, DetailView):
    '''Post detail view'''
    model = Post
    template_name = 'post/about.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = status
        context['icons'] = icons
        return context


# def about(request, slug):
#     post = get_object_or_404(Post, slug=slug)
#     return render(request, 'post/about.html', {'post': post})


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Edit post view'''
    model = Post
    form_class = PostForm
    template_name = 'post/edit.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'The post was successfully edited!')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Edit comment view'''
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment.html'

    def get_success_url(self):
        return self.get_object().post.get_absolute_url()

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or self.request.user.is_superuser


# def edit(request, slug):
#     post = get_object_or_404(Post, slug=slug)
#     if request.method == 'GET':
#         form = PostForm(instance=post)
#     else:
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():
#             form.save()
#             messages.add_message(request, messages.SUCCESS, 'The post was successfully edited!')
#             return redirect('/')
#     return render(request, 'post/edit.html', {'post': post, 'form': form})


class PostCreateView(LoginRequiredMixin, CreateView):
    '''Post create view'''
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('home')
    template_name = 'post/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The post was successfully created!')
        return super().form_valid(form)


# def create(request):
#     form = PostForm()
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             form.save_m2m()
#             messages.add_message(request, messages.SUCCESS, 'The post was successfully created!')
#             return redirect('/')
#     return render(request, 'post/create.html', {'form': form})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Post delete view'''
    model = Post
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        messages.success(request, "The post was successfully deleted!")
        return super().post(request, *args, **kwargs)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


# def delete(request, slug):
#     if request.method == 'POST':
#         post = get_object_or_404(Post, slug=slug)
#         post.delete()
#         messages.add_message(request, messages.SUCCESS, 'The post was successfully deleted!')
#     return redirect('/')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, slug=self.kwargs['slug'])
        messages.success(self.request, 'The comment was successfully added!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('about', args=(self.kwargs['slug'],))


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'The comment was successfully deleted!')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('about', args=(self.object.post.slug,))

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_superuser


# def comment_add(request, slug):
#     form = CommentForm()
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.author = request.user
#             comment.post = get_object_or_404(Post, slug=slug)
#             comment.save()
#             messages.success(request, 'The comment was successfully added!')
#             return redirect('about', slug=slug)
#     return render(request, 'post/comment.html', {'form': form})


class CustomLoginView(LoginView):
    '''Custom login view'''
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in!')
        return super().form_valid(form)


class CustomRegisterView(CreateView):
    '''Custom register view'''
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully registered a new account!')
        user = form.save()
        login(self.request, user)
        return redirect('home')


class CustomLogoutView(LogoutView):
    '''Custom logout view'''

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out!")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(PasswordChangeView):
    '''Custom password change view'''
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully changed the password!')
        return super().form_valid(form)
