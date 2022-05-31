from django.contrib.auth.views import LoginView, \
    PasswordResetView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Форма регистрации на сайте
    path(
        'signup/', views.SignUp.as_view(template_name='users/signup.html'),
        name='signup'
    ),
    # Форма после выхода из учетной записи
    path(
        'logout/',
        views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    # Форма входа на сайт
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # Форма сброса пароля
    path(
        'passwordreset/',
        PasswordResetView.as_view(template_name='users/'
                                                'password_reset_form.html'),
        name='password_reset_form'
    ),
    # Форма изменения пароля
    path(
        'password_change/',
        PasswordChangeView.as_view(template_name='users/'
                                                 'password_change_form.html'),
        name='password_change_form'
    ),
    # Форма после изменения пароля
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name='users/'
                                                     'password_change_done'
                                                     '.html'),
        name='password_change_done'
    ),
]
