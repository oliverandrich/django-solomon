from appconf import AppConf
from django.conf import settings  # noqa: F401


class SesameAuthAppConfig(AppConf):
    MAX_TOKEN_LIFETIME = 5 * 60  # 5 minutes

    LOGIN_TEMPLATE = "solomon/login.html"
    LOGIN_DONE_TEMPLATE = "solomon/login_done.html"
    LOGIN_FAILED_TEMPLATE = "solomon/login_failed.html"

    EMAIL_SUBJECT_TEMPLATE = "solomon/login_email_subject.txt"
    EMAIL_HTML_TEMPLATE = "solomon/login_email.html"
    EMAIL_TXT_TEMPLATE = "solomon/login_email.txt"

    COMPLETE_PROFILE_URL = None

    ANONYMIZE_IP_ADDRESS = False
