from django.urls import re_path

from authentication.api import (
    LoginAPI, LogoutAPI, VerifyEmailAPI, VerifyPhoneAPI, TwoFactorAuthAPI,)


urlpatterns = [
    re_path(r'^auth/login/$', LoginAPI.as_view(), name='login'),
    re_path(r'^auth/logout/$', LogoutAPI.as_view(), name='logout'),
    re_path(
        r'^auth/verify_email/$', VerifyEmailAPI.as_view(),
        name='verify_email',),
    re_path(
        r'^auth/verify_phone/$', VerifyPhoneAPI.as_view(),
        name='verify_phone',),
    re_path(
        r'^auth/two_factor_auth/$', TwoFactorAuthAPI.as_view(),
        name='two_factor_auth',),
]
