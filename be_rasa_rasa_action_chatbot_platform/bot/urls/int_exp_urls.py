from bot.views import *
from django.urls import path

urlpatterns = [
    path('get-search/', IntentExampleSearch.as_view(), name='get-search_intent_exp'),
    path('', IntentExampleList.as_view()),
    path('<uuid:pk>/', IntentExampleDetail.as_view()),

]









