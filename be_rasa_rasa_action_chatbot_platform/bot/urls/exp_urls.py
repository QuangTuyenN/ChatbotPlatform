from bot.views import *
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('question/', ChitChatIntentExampleList.as_view()),
    path('question/<uuid:pk>/', ChitChatIntentExampleDetail.as_view()),
    path('answer/', ChitChatUtterExampleList.as_view()),
    path('answer/<uuid:pk>/', ChitChatUtterExampleDetail.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
