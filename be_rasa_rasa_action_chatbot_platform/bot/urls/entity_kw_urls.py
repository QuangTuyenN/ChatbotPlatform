from bot.views import *
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', EntityKeyWordList.as_view()),
    path('<uuid:pk>/', EntityKeyWordDetail.as_view())
]

