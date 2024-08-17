from bot.views_shorter import *
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', BotList.as_view()),
    path('<uuid:pk>/', BotDetail.as_view()),
    path('chitchat/', ChitChatList.as_view()),
    path('chitchat/<uuid:pk>/', ChitChatDetail.as_view()),
    path('chit-intent-example/', ChitChatIntentExampleList.as_view()),
    path('chit-intent-example/<uuid:pk>/', ChitChatIntentExampleDetail.as_view()),
    path('chit-utter-example/', ChitChatUtterExampleList.as_view()),
    path('chit-utter-example/<uuid:pk>/', ChitChatUtterExampleDetail.as_view()),
    path('history/', EventsList.as_view()),
    # path('history/<uuid:pk>/', EventsDetail.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
