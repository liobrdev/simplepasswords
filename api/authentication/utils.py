from django.db.models.enums import TextChoices


class AuthCommands(TextChoices):
    LOGIN = 'login'
    LOGOUT = 'logout'
    REGISTER = 'register'
    TFA = 'two_factor_auth'
    VERIFY_EMAIL = 'verify_email'
    VERIFY_PHONE = 'verify_phone'