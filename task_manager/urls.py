from django.contrib import admin
from django.urls import path

from task_manager.forms import LoginForm
from task_manager.views import (
    IndexView,
    StatusCreateView,
    StatusDeleteView,
    StatusListView,
    StatusUpdateView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserLoginView,
    UserLogoutView,
    UserUpdateView,
)


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("tasks/", TaskListView.as_view(), name="tasks"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("statuses/", StatusListView.as_view(), name="statuses"),
    path("statuses/create/", StatusCreateView.as_view(), name="status_create"),
    path("statuses/<int:pk>/update/", StatusUpdateView.as_view(), name="status_update"),
    path("statuses/<int:pk>/delete/", StatusDeleteView.as_view(), name="status_delete"),
    path("users/", UserListView.as_view(), name="users"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path(
        "login/",
        UserLoginView.as_view(authentication_form=LoginForm),
        name="login",
    ),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
