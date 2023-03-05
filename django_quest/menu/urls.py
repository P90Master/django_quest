from django.urls import re_path

from .views import index


app_name = 'menu'

urlpatterns = [
    re_path(r'^(?:[0-9a-zA-Z-]+/|.{0}?)*', index, name='index')
]
