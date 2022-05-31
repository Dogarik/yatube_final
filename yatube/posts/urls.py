from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Посты одного автора
    path('group/<slug:slug>/', views.group_posts, name='group_list'),

    # Профайл автора
    path('profile/<str:username>/', views.profile, name='profile'),

    # Просмотр записи по id
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    # Добавление нового поста
    path('create/', views.post_create, name='post_create'),

    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),

    # Добавление комментария
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),

    # Подписка на автора
    path('follow/', views.follow_index, name='follow_index'),

    # Список всех подписок
    path(
        'profile/<str:username>/follow/', views.profile_follow,
        name='profile_follow',
    ),

    # Отписка
    path(
        'profile/<str:username>/unfollow/', views.profile_unfollow,
        name='profile_unfollow',
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
