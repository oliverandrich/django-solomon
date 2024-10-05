from django.urls import path

from solomon.views import login_view, logout_view, verify_view

app_name = "solomon"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("verify/<int:pk>/<str:token_string>/", verify_view, name="verify"),
    path("logout/", logout_view, name="logout"),
]
