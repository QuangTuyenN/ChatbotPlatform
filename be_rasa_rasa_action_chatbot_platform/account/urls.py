from django.urls import path
from .views import AccountList, AccountRoleList, AccountDetail, AccountRoleDetail, RequestPasswordResetEmail, PasswordTokenCheckAPI, SetNewPasswordAPIView
app_name = 'account'

urlpatterns = [
    path('', AccountList.as_view(), name=''),
    path('<uuid:pk>/', AccountDetail.as_view(), name=''),
    path('role/', AccountRoleList.as_view(), name=''),
    path('role/<uuid:pk>/', AccountRoleDetail.as_view(), name=''),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete')

]
