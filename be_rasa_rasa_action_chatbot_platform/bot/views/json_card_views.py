# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import permissions, generics

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import JsonApiSerializer
from bot.models import JsonCard


class JsonCardList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JsonApiSerializer
    queryset = JsonCard.objects.all()


class JsonCardDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JsonApiSerializer
    queryset = JsonCard.objects.all()
