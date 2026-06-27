from django.contrib import admin
from django.urls import path

from task_manager.forms import LoginForm
from task_manager.views import (
    IndexView,
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
