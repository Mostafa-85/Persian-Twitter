from django.urls import path, re_path

from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('explor/',Explore.as_view(),name='explor'),
    path('popular/hashtag/',HotHashtag.as_view(),name="hot_hashtag")


 ]