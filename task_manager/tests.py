from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Label, Status, Task


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
            self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

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


class TaskCrudTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            password="password12345",
        )
        self.executor = User.objects.create_user(
            username="executor",
            password="password12345",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="password12345",
        )
        self.status = Status.objects.create(name="новый")
        self.task = Task.objects.create(
            name="Первая задача",
            description="Описание первой задачи",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

    def test_tasks_are_available_only_for_authenticated_users(self):
        urls = [
            reverse("tasks"),
            reverse("task_create"),
            reverse("task_detail", kwargs={"pk": self.task.pk}),
            reverse("task_update", kwargs={"pk": self.task.pk}),
            reverse("task_delete", kwargs={"pk": self.task.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_tasks_list(self):
        self.client.login(username="author", password="password12345")

        response = self.client.get(reverse("tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Задачи")
        self.assertContains(response, "Создать задачу")
        self.assertContains(response, "Первая задача")
        self.assertContains(response, "новый")
        self.assertContains(response, "author")
        self.assertContains(response, "executor")
        self.assertContains(response, "Показать")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_task_create_page_contains_expected_fields(self):
        self.client.login(username="author", password="password12345")

        response = self.client.get(reverse("task_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="executor"')
        self.assertContains(response, "Имя")
        self.assertContains(response, "Описание")
        self.assertContains(response, "Статус")
        self.assertContains(response, "Исполнитель")
        self.assertContains(response, "Метки")
        self.assertContains(response, "Создать")

    def test_user_can_create_task(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Новая задача",
                "description": "Описание новой задачи",
                "status": self.status.pk,
                "executor": self.executor.pk,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        task = Task.objects.get(name="Новая задача")
        self.assertEqual(task.author, self.author)
        self.assertEqual(task.executor, self.executor)
        self.assertContains(response, "Задача успешно создана")

    def test_task_unique_name_validation_mentions_exists(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Первая задача",
                "description": "Другое описание",
                "status": self.status.pk,
                "executor": self.executor.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_user_can_view_task(self):
        self.client.login(username="author", password="password12345")

        response = self.client.get(reverse("task_detail", kwargs={"pk": self.task.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Первая задача")
        self.assertContains(response, "Описание первой задачи")
        self.assertContains(response, "Статус")
        self.assertContains(response, "Исполнитель")
        self.assertContains(response, "Метки")

    def test_user_can_update_task(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("task_update", kwargs={"pk": self.task.pk}),
            {
                "name": "Обновленная задача",
                "description": "Новое описание",
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Обновленная задача")
        self.assertEqual(self.task.executor, self.other_user)
        self.assertContains(response, "Задача успешно изменена")

    def test_author_can_delete_task(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("task_delete", kwargs={"pk": self.task.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        self.assertContains(response, "Задача успешно удалена")

    def test_non_author_cannot_delete_task(self):
        self.client.login(username="other", password="password12345")

        response = self.client.post(
            reverse("task_delete", kwargs={"pk": self.task.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        self.assertContains(response, "Задачу может удалить только ее автор")

    def test_related_user_cannot_be_deleted(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("user_delete", kwargs={"pk": self.author.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("users"))
        self.assertTrue(User.objects.filter(pk=self.author.pk).exists())
        self.assertContains(response, "Невозможно удалить пользователя")

    def test_related_status_cannot_be_deleted(self):
        self.client.login(username="author", password="password12345")

        response = self.client.post(
            reverse("status_delete", kwargs={"pk": self.status.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses"))
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())
        self.assertContains(response, "Невозможно удалить статус")


class LabelCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="label-user",
            password="password12345",
        )
        self.status = Status.objects.create(name="label-status")
        self.label = Label.objects.create(name="bug")
        self.second_label = Label.objects.create(name="feature")

    def test_labels_are_available_only_for_authenticated_users(self):
        urls = [
            reverse("labels"),
            reverse("label_create"),
            reverse("label_update", kwargs={"pk": self.label.pk}),
            reverse("label_delete", kwargs={"pk": self.label.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(
                response,
                f"{reverse('login')}?next={url}",
                fetch_redirect_response=False,
            )

    def test_labels_list(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.get(reverse("labels"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Метки")
        self.assertContains(response, "Создать метку")
        self.assertContains(response, "bug")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_label_create_page_contains_expected_field(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.get(reverse("label_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, "Имя")
        self.assertContains(response, "Создать")

    def test_user_can_create_label(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("label_create"),
            {"name": "urgent"},
            follow=True,
        )

        self.assertRedirects(response, reverse("labels"))
        self.assertTrue(Label.objects.filter(name="urgent").exists())
        self.assertContains(response, "Метка успешно создана")

    def test_label_unique_name_validation_mentions_exists(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(reverse("label_create"), {"name": "bug"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_user_can_update_label(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("label_update", kwargs={"pk": self.label.pk}),
            {"name": "backend"},
            follow=True,
        )

        self.assertRedirects(response, reverse("labels"))
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "backend")
        self.assertContains(response, "Метка успешно изменена")

    def test_user_can_delete_unused_label(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("label_delete", kwargs={"pk": self.label.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("labels"))
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())
        self.assertContains(response, "Метка успешно удалена")

    def test_user_cannot_delete_label_related_to_task(self):
        task = Task.objects.create(
            name="Задача с меткой",
            description="Описание",
            status=self.status,
            author=self.user,
        )
        task.labels.add(self.label)
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("label_delete", kwargs={"pk": self.label.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("labels"))
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())
        self.assertContains(response, "Невозможно удалить метку")

    def test_user_can_create_task_with_labels(self):
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Задача с несколькими метками",
                "description": "Описание",
                "status": self.status.pk,
                "executor": "",
                "labels": [self.label.pk, self.second_label.pk],
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        task = Task.objects.get(name="Задача с несколькими метками")
        self.assertCountEqual(task.labels.all(), [self.label, self.second_label])

    def test_user_can_update_task_labels(self):
        task = Task.objects.create(
            name="Задача для обновления меток",
            description="Описание",
            status=self.status,
            author=self.user,
        )
        task.labels.add(self.label)
        self.client.login(username="label-user", password="password12345")

        response = self.client.post(
            reverse("task_update", kwargs={"pk": task.pk}),
            {
                "name": task.name,
                "description": task.description,
                "status": self.status.pk,
                "executor": "",
                "labels": [self.second_label.pk],
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks"))
        task.refresh_from_db()
        self.assertCountEqual(task.labels.all(), [self.second_label])


class TaskFilterTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="filter-author",
            password="password12345",
        )
        self.other_author = User.objects.create_user(
            username="filter-other-author",
            password="password12345",
        )
        self.executor = User.objects.create_user(
            username="filter-executor",
            password="password12345",
        )
        self.other_executor = User.objects.create_user(
            username="filter-other-executor",
            password="password12345",
        )
        self.new_status = Status.objects.create(name="filter-new")
        self.done_status = Status.objects.create(name="filter-done")
        self.bug_label = Label.objects.create(name="filter-bug")
        self.feature_label = Label.objects.create(name="filter-feature")
        self.first_task = Task.objects.create(
            name="Filter first task",
            description="First",
            status=self.new_status,
            author=self.author,
            executor=self.executor,
        )
        self.first_task.labels.add(self.bug_label)
        self.second_task = Task.objects.create(
            name="Filter second task",
            description="Second",
            status=self.done_status,
            author=self.other_author,
            executor=self.other_executor,
        )
        self.second_task.labels.add(self.feature_label)

    def test_filter_form_has_expected_fields_and_labels(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(reverse("tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="executor"')
        self.assertContains(response, 'name="labels"')
        self.assertContains(response, 'name="self_tasks"')
        self.assertContains(response, "Статус")
        self.assertContains(response, "Исполнитель")
        self.assertContains(response, "Метка")
        self.assertContains(response, "Только свои задачи")

    def test_filter_tasks_by_status(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(reverse("tasks"), {"status": self.new_status.pk})

        self.assertContains(response, "Filter first task")
        self.assertNotContains(response, "Filter second task")

    def test_filter_tasks_by_executor(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(reverse("tasks"), {"executor": self.other_executor.pk})

        self.assertNotContains(response, "Filter first task")
        self.assertContains(response, "Filter second task")

    def test_filter_tasks_by_label(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(reverse("tasks"), {"labels": self.bug_label.pk})

        self.assertContains(response, "Filter first task")
        self.assertNotContains(response, "Filter second task")

    def test_filter_only_self_tasks(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(reverse("tasks"), {"self_tasks": "on"})

        self.assertContains(response, "Filter first task")
        self.assertNotContains(response, "Filter second task")

    def test_filter_combines_conditions(self):
        self.client.login(username="filter-author", password="password12345")

        response = self.client.get(
            reverse("tasks"),
            {
                "status": self.new_status.pk,
                "executor": self.executor.pk,
                "labels": self.bug_label.pk,
                "self_tasks": "on",
            },
        )

        self.assertContains(response, "Filter first task")
        self.assertNotContains(response, "Filter second task")
