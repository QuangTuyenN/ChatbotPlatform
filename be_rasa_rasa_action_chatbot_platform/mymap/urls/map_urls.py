from mymap.views import *
from django.urls import path

urlpatterns = [
    path('root/', MapRootList.as_view()),
    path('child/', MapChildList.as_view()),
    path('root/<uuid:pk>/', MapRootDetail.as_view()),
    path('child/<uuid:pk>/', MapChildDetail.as_view()),

]