from bot.views import *
from django.urls import path


urlpatterns = [
    path('', EntityList.as_view()),
    path('<uuid:pk>/', EntityDetail.as_view())
]
