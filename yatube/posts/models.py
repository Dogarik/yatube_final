from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import CharField

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы',
        help_text='Введите имя группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка',
        help_text='Введите ссылку',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание',
    )

    class Meta:
        verbose_name_plural = 'Группы постов',

    def __str__(self) -> CharField:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Список постов',
        verbose_name = 'Пост'
        ordering = ['-pub_date'][:10]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Комментарий',
    )
    created = models.DateTimeField(
        verbose_name='Дата и время комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = 'Список комментариев',
        verbose_name = 'Комментарий'
        ordering = ['-created']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь "{self.user}" подписан на "{self.author}"'
