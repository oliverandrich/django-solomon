from django.urls import path

from solomon.views import LoginView, logout_view, signup_view, verify_view

app_name = "solomon"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("verify/<str:jwt_token>/", verify_view, name="verify"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
]
