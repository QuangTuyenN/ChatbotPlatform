
# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import FormSlotSerializer
from bot.models import FormSlot


class FormSlotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FormSlotSerializer
    queryset = FormSlot.objects.all()


class FormSlotDetail(generics.RetrieveUpdateDestroyAPIView):

    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = FormSlot.objects.all()
    serializer_class = FormSlotSerializer
