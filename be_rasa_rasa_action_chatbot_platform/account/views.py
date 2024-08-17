from account.models import AccountRole, Account
from account.serializers import AccountRoleSerializer, AccountSerializer
from rest_framework import generics, status
from rest_framework import permissions
from core.pagination import StandardResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions, generics


# SEND MAIL
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from .custom_serializers import *
from django.http import HttpResponsePermanentRedirect
import os

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from .models import Account
from .serializers import ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from django.core.mail import EmailMessage


def send_email(data):
    email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
    email.send()


class AccountList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]

    queryset = Account.objects.all()

    serializer_class = AccountSerializer

    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['GET'])
    def custom_action(self, request):
        # Custom action logic for POST request
        # Perform any operation with the posted data
        return Response({'message': 'Custom POST action executed successfully.'})


class AccountDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    http_method_names = ['get', 'post', 'put', 'delete']


class AccountRoleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = AccountRole.objects.all()
    serializer_class = AccountRoleSerializer
    pagination_class = StandardResultsSetPagination

    # @action(detail=False, methods=['GET'])
    # def custom_action(self, request):
    #     # Custom action logic for POST request
    #     # Perform any operation with the posted data
    #     return Response({'message': 'Custom POST action executed successfully.'})


class AccountRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = AccountRole.objects.all()
    serializer_class = AccountRoleSerializer
    http_method_names = ['get', 'post', 'put', 'delete']


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('account:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + relativeLink
            email_body = f'Hello, \n Use the link below to reset your password  \n{absurl}'
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your password'}
            send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')
        print(redirect_url)

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

