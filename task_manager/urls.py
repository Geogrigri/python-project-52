from django.contrib import admin
from django.urls import path

from task_manager.forms import LoginForm
from task_manager.views import (
    IndexView,
    StatusCreateView,
    StatusDeleteView,
    StatusListView,
    StatusUpdateView,
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
