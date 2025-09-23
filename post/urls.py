from django.urls import path
import post.views as views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<str:slug>', views.about, name='about'),
    path('post/create/', views.create, name='create'),
    path('post/<str:slug>/edit/', views.edit, name='edit'),
    path('post/<str:slug>/delete/', views.delete, name='delete'),
]