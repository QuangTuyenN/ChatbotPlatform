# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import ChitChatSerializer, ChitChatCustomSerializer
from bot.models import ChitChat
from bot.utils import _get_chitchat_data

# import python lib
import unidecode


def normalize_vietnamese(text):
    # Loại bỏ dấu tiếng Việt
    text = unidecode.unidecode(text)
    # Chuyển thành chữ thường
    text = text.lower()
    return text


class ChitChatList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related(
        "chitchatintentexample_set", "chitchatutterexample_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(name="chitchatIntentName", description="Filter by chitchatIntentName",
                                     required=False, type=str),
                    OpenApiParameter(name="chitchatId", description="Filter by id chitchat",
                                     required=False, type=str)
                    ])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        chitchat_intent_name = request.query_params.get("chitchatIntentName")

        chitchat_id = request.query_params.get("chitchatId")
        if bot is not None and (chitchat_id is None or chitchat_id == ''):
            chitchats = self.queryset.filter(bot=bot).order_by('-created_at')
            if chitchat_intent_name:
                chitchat_intent_name_lower = normalize_vietnamese(chitchat_intent_name)
                if chitchat_intent_name != chitchat_intent_name_lower:
                    chitchats = chitchats.filter(name__icontains=chitchat_intent_name)
                else:
                    chitchats_lower = []
                    for chit in chitchats:
                        if chitchat_intent_name_lower in normalize_vietnamese(chit.name):
                            chitchats_lower.append(chit)
                    chitchats = chitchats_lower
            chits_list = [_get_chitchat_data(chit) for chit in chitchats]
            page = self.paginate_queryset(chits_list)
            serializer = ChitChatCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if bot is not None and chitchat_id is not None:
            chitchats = self.queryset.filter(id=chitchat_id).order_by('-created_at')
            chits_list = [_get_chitchat_data(chit) for chit in chitchats]
            page = self.paginate_queryset(chits_list)
            serializer = ChitChatCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                chit = self.queryset.get(pk=serializer.data["id"])
                chit = _get_chitchat_data(chit)
                return Response(chit, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Dữ liệu không hợp lệ!", status=status.HTTP_400_BAD_REQUEST)


class ChitChatDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related(
        "chitchatintentexample_set", "chitchatutterexample_set")

    # def get(self, request, *args, **kwargs):
    #     chit = self.get_object()
    #     chit = _get_chitchat_data(chit)
    #     return Response(chit, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        chit = self.get_object()
        serializer = self.get_serializer(chit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            chit = _get_chitchat_data(chit)
            return Response(chit, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
