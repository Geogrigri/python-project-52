from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django_filters.views import FilterView

from task_manager.filters import TaskFilter
from task_manager.forms import LabelForm, StatusForm, TaskForm, UserRegistrationForm, UserUpdateForm
from task_manager.models import Label, Status, Task


class IndexView(TemplateView):
    template_name = "index.html"


class UserListView(ListView):
    model = User
    template_name = "users/index.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.order_by("id")


class UserCreateView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/create.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно зарегистрирован")
        return super().form_valid(form)


class UserPermissionMixin:
    permission_message = "У вас нет прав для изменения"

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object():
            messages.error(request, self.permission_message)
            return redirect("users")
        return super().dispatch(request, *args, **kwargs)


class UserUpdateView(UserPermissionMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/update.html"
    success_url = reverse_lazy("users")

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно изменен")
        return super().form_valid(form)


class UserDeleteView(UserPermissionMixin, DeleteView):
    model = User
    template_name = "users/delete.html"
    success_url = reverse_lazy("users")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Невозможно удалить пользователя")
            return redirect("users")
        messages.success(self.request, "Пользователь успешно удален")
        return response


class UserLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Вы залогинены")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы разлогинены")
        return redirect("index")


class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/index.html"
    context_object_name = "labels"

    def get_queryset(self):
        return Label.objects.order_by("id")


class LabelCreateView(LoginRequiredMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/create.html"
    success_url = reverse_lazy("labels")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно создана")
        return super().form_valid(form)


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/update.html"
    success_url = reverse_lazy("labels")

    def form_valid(self, form):
        messages.success(self.request, "Метка успешно изменена")
        return super().form_valid(form)


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Невозможно удалить метку")
            return redirect("labels")
        messages.success(self.request, "Метка успешно удалена")
        return response


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/index.html"
    context_object_name = "statuses"

    def get_queryset(self):
        return Status.objects.order_by("id")


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/create.html"
    success_url = reverse_lazy("statuses")

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан")
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/update.html"
    success_url = reverse_lazy("statuses")

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно изменен")
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("statuses")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Невозможно удалить статус")
            return redirect("statuses")
        messages.success(self.request, "Статус успешно удален")
        return response


class TaskListView(LoginRequiredMixin, FilterView):
    model = Task
    filterset_class = TaskFilter
    template_name = "tasks/index.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.select_related(
            "status", "author", "executor"
        ).prefetch_related("labels").order_by("id")


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/create.html"
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Задача успешно создана")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/update.html"
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно изменена")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user != self.get_object().author:
            messages.error(request, "Задачу может удалить только ее автор")
            return redirect("tasks")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно удалена")
        return super().form_valid(form)
