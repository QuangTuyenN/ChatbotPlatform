from bot.views import ChitChatList, ChitChatDetail
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', ChitChatList.as_view()),
    path('<uuid:pk>/', ChitChatDetail.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
