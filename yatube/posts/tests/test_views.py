from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django import forms

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаю группу, текст и автора уже внутри поста
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовая запись',
            group=Group.objects.create(
                title='Заголовок группы',
                slug='test_slug')),

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяет шаблоны для каждого пути
    def test_URLS_templates_all(self):
        """Проверяет сообветствие url и шаблона"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test_user'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # проверяет контекст на главной странице
    def test_context_index(self):
        """Контекст в index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0,
                         'Тестовая запись')
        self.assertEqual(post_author_0, 'test_user')
        self.assertEqual(post_group_0, 'Заголовок группы')

    # Проверяет контекст на странице групп
    def test_context_group_list(self):
        """Контекст в group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context["group"]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        self.assertEqual(group_title_0, 'Заголовок группы')
        self.assertEqual(group_slug_0, 'test_slug')

    # Проверяет контекст на странице профиля
    def test_context_profile(self):
        """Контекст в profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_user'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(response.context['author'].username, 'test_user')
        self.assertEqual(post_text_0, 'Тестовая запись')

    # Проверяет содержимое страницы с деталями поста
    def test_post_detail(self):
        """тест на работоспособность post_detail"""
        response = self.authorized_client.get((
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        ))
        page_obj = response.context['post']
        # текст на странице сравниваем с текстом образца
        text = page_obj.text
        obrazec = Post.objects.get(id=1)
        self.assertEqual(text, obrazec.text)

    # Проверяет правильность типов полей формы для редактирования поста
    def test_post_edit_context(self):
        """Шаблон редактирования поста по id"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        # Словарь ожидаемых типов полей формы:
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Проверяет правильность типов полей формы для моздания поста
    def test_post_create_context(self):
        """Шаблон создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Пост не попал в другую группу
    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Тестовая запись')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user',
                                              email='test@gmail.com',)
        cls.group = Group.objects.create(
            title=('Заголовок тестовой группы'),
            slug='test_slug',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.user = User.objects.create_user(username='mobpsycho100')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка на десять постов для всех веб-страниц с паджинатором
    def test_first_page_ten_posts(self):
        """Проверка на десять постов для всех веб-страниц с паджинатором"""
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:group_list", kwargs={"slug": "test_slug"}): "group",
            reverse("posts:profile", kwargs={"username": "user"}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 10)

    # Проверка на три поста на второй странице паджинатора
    def test_second_page_contains_three_posts(self):
        """Проверка на три поста на второй странице паджинатора"""
        list_urls = {
            reverse("posts:index") + "?page=2": "index",
            reverse("posts:group_list", kwargs={"slug": "test_slug"}
                    ) + "?page=2": "group",
            reverse("posts:profile", kwargs={"username": "user"}) + "?page=2":
            "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3)
