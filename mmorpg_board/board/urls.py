from django.urls import path
from .views import register_view, confirm_email_view, login_view, home_view, registration_success_view, create_post, \
    post_detail_view, my_posts_view, edit_post_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('confirm/', confirm_email_view, name='confirm_email'),
    path('register/success/', registration_success_view, name='registration_success'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('create/', create_post, name='create_post'),
    path('post/<int:pk>/', post_detail_view, name='post_detail'),

    path('my_posts/', my_posts_view, name='my_posts'),
    path('edit/<int:post_id>/', edit_post_view, name='edit_post'),
]

