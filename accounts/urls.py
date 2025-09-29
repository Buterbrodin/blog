from django.urls import path, include
import accounts.views as views
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit', views.profile, name='profile_edit'),
    path('activate/<uuid64>/<token>/', views.activate, name='activate'),
    path('password_reset/', views.CustomPasswordRestView.as_view(), name='password_reset'),
    path('password_reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]
