# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import ChitChatUtterExampleSerializer, ChitChatUtterExampleCustomSerializer
from bot.models import ChitChatUtterExample


class ChitChatUtterExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChitChatUtterExampleSerializer
    queryset = ChitChatUtterExample.objects.all()

    def post(self, request, *args, **kwargs):
        chitchatuttexps = self.queryset.filter(bot=request.data['bot'])
        if len(request.data['text']) > 1000:
            return Response("Câu trả lời chitchat không được quá 1000 kí tự",
                            status=status.HTTP_403_FORBIDDEN)
        for chitchatuttexp in chitchatuttexps:
            if chitchatuttexp.text == request.data['text']:
                return Response("Câu trả lời chitchat đã được tạo ở bot này",
                                status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    @extend_schema(
        parameters=[OpenApiParameter(name="chitchat", description="Filter by chitchat", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        chit = request.query_params.get("chitchat")
        if chit is not None:
            exps = self.queryset.filter(chitchat=chit).order_by('-created_at')
            ###################
            page = self.paginate_queryset(exps)
            serializer = ChitChatUtterExampleCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            ###################
            # exps = self.get_serializer(exps, many=True)
            # return Response(exps.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ChitChatUtterExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChitChatUtterExample.objects.all()
    serializer_class = ChitChatUtterExampleSerializer

    def put(self, request, *args, **kwargs):
        chitchat_exp = self.get_object()
        bot = chitchat_exp.bot
        chitchat_exps = self.queryset.filter(bot=bot)
        new_text = request.data['text']
        chitchat_exps_filter = chitchat_exps.filter(text=new_text)
        count = chitchat_exps_filter.count()
        if count > 1:
            return Response('Câu trả lời chitchat đã được sử dụng ở các chitchat khác, vui lòng đổi câu khác',
                            status=status.HTTP_400_BAD_REQUEST)
        if len(request.data['text']) > 1000:
            return Response("Câu trả lời chitchat không được quá 1000 kí tự",
                            status=status.HTTP_403_FORBIDDEN)
        # Nếu không trùng, cập nhật đối tượng với dữ liệu mới
        serializer = self.get_serializer(chitchat_exp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
