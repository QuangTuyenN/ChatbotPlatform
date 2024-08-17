
# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import FormCardSerializer
from bot.models import FormCard


class FormCardList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FormCardSerializer
    queryset = FormCard.objects.all()


class FormCardDetail(generics.RetrieveUpdateDestroyAPIView):

    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = FormCard.objects.all()
    serializer_class = FormCardSerializer
