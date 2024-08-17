# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import SlotSerializer
from bot.serializers import SlotPostStepCustomSerializer
from bot.models import Slot
from bot.models import Entity

# IMPORT PYTHON LIB
import uuid


class SlotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    @extend_schema(
        parameters=[OpenApiParameter(
            name="bot", description="Filter by bot", required=True, type=str)]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        if bot is not None and self.is_valid_uuid(str(bot)) is True:
            slots = self.queryset.filter(bot=bot)
            page = self.paginate_queryset(slots)
            serializers = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializers.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CustomSlotList(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    @extend_schema(
        parameters=[OpenApiParameter(
            name="bot", description="Filter by bot", required=True, type=str)]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        list_validate_types = Slot.VALIDATE_TYPES
        data = []
        if bot is not None and self.is_valid_uuid(str(bot)) is True:
            entities = Entity.objects.filter(bot_id=bot)
            data.append({'list_entity': entities,
                         'list_validate_types': list_validate_types})
            serializer = SlotPostStepCustomSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class SlotDetail(generics.RetrieveUpdateDestroyAPIView):

    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
