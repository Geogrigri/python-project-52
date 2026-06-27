from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Status


class UserCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ivan",
            password="password12345",
            first_name="Иван",
            last_name="Иванов",
        )
        self.other_user = User.objects.create_user(
            username="petr",
            password="password12345",
            first_name="Петр",
            last_name="Петров",
        )

    def test_users_list_is_public(self):
        response = self.client.get(reverse("users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ivan")
        self.assertContains(response, "petr")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_registration_page_contains_expected_fields(self):
        response = self.client.get(reverse("user_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        self.assertContains(response, "Зарегистрировать")

    def test_user_can_register(self):
        response = self.client.post(
            reverse("user_create"),
            {
                "first_name": "Анна",
                "last_name": "Смирнова",
                "username": "anna",
                "password1": "complex-password-123",
                "password2": "complex-password-123",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="anna").exists())
        self.assertContains(response, "Пользователь успешно зарегистрирован")

    def test_duplicate_username_validation_mentions_exists(self):
        response = self.client.post(
            reverse("user_create"),
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "username": "ivan",
                "password1": "complex-password-123",
                "password2": "complex-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_user_can_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "ivan", "password": "password12345"},
            follow=True,
        )

        self.assertRedirects(response, reverse("index"))
        self.assertContains(response, "Вы залогинены")

    def test_user_can_logout(self):
        self.client.login(username="ivan", password="password12345")

        response = self.client.post(reverse("logout"), follow=True)

        self.assertRedirects(response, reverse("index"))
        self.assertContains(response, "Вы разлогинены")

    def test_user_can_update_self(self):
        self.client.login(username="ivan", password="password12345")

        response = self.client.post(
            reverse("user_update", kwargs={"pk": self.user.pk}),
            {
                "first_name": "Иван",
                "last_name": "Сергеев",
                "username": "ivan-new",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("users"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "ivan-new")
        self.assertEqual(self.user.last_name, "Сергеев")
        self.assertContains(response, "Пользователь успешно изменен")

    def test_user_cannot_update_another_user(self):
        self.client.login(username="ivan", password="password12345")

        response = self.client.post(
            reverse("user_update", kwargs={"pk": self.other_user.pk}),
            {
                "first_name": "Петр",
                "last_name": "Новый",
                "username": "petr-new",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("users"))
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.username, "petr")
        self.assertContains(response, "У вас нет прав для изменения")

    def test_user_can_delete_self(self):
        self.client.login(username="ivan", password="password12345")

        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.user.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("users"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertContains(response, "Пользователь успешно удален")

    def test_user_cannot_delete_another_user(self):
        self.client.login(username="ivan", password="password12345")

        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.other_user.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("users"))
        self.assertTrue(User.objects.filter(pk=self.other_user.pk).exists())
        self.assertContains(response, "У вас нет прав для изменения")


class StatusCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="status-user",
            password="password12345",
        )
        self.status = Status.objects.create(name="новый")

    def test_statuses_are_available_only_for_authenticated_users(self):
        urls = [
            reverse("statuses"),
            reverse("status_create"),
            reverse("status_update", kwargs={"pk": self.status.pk}),
            reverse("status_delete", kwargs={"pk": self.status.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_statuses_list(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.get(reverse("statuses"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Статусы")
        self.assertContains(response, "Создать статус")
        self.assertContains(response, "новый")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_status_create_page_contains_expected_field(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.get(reverse("status_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, "Имя")
        self.assertContains(response, "Создать")

    def test_user_can_create_status(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.post(
            reverse("status_create"),
            {"name": "в работе"},
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses"))
        self.assertTrue(Status.objects.filter(name="в работе").exists())
        self.assertContains(response, "Статус успешно создан")

    def test_status_unique_name_validation_mentions_exists(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.post(reverse("status_create"), {"name": "новый"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_user_can_update_status(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.post(
            reverse("status_update", kwargs={"pk": self.status.pk}),
            {"name": "на тестировании"},
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses"))
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "на тестировании")
        self.assertContains(response, "Статус успешно изменен")

    def test_user_can_delete_status(self):
        self.client.login(username="status-user", password="password12345")

        response = self.client.post(
            reverse("status_delete", kwargs={"pk": self.status.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses"))
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())
        self.assertContains(response, "Статус успешно удален")
