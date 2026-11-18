from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', refresh_token_view, name='refresh'),
    path('verify-email/', verify_email_view, name='verify-email'),
    path('password-reset/', password_reset_view, name='password-reset'),
    path('password-reset-confirm/', password_reset_confirm_view, name='password-reset-confirm'),
    path('change-password/', change_password_view, name='change-password'),
]


