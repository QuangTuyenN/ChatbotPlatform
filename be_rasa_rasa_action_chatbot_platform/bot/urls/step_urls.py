from bot.views import *
from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', StepList.as_view()),
    path('<uuid:pk>/', StepDetail.as_view()),
    path('get-unuse-intent/', CustomStepIntentList().as_view()),
    path('get-intent-exp-in-intent/', CustomStepIntentExampleList.as_view()),
    path('slot/get-entity-validatetypes/', CustomSlotList().as_view()),
    path('slot/get-slot-formcard/', CustomStepSlotList().as_view())
]
