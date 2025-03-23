from django.urls import path
from .views import register_view, confirm_email_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('confirm/', confirm_email_view, name='confirm_email'),
]
