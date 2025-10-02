from django.urls import path, include
import accounts.views as views
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('oauth/', include('social_django.urls', namespace='oauth')),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path("register/", views.CustomRegisterView.as_view(), name="register"),
    path('profile/', views.profile, name='profile'),
    path('activate/<uuid64>/<token>/', views.activate, name='activate'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]
