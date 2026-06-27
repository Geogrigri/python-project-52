from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from task_manager.forms import UserRegistrationForm, UserUpdateForm


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
        messages.success(self.request, "Пользователь успешно удален")
        return super().form_valid(form)


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
