import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_img = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=cls.small_img,
            content_type='image/jpg'
        )
        cls.user = User.objects.create(username='TestNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.user2 = User.objects.create(username='TestNameAuthor2')
        cls.group_for_user2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = self.group
        user = self.user
        post = self.post
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', args=[group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[user.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[post.pk]):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', args=[post.pk]):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.post(
            reverse('posts:index')
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = str(first_object.author)
        post_group_0 = str(first_object.group)
        post_image_0 = first_object.image
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, self.post.group.title)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:group_list',
                                                       args=[
                                                           self.group.slug])))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(self.group, response.context['group'])
        self.assertEqual(post_group_0, response.context['group'])
        self.assertNotEqual(self.group_for_user2,
                            response.context['group'])
        self.assertEqual(post_image_0, self.post.image)

    def test_post_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:profile',
                                                       args=[
                                                           self.user.username
                                                       ])))
        first_object = response.context['page_obj'][0]
        post_group_0 = str(first_object.group)
        post_image_0 = first_object.image
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(self.user.username,
                         str(response.context['author']))
        self.assertNotEqual(self.user2,
                            first_object.author)
        self.assertNotEqual(self.group_for_user2,
                            post_group_0)
        self.assertEqual(post_group_0, self.post.group.title)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_detail',
                                                       args=[self.post.pk])))
        self.assertEqual(self.post, response.context['post'])
        self.assertEqual(self.post.text, str(response.context['post']))

    def test_post_edit_post_show_correct_context(self):
        """Шаблон create_post для редактирования поста сформирован
        с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_edit',
                                                       args=[self.post.pk])))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_post_show_correct_context(self):
        """Шаблон create_post для создания поста сформирован
        с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment(self):
        comment_counter = self.post.comments.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comment_counter + 1)
        comment_text = response.context['comments'][0].text
        self.assertEqual(comment_text, form_data['text'])


class PostsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_1')
        cls.user_2 = User.objects.create_user(username='User_2')
        cls.author = User.objects.create_user(username='author_1')
        cls.guest = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.author,
            group=cls.group,
        )

    def test_follow_users_for_authorized_client(self):
        url_login = reverse('users:login')
        url_follow = reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}
        )
        self.assertRedirects(
            self.guest.get(reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username})
            ),
            f'{url_login}?next={url_follow}'
        )

    def test_user_tracking_for_authorized_client(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username})
        )

    def test_unfollow_users_for_authorized_client(self):
        follow_page = reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username})
        self.authorized_client.get(follow_page)
        follow = Follow.objects.filter(user=self.user)
        follow_count_1 = len(follow)
        follow_page = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username})
        self.authorized_client.get(follow_page)
        follow = Follow.objects.filter(user=self.user)
        follow_count_2 = len(follow)
        self.assertEqual(follow_count_2, follow_count_1 - 1)

    def test_user_follow_posts_exists_at_desire_location(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username})
        )
        post = Post.objects.create(
            text='text',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        content = response.context['page_obj'][0]
        self.assertEqual(content.text, post.text)

    def test_cache_in_index_page_show_correct_context(self):
        Post.objects.create(
            text='Текст',
            author=self.user,
        )
        leng = Post.objects.count()
        resp = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(resp.context.get('page_obj')), leng)
        Post.objects.last().delete()
        self.assertEqual(len(resp.context.get('page_obj')), leng)
        cache.clear()
        resp = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(resp.context.get('page_obj')), leng - 1)
