from django.urls import re_path

from authentication.api import (
    ResetPasswordRequestAPI, ResetPasswordEmailAPI, ResetPasswordPhoneAPI,
    ResetPasswordSubmitAPI,)


urlpatterns = [
    re_path(
        r'^auth/reset_password/request/$', ResetPasswordRequestAPI.as_view(),
        name='reset_password_request',),
    re_path(
        r'^auth/reset_password/email/$', ResetPasswordEmailAPI.as_view(),
        name='reset_password_email',),
    re_path(
        r'^auth/reset_password/phone/$', ResetPasswordPhoneAPI.as_view(),
        name='reset_password_phone',),
    re_path(
        r'^auth/reset_password/submit/$', ResetPasswordSubmitAPI.as_view(),
        name='reset_password_submit',),
]
