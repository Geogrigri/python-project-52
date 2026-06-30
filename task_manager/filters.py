import django_filters
from django import forms
from django.contrib.auth.models import User

from task_manager.forms import UserChoiceField
from task_manager.models import Label, Status, Task


class UserChoiceFilter(django_filters.ModelChoiceFilter):
    field_class = UserChoiceField


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        label="Статус",
        queryset=Status.objects.all(),
        empty_label="---------",
    )
    executor = UserChoiceFilter(
        label="Исполнитель",
        queryset=User.objects.all(),
        empty_label="---------",
    )
    labels = django_filters.ModelChoiceFilter(
        label="Метка",
        queryset=Label.objects.all(),
        empty_label="---------",
        field_name="labels",
    )
    self_tasks = django_filters.BooleanFilter(
        label="Только свои задачи",
        method="filter_self_tasks",
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = ("status", "executor", "labels", "self_tasks")

    def filter_self_tasks(self, queryset, name, value):
        if value and self.request is not None:
            return queryset.filter(author=self.request.user)
        return queryset
