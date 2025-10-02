from django.template.defaulttags import comment
from django.test import TestCase
from post.models import Post, Comment
from django.contrib.auth.models import User
from django.urls import reverse, resolve
import post.views as views
from post.models import Post, Comment


class PostURLsTests(TestCase):

    def setUp(self):
        self.user = User(username='test-user', is_active=True)
        self.user.set_password('Assembler7002')
        self.user.save()
        self.post = Post(title='test-post', content='test-content', author=self.user)
        self.post.save()
        self.post.tags.add('test-tag')
        self.post.save()
        self.comment = Comment.objects.create(author=self.user, post=self.post, content='test-content')

    def test_home_url_view(self):
        url = reverse('home')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.HomeView)

    def test_home_url_response(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post/home.html')

    def test_about_url_view(self):
        url = reverse('about', args=['test-arg'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.PostDetailView)

    def test_about_url_response_unauthorized(self):
        url = reverse('about', args=[self.post.slug])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')
        self.assertEqual(response.status_code, 200)

    def test_about_url_response_authorized(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('about', args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post/about.html')
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.comment.content)

    def test_about_url_response_authorized_invalid(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('about', args=['invalid-arg'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_create_url_view(self):
        url = reverse('create')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.PostCreateView)

    def test_post_create_url_unauthorized_response(self):
        url = reverse('create')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')

    def test_post_create_url_authorized_valid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('create')
        context = {'title': 'test-post', 'content': 'test-content-for-post', 'tags': 'hello,world'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Post.objects.count(), 2)  # +1 post from setUp

    def test_post_create_url_authorized_invalid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('create')
        context = {'title': '', 'content': '', 'tags': ''}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
        self.assertEqual(Post.objects.count(), 1)  # 1 post from setUp

    def test_post_share_url_view(self):
        url = reverse('post_send', args=['test-arg'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.PostShareView)

    def test_post_share_url_unauthorized_response(self):
        url = reverse('post_send', args=[self.post.slug])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')

    def test_post_share_url_authorized_valid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('post_send', args=[self.post.slug])
        context = {'email': 'test@email.com', 'description': 'test-description'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'The post was successfully shared!')

    def test_post_share_url_authorized_invalid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('post_send', args=[self.post.slug])
        context = {'email': '', 'description': ''}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'This field is required.')

    def test_post_edit_url_view(self):
        url = reverse('edit', args=['test-arg'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.PostEditView)

    def test_post_edit_url_unauthorized_response(self):
        url = reverse('edit', args=['test-arg'])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f'{reverse('login')}?next={url}')

    def test_post_edit_url_authorized_permitted_valid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('edit', args=[self.post.slug])
        context = {'title': 'edited-test-post', 'content': 'edited-post-content', 'tags': 'edited'}
        response = self.client.post(url, context, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'The post was successfully edited!')
        self.assertEqual(self.post.title, 'edited-test-post')

    def test_post_edit_url_authorized_permitted_invalid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('edit', args=[self.post.slug])
        context = {'title': '', 'content': '', 'tags': ''}
        response = self.client.post(url, context)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
        self.assertNotEqual(self.post.title, '')

    def test_post_edit_url_authorized_unpermitted_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        user2 = User.objects.create(username='test-user2')
        post2 = Post.objects.create(author=user2, title='test title2', content='test content2')
        url = reverse('edit', args=[post2.slug])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, 'You do not have permission to edit this post.')

    def test_post_delete_url_view(self):
        url = reverse('delete', args=['test-arg'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.PostDeleteView)

    def test_post_delete_url_unauthorized_response(self):
        url = reverse('delete', args=['test-arg'])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_post_delete_url_authorized_permitted_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('delete', args=[self.post.slug])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, 'The post was successfully deleted!')

    def test_post_delete_url_authorized_unpermitted_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        user2 = User.objects.create(username='test-user2')
        post2 = Post.objects.create(author=user2, title='test title2', content='test content2')
        url = reverse('delete', args=[post2.slug])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[post2.slug]))
        self.assertContains(response, 'You do not have permission to delete this post.')

    def test_comment_add_url_view(self):
        url = reverse('comment_add', args=['test-arg'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CommentCreateView)

    def test_comment_add_url_unauthorized_response(self):
        url = reverse('comment_add', args=['test-arg'])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_comment_add_url_authorized_valid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('comment_add', args=[self.post.slug])
        context = {'content': 'test-comment-for-a-post'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'The comment was successfully added!')
        self.assertEqual(self.post.comments.count(), 2)  # +1 comment from setUp

    def test_comment_add_url_authorized_invalid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('comment_add', args=[self.post.slug])
        context = {'content': 'test'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'content', 'Comment must be at least 10 characters')
        self.assertEqual(self.post.comments.count(), 1)  # 1 comment from setUp

    def test_comment_delete_url_view(self):
        url = reverse('comment_delete', args=['1'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CommentDeleteView)

    def test_comment_delete_url_unauthorized_response(self):
        url = reverse('comment_delete', args=[self.comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_comment_delete_url_authorized_unpermitted_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        user2 = User.objects.create(username='test-user2')
        comment2 = Comment.objects.create(author=user2, post=self.post, content='test-comment-2')
        url = reverse('comment_delete', args=[comment2.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'You do not have permission to delete this comment.')
        self.assertEqual(self.post.comments.count(), 2)  # +1 comment from setUp

    def test_comment_delete_url_authorized_permitted_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('comment_delete', args=[self.comment.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'The comment was successfully deleted!')

    def test_comment_edit_url_view(self):
        url = reverse('comment_edit', args=['1'])
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.CommentEditView)

    def test_comment_edit_url_unauthorized_response(self):
        url = reverse('comment_edit', args=[self.comment.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_comment_edit_url_authorized_valid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('comment_edit', args=[self.comment.pk])
        context = {'content': 'edited-comment-for-post'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('about', args=[self.post.slug]))
        self.assertContains(response, 'The comment was successfully edited!')

    def test_comment_edit_url_authorized_invalid_response(self):
        self.client.login(username=self.user.username, password='Assembler7002')
        url = reverse('comment_edit', args=[self.comment.pk])
        context = {'content': 'inv'}
        response = self.client.post(url, context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'content', 'Comment must be at least 10 characters')
        self.assertEqual(self.comment.content, 'test-content')


class PostModelTests(TestCase):

    def setUp(self):
        self.author = User.objects.create(username='test-author')
        self.post = Post.objects.create(author=self.author, title='test title', content='test content')

    def test_post_str(self):
        self.assertEqual(str(self.post), 'test title')

    def test_post_create(self):
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.author, self.author)
        self.assertEqual(self.post.title, 'test title')
        self.assertEqual(self.post.content, 'test content')
        self.assertEqual(self.post.views, 0)

    def test_post_save(self):
        author1 = User.objects.create(username='test-author1')
        author2 = User.objects.create(username='test-author2')

        post1 = Post(author=author1, title='test title1', content='test content1')
        post2 = Post(author=author2, title='test title2', content='test content2')

        post1.save()
        post2.save()

        posts = Post.objects.all()

        self.assertEqual(posts.count(), 3)  # +1 post from setUp()
        self.assertIn(post1, posts)
        self.assertIn(post2, posts)
        self.assertEqual(post1.author, author1)
        self.assertEqual(post2.author, author2)

    def test_post_slug(self):
        post1 = Post.objects.create(author=self.author, title='test title', content='test content')
        self.assertEqual(self.post.slug, 'test-title')
        self.assertEqual(post1.slug, 'test-title-1')

    def test_post_tags(self):
        self.post.tags.add('test-tag')
        self.assertEqual(self.post.tags.count(), 1)
        self.post.tags.remove('test-tag')
        self.assertEqual(self.post.tags.count(), 0)

    def test_post_absolute_url(self):
        post_url = self.post.get_absolute_url()
        self.assertEqual(post_url, reverse('about', args=[self.post.slug]))


class CommentModelTests(TestCase):

    def setUp(self):
        self.author = User.objects.create(username='test-author')
        self.post = Post.objects.create(author=self.author, title='test title', content='test content')
        self.comment = Comment.objects.create(author=self.author, post=self.post, content='test content')

    def test_comment_create(self):
        self.assertIsInstance(self.comment, Comment)
        self.assertEqual(self.comment.author, self.author)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, 'test content')

    def test_comment_str(self):
        self.assertEqual(str(self.comment), f'Comment by {self.author} on {self.post}')

    def test_comment_save(self):
        author1 = User.objects.create(username='test-author1')
        author2 = User.objects.create(username='test-author2')
        post1 = Post.objects.create(author=author1, title='test title1', content='test content1')
        post2 = Post.objects.create(author=author2, title='test title2', content='test content2')

        comment1 = Comment(author=author1, post=post1, content='test content1')
        comment2 = Comment(author=author2, post=post2, content='test content2')

        comment1.save()
        comment2.save()

        comments = Comment.objects.all()

        self.assertEqual(comments.count(), 3)  # +1 comment from setUp
        self.assertIn(comment1, comments)
        self.assertIn(comment2, comments)
        self.assertEqual(comment1.author, author1)
        self.assertEqual(comment2.author, author2)
        self.assertEqual(comment1.post, post1)
        self.assertEqual(comment2.post, post2)

    def test_comment_deleted_with_post(self):
        self.post.delete()
        self.assertEqual(Comment.objects.count(), 0)
