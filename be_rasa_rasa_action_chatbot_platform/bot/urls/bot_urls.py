from bot.views import BotList, BotDetail, BotTrain, BotHtml
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', BotList.as_view()),
    path('<uuid:pk>/', BotDetail.as_view()),
    path('<uuid:pk>/train/', BotTrain.as_view()),
    path('<uuid:pk>/html/', BotHtml.as_view()),
]
