from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from task_manager.models import Label, Status, Task


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
    password1 = forms.CharField(
        label="Пароль",
        required=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        required=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "password1", "password2")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "username": "Имя пользователя",
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn’t match.")
            validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


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


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ("name",)
        labels = {
            "name": "Имя",
        }


class TaskForm(forms.ModelForm):
    executor = UserChoiceField(
        label="Исполнитель",
        queryset=User.objects.all(),
        required=False,
    )
    labels = forms.ModelMultipleChoiceField(
        label="Метки",
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple,
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
