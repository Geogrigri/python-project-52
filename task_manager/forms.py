from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from task_manager.models import Status, Task


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "password1", "password2")
        labels = {
            "username": "Имя пользователя",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Имя пользователя",
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ("name",)
        labels = {
            "name": "Имя",
        }


class TaskForm(forms.ModelForm):
    labels = forms.MultipleChoiceField(
        label="Метки",
        required=False,
        choices=(),
        disabled=True,
    )

    class Meta:
        model = Task
        fields = ("name", "description", "status", "executor", "labels")
        labels = {
            "name": "Имя",
            "description": "Описание",
            "status": "Статус",
            "executor": "Исполнитель",
        }
