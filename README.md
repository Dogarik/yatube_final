# Проект YATUBE
Социальная сеть
### Описание
Благодаря этому проекту можно создавать посты, оставлять комментарии под постами и подписываться на понравившихся авторов.
### Технологии
Python, Django, DRF, DRF-Simple JWT, Django CORS, Bootstrap.
### Запуск проекта в dev-режиме
- Клонировать репозиторий и перейти в него в командной строке:
- Установите и активируйте виртуальное окружение:
```
Для пользователей Windows:
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Перейдите в каталог с файлом manage.py выполните команды:
Выполнить миграции:
```
python manage.py migrate
```
Создайте супер-пользователя:
```
python manage.py createsuperuser
```
Запуск проекта:
```
python manage.py runserver
```
### Добавление сообществ проект реализованного через админ панель Django:
```
admin/admin/ - после авторазиации, перейдите в раздел "сообщества" и создайте тематики
```
### Авторы
Rustam Magomedov (dogarik2007)
