from django.urls import path
from .views import register_view, confirm_email_view, login_view, home_view, registration_success_view, create_post, \
    post_detail_view, my_posts_view, edit_post_view, my_replies_view, accept_reply_view, \
    delete_reply_view, delete_post_view, custom_logout_view, subscriptions, unsubscribe

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('confirm/', confirm_email_view, name='confirm_email'),
    path('register/success/', registration_success_view, name='registration_success'),
    path('login/', login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('create/', create_post, name='create_post'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),

    path('my_posts/', my_posts_view, name='my_posts'),
    path('delete_post/<int:post_id>/', delete_post_view, name='delete_post'),
    path('edit/<int:post_id>/', edit_post_view, name='edit_post'),

    path('my_replies/', my_replies_view, name='my_replies'),
    path('accept_reply/<int:reply_id>/', accept_reply_view, name='accept_reply'),
    path('delete_reply/<int:reply_id>/', delete_reply_view, name='delete_reply'),

    path('subscriptions/', subscriptions, name='subscriptions'),
    path('unsubscribe/<int:sub_id>/', unsubscribe, name='unsubscribe'),
]

