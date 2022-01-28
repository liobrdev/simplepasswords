from django.urls import include, re_path

from authentication import endpoints as auth
from entries import endpoints as entries
from users import endpoints as users
from custom_db_logger import endpoints as logs

from utils.views import not_found


urlpatterns = [
    re_path(r'^api/', include(auth)),
    re_path(r'^api/', include(entries)),
    re_path(r'^api/', include(users)),
    re_path(r'^api/', include(logs)),
]

handler404 = not_found