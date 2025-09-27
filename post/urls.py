from django.urls import path
import post.views as views
from post.forms import CustomLoginForm, CustomPasswordChangeForm
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.HomeView.as_view(), name='home'),
                  path('post/<str:slug>', views.PostDetailView.as_view(), name='about'),
                  path('post/create/', views.PostCreateView.as_view(), name='create'),
                  path('post/<str:slug>/edit/', views.PostEditView.as_view(), name='edit'),
                  path('post/<str:slug>/delete/', views.PostDeleteView.as_view(), name='delete'),
                  path('login/', views.CustomLoginView.as_view(), name='login'),
                  path('logout/', views.CustomLogoutView.as_view(), name='logout'),
                  path("register/", views.CustomRegisterView.as_view(), name="register"),
                  path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
                  path('comment/<str:slug>/add', views.CommentCreateView.as_view(), name='comment_add'),
                  path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(), name='comment_delete'),
                  path('comment/<int:pk>/edit', views.CommentEditView.as_view(), name='comment_edit')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
