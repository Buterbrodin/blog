from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm, PostShareForm
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, FormView
from django.urls import reverse
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.core.cache import cache
from django.conf import settings
from post.tasks import post_share


class HomeView(ListView):
    """
    Home view

    Features:
      * Shows the main page of the blog
      * Accessible for all users
      * Shows 5 posts per page
      * Shows most viewed posts and most commented posts
    """
    model = Post
    template_name = 'post/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        """
        Returns a queryset of posts

        Features:
          * Cached for 60 seconds to maintain performance and accuracy of the views counter
          * Filters posts based on user posts, tags and search query parameters
          * Returns an empty queryset if user is not authenticated and if user has no posts
          * Solves the issue of N+1
        """
        qs = cache.get('posts')  # tries to get the queryset from cache
        if not qs:
            qs = Post.objects.select_related('author').prefetch_related('tags').order_by(
                '-created_at')  # if cache is empty, creates a queryset, solves N+1 issue
            cache.set('posts', qs, 60)  # set the queryset in cache for 60 seconds
        if self.request.GET.get('user_posts') == 'true':  # if user_posts in GET parameters, filters posts by user
            if self.request.user.is_authenticated:
                qs = qs.filter(author=self.request.user)
            else:
                qs = Post.objects.none()  # if user is not authenticated, returns an empty queryset
        elif self.request.GET.get('tag'):  # if tag in GET parameters, filters posts by tag
            tag = self.request.GET.get('tag')
            qs = qs.filter(tags__name__icontains=tag)
        elif self.request.GET.get('content'):  # if user used search bar, filters posts by content and title
            content = self.request.GET.get('content')
            qs = qs.filter(
                Q(content__icontains=content) | Q(title__icontains=content) | Q(
                    tags__name__icontains=content)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        """Adds the most views and most commented posts to the context"""
        context = super().get_context_data(**kwargs)
        most_viewed_posts = cache.get('most_viewed_posts')  # checks if most_viewed_posts is in cache
        if not most_viewed_posts:  # if not, creates a queryset and caches it for 60 seconds
            most_viewed_posts = Post.objects.order_by('-views')[:5]
            cache.set('most_viewed_posts', most_viewed_posts, 60)
        most_commented_posts = cache.get('most_commented_posts')  # checks if most_commented_posts is in cache
        if not most_commented_posts:  # if not, creates a queryset and caches it for 60 seconds
            most_commented_posts = Post.objects.annotate(num_comments=Count('comments')).order_by('-num_comments')[:5]
            cache.set('most_commented_posts', most_commented_posts, 60)
        context['most_viewed_posts'] = most_viewed_posts
        context['most_commented_posts'] = most_commented_posts
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Post detail view

    Features:
      * Cached for 60 seconds to maintain performance and accuracy of the views counter
      * Shows the post and its comments
      * Solves the issue of N+1
    """
    model = Post
    template_name = 'post/about.html'
    context_object_name = 'post'
    slug_field = 'slug'  # slug field name
    slug_url_kwarg = 'slug'  # slug url keyword argument

    def get_queryset(self):
        """Returns a queryset of posts, solves the issue of N+1"""
        return Post.objects.select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        """Adds the comments to the context"""
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = post.comments.select_related("author").order_by("-created_at")
        return context

    def get_object(self, queryset=None):
        """Increases the views counter"""
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save()
        return obj


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Post edit view

    Features:
      * Only author or superuser can edit the post
      * If the post is edited successfully, eliminates the cache  adds a success message
      * If user has no permission, shows an error message and redirects to the home page
    """
    model = Post
    form_class = PostForm
    template_name = 'post/edit.html'

    def get_success_url(self):
        """Returns the success url"""
        return reverse('about', args=[self.kwargs['slug']])

    def form_valid(self, form):
        """Sends a success message and eliminates the cache"""
        messages.success(self.request, 'The post was successfully edited!')
        cache.delete('posts')  # eliminates the cache
        return super().form_valid(form)

    def test_func(self):
        """Checks if the user is the author of the post or a superuser"""
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser

    def handle_no_permission(self):
        """If a user is not authenticated, redirects to the login page, otherwise shows an error message and redirects to the home page"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'You do not have permission to edit this post.')
        return redirect('home')


