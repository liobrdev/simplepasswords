from django.urls import re_path

from entries.api import (
    ListCreateEntriesAPI,
    RetrieveEntryAPI,
    UpdateEntryAPI,
    DestroyEntryAPI,)


urlpatterns = [
    re_path(r'^entries/$', ListCreateEntriesAPI.as_view(), name='entry-list'),
    re_path(
        r'^entry_retrieve/(?P<slug>[\w-]{10})/$', 
        RetrieveEntryAPI.as_view(),
        name='entry-retrieve',),
    re_path(
        r'^entry_update/(?P<slug>[\w-]{10})/$', 
        UpdateEntryAPI.as_view(),
        name='entry-update',),
    re_path(
        r'^entry_destroy/(?P<slug>[\w-]{10})/$', 
        DestroyEntryAPI.as_view(),
        name='entry-destroy',),
]