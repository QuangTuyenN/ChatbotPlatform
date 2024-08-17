from bot.views import *
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path
router = DefaultRouter()
urlpatterns = [
    path('', IntentList.as_view()),
    path('<uuid:pk>/', IntentDetail.as_view()),
]
