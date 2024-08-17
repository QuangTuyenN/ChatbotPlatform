from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Customize the response here
        response_data = {
            "token": {
                "accessToken": data.get("access"),
                "refreshToken": data.get("refresh"),
            },
            "user": {
                "createdAt": str(self.user.created_at),
                "id": str(self.user.id),
                "fullName": self.user.full_name,
                "userName": self.user.user_name,
                "email": self.user.email,
                "isActive": self.user.is_active
            },
            "isAdminGroup": self.user.is_staff  # Assuming 'is_staff' indicates admin status
        }

        return response_data
