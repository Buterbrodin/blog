from django.urls import path
import post.views as views
from post.forms import CustomLoginForm, CustomPasswordChangeForm
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<str:slug>', views.about, name='about'),
    path('post/create/', views.create, name='create'),
    path('post/<str:slug>/edit/', views.edit, name='edit'),
    path('post/<str:slug>/delete/', views.delete, name='delete'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change')
]
