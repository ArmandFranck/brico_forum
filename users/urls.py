from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('create_post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('messages/<int:user_id>/', views.view_messages, name='view_messages'),
    path('send_message/<int:user_id>/', views.send_message, name='send_message'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('messages/', views.view_private_messages, name='view_private_messages'),
    path('messages/', views.received_messages, name='received_messages'),
    
]