class PostCreateView(LoginRequiredMixin, CreateView):
    '''
    Post create view

    Features:
      * Only authenticated users can create posts
      * If the post is created successfully, eliminates the cache and sends a success message
      * If user has no permission, redirects to the login page
    '''
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('home')
    template_name = 'post/create.html'

    def form_valid(self, form):
        """Sends a success message and eliminates the cache"""
        form.instance.author = self.request.user
        cache.delete('posts')  # eliminates the cache
        messages.success(self.request, 'The post was successfully created!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''
    Post delete view

    Features:
      * Only author or superuser can delete the post
      * If the post is deleted successfully, eliminates the cache and sends a success message
      * If user has no permission, redirects to the post page and shows an error message
    '''

    model = Post
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        """Sends a success message and eliminates the cache if the post is deleted successfully"""
        messages.success(request, "The post was successfully deleted!")
        cache.delete('posts')  # eliminates the cache
        return super().post(request, *args, **kwargs)

    def test_func(self):
        """Checks if the user is the author of the post or a superuser"""
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser

    def handle_no_permission(self):
        """If a user is not authenticated, redirects to the login page, otherwise shows an error message and redirects to the home page"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'You do not have permission to delete this post.')
        return redirect('about', slug=self.kwargs['slug'])


class PostShareView(LoginRequiredMixin, FormView):
    """
    Post share view

    Features:
      * Only authenticated users can share posts
      * Sends an async task of sending the post to the user's email and sends a success message
      * If user has no permission, redirects to the post page
    """
    template_name = 'post/share.html'
    form_class = PostShareForm

    def form_valid(self, form):
        """Sends an async task of sending the post to the user's email and sends a success message"""
        slug = self.kwargs['slug']  # gets the slug from the URL
        post = get_object_or_404(Post, slug=slug)
        full_url = self.request.build_absolute_uri(post.get_absolute_url())  # gets the full URL of the post
        username = self.request.user.username
        description = form.cleaned_data['description']  # gets the description from the form
        email_to = form.cleaned_data['email']  # gets the email from the form
        post_share.delay(slug, full_url, username, description,
                         email_to)  # adds an async task of sending the post to the user's email
        messages.success(self.request, 'The post was successfully shared!')
        return super().form_valid(form)

    def get_success_url(self):
        """Returns the success url"""
        return reverse('about', args=[self.kwargs['slug']])


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Comment create view

    Features:
      * Only authenticated users can create comments
      * Sends a success message if a comment is added successfully
      * If user has no permission, redirects to the login page
    """
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment_create.html'

    def form_valid(self, form):
        """Sends a success message if a comment is added successfully"""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, slug=self.kwargs[
            'slug'])  # gets the post from the database using the slug from the URL
        messages.success(self.request, 'The comment was successfully added!')
        return super().form_valid(form)

    def get_success_url(self):
        """Returns the success url"""
        return reverse('about', args=(self.kwargs['slug'],))


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Comment edit view

    Features:
      * Only author or superuser can edit the comment
      * If the comment is edited successfully, sends a success message
      * If user has no permission, shows an error page
    """
    model = Comment
    form_class = CommentForm
    template_name = 'post/comment_edit.html'

    def get_success_url(self):
        """Returns the success url"""
        return self.get_object().post.get_absolute_url()

    def form_valid(self, form):
        """Sends a success message"""
        messages.success(self.request, 'The comment was successfully edited!')
        return super().form_valid(form)

    def test_func(self):
        """Checks if the user is the author of the comment or a superuser"""
        comment = self.get_object()
        return comment.author == self.request.user or self.request.user.is_superuser


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Comment delete view

    Features:
      * Only author or superuser can delete the comment
      * Sends a success message if a comment is deleted successfully
      * If a user is not authenticated, redirects to the login page
      * If a user is authenticated but does not have permission, redirects to the post page and shows an error message
    """
    model = Comment

    def post(self, request, *args, **kwargs):
        """Sends a success message if a comment is deleted successfully"""
        messages.success(self.request, 'The comment was successfully deleted!')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """Returns the success url"""
        return reverse('about', args=[self.object.post.slug])

    def test_func(self):
        """Checks if the user is the author of the comment or a superuser"""
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_superuser

    def handle_no_permission(self):
        """If a user is not authenticated, redirects to the login page, otherwise shows an error message and redirects to the home page"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'You do not have permission to delete this comment.')
        post = self.get_object().post
        return redirect('about', slug=post.slug)
