from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def pages_response_template(self):
        template_response_code = {
            '/': 'posts/index.html',
            '/group/<slug:slug>/': 'posts/group_list.html',
            '/profile/<str:username>/': 'posts/profile.html',
            '/posts/<int:post_id>/': 'posts/post_detail.html',
        }
        for template, address in template_response_code.items():
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertTemplateUsed(response, address)

    def test_create_response_template(self):
        """Страница /create/ использует шаблон posts/create_post.html"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_unexisting_page_404(self):
        """Страница /unexisting_page/ возвращает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
