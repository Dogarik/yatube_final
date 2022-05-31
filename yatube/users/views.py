# Импортируем CreateView, чтобы создать ему наследника
from django.contrib.auth.views import LogoutView
from django.views.generic import CreateView

# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy

# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class LogoutView(LogoutView):
    form_class = LogoutView
    success_url = reverse_lazy('users:logout')
    template_name = 'users/logged_out.html'
