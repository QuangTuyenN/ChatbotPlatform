from menu.views import MenuList, MenuDetail
from django.urls import path

urlpatterns = [
    path('', MenuList.as_view()),
    path('<uuid:pk>/', MenuDetail.as_view())
]
