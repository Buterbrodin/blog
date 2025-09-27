from django.urls import path
import accounts.views as views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit', views.profile, name='profile_edit')
]
