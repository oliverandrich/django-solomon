from appconf import AppConf
from django.conf import settings  # noqa: F401


class SesameAuthAppConfig(AppConf):
    MAX_TOKEN_LIFETIME = 5 * 60  # 5 minutes

    LOGIN_TEMPLATE_NAME = "solomon/login.html"
    LOGIN_DONE_TEMPLATE_NAME = "solomon/login_done.html"
    LOGIN_EMAIL_HTML_TEMPLATE_NAME = "solomon/login_email.html"
    LOGIN_EMAIL_TXT_TEMPLATE_NAME = "solomon/login_email.txt"
    LOGIN_FAILED_TEMPLATE_NAME = "solomon/login_failed.html"

    SIGNUP_REQUIRED = True
    SIGNUP_REQUIRE_NAME = True
    SIGNUP_TEMPLATE_NAME = "solomon/signup.html"
    SIGNUP_DONE_TEMPLATE_NAME = "solomon/signup_done.html"
    SIGNUP_EMAIL_HTML_TEMPLATE_NAME = "solomon/signup_email.html"
    SIGNUP_EMAIL_TXT_TEMPLATE_NAME = "solomon/signup_email.txt"
