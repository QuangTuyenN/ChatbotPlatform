# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import *
from bot.models import *
from core.pagination import StandardResultsSetPagination
from bot.utils import _get_intent_data

# IMPORT PYTHON LIB
from bot.utils import *


class IntentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = IntentSerializer
    queryset = Intent.objects.prefetch_related("intentexample_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(
                        name="intent_name_filter", description="Filter by intent name", required=False, type=str)
                    ])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        intent_name_filter = request.query_params.get("intent_name_filter")
        if bot is not None and is_valid_uuid(str(bot)) is True and (intent_name_filter is None or intent_name_filter == ''):
            intents = self.queryset.filter(bot=bot).order_by('-created_at')
            print("intent: ", intents)
            intents_list = [_get_intent_data(intent) for intent in intents]
            page = self.paginate_queryset(intents_list)
            serializer = IntentCustomSerializer(page, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            # serializer = IntentCustomSerializer(intents_list, many=True)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        elif bot is not None and is_valid_uuid(str(bot)) is True and intent_name_filter is not None:
            intents = self.queryset.filter(bot=bot).order_by('-created_at')
            print("intent: ", intents)
            intents_list = []
            intent_name_filter_lower = normalize_vietnamese(intent_name_filter)
            if intent_name_filter_lower != intent_name_filter:
                intents = intents.filter(name__icontains=intent_name_filter)
                for intent in intents:
                    # if intent_name_filter in intent.name:
                    intents_list.append(_get_intent_data(intent))
            else:
                for intent in intents:
                    if intent_name_filter_lower in normalize_vietnamese(intent.name):
                        intents_list.append(_get_intent_data(intent))
            page = self.paginate_queryset(intents_list)
            serializer = IntentCustomSerializer(page, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        intents = self.queryset.filter(bot=request.data['bot'])
        if len(request.data['name']) > 200:
            return Response("Độ dài của ý định không được quá 200 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        for intent in intents:
            if intent.name == request.data['name']:
                return Response("Tên ý định đã được tạo ở bot này",
                                status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class IntentViewSet(viewsets.GenericViewSet):
    queryset = Intent.objects.all()
    http_method_names = ['get']
    serializer_class = IntentSerializer
    pagination_class = StandardResultsSetPagination  # Sử dụng phân trang

    @extend_schema(parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str)])
    @action(methods=['get'], detail=False)
    def get_unused_intent(self, request, pk=None):
        bot = request.query_params.get("bot")
        intents_data = []
        if bot is not None and is_valid_uuid(str(bot)) is True:
            # Filter intents where bot matches and step_id is None
            unused_intents = self.queryset.filter(
                bot=bot, step_id__isnull=True)
            for intent in unused_intents:
                intents_data.append({'id': intent.id, 'name': intent.name})
            serializer = UnusedIntentCustomSerializer(intents_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class IntentDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Intent.objects.prefetch_related("intentexample_set")
    serializer_class = IntentSerializer

    def put(self, request, *args, **kwargs):
        intent_id = kwargs.get("pk")
        step = request.data.get("step", '')
        print(step)
        # Ensure position is an integer
        if intent_id is not None and is_valid_uuid(str(intent_id)):
            print("go here")
            try:
                intent = self.queryset.get(id=intent_id)
                intents = self.queryset.all()
                for it in intents:
                    if it is not None and it.step is not None and str(it.step.id) != str(step) and str(step) != "":
                        if intent_id == it.id:
                            return Response('Ý định này đã được chọn ở bước khác, vui lòng chọn ý định khác cho bước này', status=status.HTTP_400_BAD_REQUEST)
                serializer = IntentSerializer(
                    intent, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        intent = self.get_object()
        intent_exp = intent.intentexample_set.all()
        print("----------", intent_exp)
        if intent_exp:
            return Response("Ý định đã thiết lập câu mẫu, không thể xóa",
                            status=status.HTTP_403_FORBIDDEN)
        if intent.step:
            return Response("Ý định đã thiết lập trong step, không thể xóa",
                            status=status.HTTP_403_FORBIDDEN)
        # Nếu không trùng, tiếp tục xóa đối tượng
        self.perform_destroy(intent)
        return Response(status=status.HTTP_204_NO_CONTENT)


