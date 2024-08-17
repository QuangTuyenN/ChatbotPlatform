from bot.views import *
from django.urls import path

# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('text-card/', TextCardList.as_view()),
    path('text-card/<uuid:pk>/', TextCardDetail.as_view()),
    path('image-card/', ImageCardList.as_view()),
    path('image-card/<uuid:pk>/', ImageCardDetail.as_view()),
    path('custom-actions/', CustomActionList.as_view()),
    path('custom-actions/<uuid:pk>/', CustomActionDetail.as_view()),
    path('json-card/', JsonCardList.as_view()),
    path('json-card/<uuid:pk>/', JsonCardDetail.as_view()),
    path('form-card/', FormCardList.as_view()),
    path('form-card/<uuid:pk>/', FormCardDetail.as_view()),
    path('form-card/form-slot/', FormSlotList.as_view()),
    path('form-card/form-slot/<uuid:pk>/', FormSlotDetail.as_view()),
    path('action-card/', ActionCardList().as_view()),
    path('action-card/<uuid:pk>/', ActionCardDetail().as_view()),
    path('slot/', SlotList.as_view()),
    path('slot/<uuid:pk>/', SlotDetail.as_view()),
]
