from django.urls import path
import post.views as views
from post.forms import CustomLoginForm, CustomPasswordChangeForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<str:slug>', views.about, name='about'),
    path('post/create/', views.create, name='create'),
    path('post/<str:slug>/edit/', views.edit, name='edit'),
    path('post/<str:slug>/delete/', views.delete, name='delete'),
    path('login/',
         auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CustomLoginForm,
                                      redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html',
                                                                   form_class=CustomPasswordChangeForm,
                                                                   success_url=reverse_lazy('home')),
         name='password_change')
]
