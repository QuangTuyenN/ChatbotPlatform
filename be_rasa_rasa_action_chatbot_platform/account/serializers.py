from rest_framework import serializers
from account.models import Account, AccountRole
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        # data.pop('refresh', None)  # remove refresh from the payload
        data['access'] = str(refresh.access_token)

        # Add extra responses here
        data['id'] = str(self.user.id)
        data['user_name'] = str(self.user.user_name)
        data['email'] = str(self.user.email)
        data['full_name'] = str(self.user.full_name)
        data['image'] = str(self.user.image)

        return data


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class AccountRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRole
        fields = '__all__'


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']