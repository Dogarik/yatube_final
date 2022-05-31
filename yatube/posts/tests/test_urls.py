from django.test import TestCase, Client
from ..models import Post, User, Group
from django.urls import reverse


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth_user'
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='test description'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group
        )
        cls.post_edit_url = reverse('posts:post_edit', args=[cls.post.id])
        cls.post_url = reverse('posts:post_detail', args=[cls.post.pk])
        cls.index_url = reverse('posts:index')
        cls.group_url = reverse('posts:group_list', args=[cls.group.slug])
        cls.profile_url = reverse('posts:profile', args=[cls.user.username])
        cls.create_urls = reverse('posts:post_create')
        cls.follow_urls = reverse('posts:follow_index')
        cls.unexisting_url = '/unexisting/'
        cls.urls_list_guest_client = [
            cls.index_url,
            cls.group_url,
            cls.profile_url,
            cls.post_url,
            # cls.follow_urls,
        ]
        cls.urls_list_authorized_client = [
            cls.create_urls,
            cls.follow_urls,
        ]

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Страницы, доступные неавторизированному пользователю"""
        for item in self.urls_list_guest_client:
            response = self.guest_client.get(item)
            self.assertEqual(response.status_code, 200)

    def test_url_not_exists_at_desired_location(self):
        """Несуществующие страницы"""
        response = self.guest_client.get(self.unexisting_url)
        self.assertEqual(response.status_code, 404)

    def test_url_is_available_to_any_user(self):
        """Страница /create/ доступна авторизированному пользователю."""
        for item in self.urls_list_authorized_client:
            response = self.authorized_client.get(item)
            self.assertEqual(response.status_code, 200)

    def test_non_author_cannot_edit_post(self):
        """Страница /edit/ доступна только автору поста"""
        non_author = User.objects.create_user(username='non_author')
        not_author_client = Client()
        not_author_client.force_login(non_author)
        response = not_author_client.get(PostsURLTests.post_edit_url)
        self.assertRedirects(response, PostsURLTests.post_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': self.index_url,
            'posts/group_list.html': self.group_url,
            'posts/profile.html': self.profile_url,
            'posts/post_detail.html': self.post_url,
            'posts/create_post.html': self.create_urls,
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                # self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
