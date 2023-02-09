from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug5',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='Nikita')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = User.objects.get(username='Nikita')
        group_1 = Group.objects.get(title='Заголовок для тестовой группы')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Nikita'}))
        self.assertEqual(post_1.text, 'Данные из формы')
        self.assertEqual(author_1.username, 'Nikita')
        self.assertEqual(group_1.title, 'Заголовок для тестовой группы')

    def test_guest_new_post(self):
        """неавторизоанный не может создавать посты"""
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного пользователя').exists())

    def test_authorized_edit_post(self):
        """авторизованный может редактировать"""
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        self.client.get(f'/Nikita/{post_2.id}/edit/')
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_2.id
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_2.text, 'Измененный текст')
