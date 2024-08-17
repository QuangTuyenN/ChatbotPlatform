from bot.views import *
from django.urls import path


urlpatterns = [
    path('', EventsList.as_view()),
    path('custom', EventsCustomList.as_view())
]
