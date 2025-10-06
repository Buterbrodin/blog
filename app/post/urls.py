from django.urls import path
import post.views as views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post/<str:slug>', views.PostDetailView.as_view(), name='about'),
    path('post_share/<str:slug>/', views.PostShareView.as_view(), name='post_send'),
    path('post/create/', views.PostCreateView.as_view(), name='create'),
    path('post/<str:slug>/edit/', views.PostEditView.as_view(), name='edit'),
    path('post/<str:slug>/delete/', views.PostDeleteView.as_view(), name='delete'),
    path('comment/<str:slug>/add', views.CommentCreateView.as_view(), name='comment_add'),
    path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/edit', views.CommentEditView.as_view(), name='comment_edit'),
]
