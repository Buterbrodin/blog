from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm, PostShareForm
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.urls import reverse
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


class HomeView(ListView):
    '''Home page view'''
    model = Post
    template_name = 'post/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        qs = cache.get('posts')
        if not qs:
            qs = Post.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
            cache.set('posts', qs, 60)
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
                Q(content__icontains=content) | Q(title__icontains=content) | Q(
                    tags__name__icontains=content)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        most_viewed_posts = cache.get('most_viewed_posts')
        if not most_viewed_posts:
            most_viewed_posts = Post.objects.order_by('-views')[:5]
            cache.set('most_viewed_posts', most_viewed_posts, 60)
        most_commented_posts = cache.get('most_commented_posts')
        if not most_commented_posts:
            most_commented_posts = Post.objects.annotate(num_comments=Count('comments')).order_by('-num_comments')[:5]
            cache.set('most_commented_posts', most_commented_posts, 60)
        context['most_viewed_posts'] = most_viewed_posts
        context['most_commented_posts'] = most_commented_posts
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
#     return render(request, 'post/home.html', {'posts': posts})


class PostDetailView(LoginRequiredMixin, DetailView):
    '''Post detail view'''
    model = Post
    template_name = 'post/about.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = post.comments.select_related("author").order_by("-created_at")
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save()
        return obj


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
        cache.delete('posts')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Edit comment view'''
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment_create.html'

    def get_success_url(self):
        return self.get_object().post.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, 'The comment was successfully edited!')
        return super().form_valid(form)

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
        cache.delete('posts')
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
        cache.delete('posts')
        return super().post(request, *args, **kwargs)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser


def post_send(request, slug):
    form = PostShareForm()
    if request.method == 'POST':
        form = PostShareForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, slug=slug)
            cd = form.cleaned_data
            post_url = post.get_absolute_url()
            full_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{request.user.username} shared this post: {post.title}"
            message = f"{cd['description']} \n\n\n Check out this post at: {full_url}"
            email_to = cd['email']
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email_to],
            )
            messages.success(request, 'The post was successfully shared!')
            return redirect(post_url)
    return render(request, 'post/share.html', {'form': form})


# def delete(request, slug):
#     if request.method == 'POST':
#         post = get_object_or_404(Post, slug=slug)
#         post.delete()
#         messages.add_message(request, messages.SUCCESS, 'The post was successfully deleted!')
#     return redirect('/')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment_create.html'

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
#     return render(request, 'post/comment_create.html', {'form': form})
