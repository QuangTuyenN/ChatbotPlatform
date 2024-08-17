# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import IntentExampleSerializer, IntentExampleCustomSerializer, IntentExampleFilterCustomSerializer
from bot.models import IntentExample, EntityKeyWord
from bot.utils import _get_intent_exp_data, _get_intent_exp_data_detail

# IMPORT PYTHON LIB
import uuid
from unidecode import unidecode
from django.forms.models import model_to_dict


class IntentExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IntentExampleSerializer
    queryset = IntentExample.objects.select_related(
        'intent', 'bot').prefetch_related('entitykeyword_set')

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    def post(self, request, *args, **kwargs):
        int_exps = self.queryset.filter(bot=request.data['bot'])
        if len(request.data['text']) > 500:
            return Response("Độ dài của câu mẫu không được quá 500 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        for int_exp in int_exps:
            if int_exp.text == request.data['text']:
                return Response("Nội dung câu mẫu đã được tạo ở bot này",
                                status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)
    # def post(self, request, *args, **kwargs):
    #     try:
    #         intent_exp_text = request.data.get('text')
    #         bot = request.data.get('bot')
    #         texts = self.queryset.filter(bot=bot)
    #         for t in texts:
    #             if str(t.text) == str(intent_exp_text):
    #                 return Response('Tên câu mẫu này đã được tạo ở bot này, vui lòng đổi tên khác', status=status.HTTP_403_FORBIDDEN)
    #         serializer = IntentExampleSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         print(e)
    #         return Response(status=status.HTTP_403_FORBIDDEN)

    @extend_schema(parameters=[OpenApiParameter(name="intent", description="Filter by intent", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        intent_id = request.query_params.get("intent")
        if intent_id is not None and self.is_valid_uuid(str(intent_id)) is True:
            intent_exps = self.queryset.filter(intent=intent_id)
            list_int_exps = []
            for intent_exp in intent_exps:
                intent_exp_dict = {"id": intent_exp.id, "intent_name": intent_exp.intent.name,
                                   "text": intent_exp.text, "entity": []}
                entity_keywords = intent_exp.entitykeyword_set.all()
                for entity_keyword in entity_keywords:
                    intent_exp_dict["entity"].append(
                        entity_keyword.entity.name)
                intent_exp_dict["entity"] = list(
                    set(intent_exp_dict["entity"]))
                list_int_exps.append(intent_exp_dict)
            if len(list_int_exps) == 0:
                list_int_exps = [{"id": "", "intent_name": "", "text": "", "entity": []}]
            page = self.paginate_queryset(list_int_exps)
            serializer = IntentExampleFilterCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class IntentExampleSearch(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = IntentExample.objects.all().order_by('-created_at')
    serializer_class = IntentExampleSerializer

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(
                        name="intentName", description="Filter by intent name", required=False, type=str),
                    OpenApiParameter(
                        name="entityName", description="Filter by entity name", required=False, type=str),
                    OpenApiParameter(
                        name="intentText", description="Filter by intent text", required=False, type=str)
                    ]
    )
    def get(self, request, *args, **kwargs):
        intent_name = request.query_params.get("intentName", '').lower()
        entity_name = request.query_params.get('entityName', '').lower()
        intent_text = request.query_params.get('intentText', '').lower()
        if len(intent_name) > 200:
            return Response("Độ dài intent_name không được quá 200 ký tự, vui lòng sửa lại.",status=status.HTTP_403_FORBIDDEN)
        if len(entity_name) > 200:
            return Response("Độ dài entity_name không được quá 200 ký tự, vui lòng sửa lại.",status=status.HTTP_403_FORBIDDEN)
        if len(intent_text) > 500:
            return Response("Độ dài intent_text không được quá 500 ký tự, vui lòng sửa lại.",status=status.HTTP_403_FORBIDDEN)
        intent_name_unidecode = unidecode(intent_name)
        entity_name_unidecode = unidecode(entity_name)
        intent_text_unidecode = unidecode(intent_text)
        bot = request.query_params.get("bot")

        if bot is not None and self.is_valid_uuid(str(bot)) is True:
            intent_exp = self.queryset.filter(bot=bot)
            # Sử dụng select_related và prefetch_related để giảm số lượng query
            intent_exp = intent_exp.select_related('intent').prefetch_related('entitykeyword_set__entity')
            #intent_exp_unidecode = []
            if intent_name:
                if intent_name != intent_name_unidecode:
                    intent_exp = intent_exp.filter(intent__name__icontains=intent_name)
                else:
                    intent_exp_unidecode = []
                    for i in intent_exp:
                        if intent_name_unidecode in unidecode(str(i.intent).lower()):
                            intent_exp_unidecode.append(i)
                    intent_exp = intent_exp_unidecode

            # if entity_name:
            #     if entity_name != entity_name_unidecode:
            #         intent_exp = intent_exp.filter(entitykeyword__entity__name__icontains=entity_name).distinct()
            #     else:
            #         intent_exp_unidecode = []
            #         for i in intent_exp:
            #             if entity_name_unidecode in unidecode(i.entitykeyword_set.first().entity.name.lower() if i.entitykeyword_set.exists() else ''):
            #                 intent_exp_unidecode.append(i)
            #         intent_exp = intent_exp_unidecode
            if entity_name:
                if entity_name != entity_name_unidecode:
                    intent_exp = intent_exp.filter(entitykeyword__entity__name__icontains=entity_name)
                else:
                    intent_exp_unidecode = []
                    for i in intent_exp:
                        entities_kw = i.entitykeyword_set.all()
                        print(" entities_kw", entities_kw)
                        for ek in entities_kw:
                            if entity_name_unidecode in unidecode(ek.entity.name.lower()):
                                intent_exp_unidecode.append(i)
                    intent_exp = intent_exp_unidecode

            if intent_text:
                if intent_text != intent_text_unidecode:
                    intent_exp = intent_exp.filter(text__icontains=intent_text)
                else:
                    intent_exp_unidecode = []
                    for i in intent_exp:
                        if intent_text_unidecode in unidecode(i.text.lower()):
                            intent_exp_unidecode.append(i)
                    intent_exp = intent_exp_unidecode
            data = [_get_intent_exp_data(i) for i in intent_exp]
            page = self.paginate_queryset(data)
            serializer = IntentExampleCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="exps", description="List of IDs to delete", required=True, type=str)
        ]
    )
    def delete(self, request, *args, **kwargs):
        exps = request.query_params.get('exps', '')
        if exps:
            try:
                # Remove brackets and split the string by commas to get individual IDs
                exps = exps.strip('[]').split(',')
                IntentExample.objects.filter(id__in=exps).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)


class IntentExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IntentExampleSerializer
    queryset = IntentExample.objects.prefetch_related('entitykeyword_set')

    def get(self, request, *args, **kwargs):
        intent_exp_id = kwargs.get("pk")
        if intent_exp_id:
            intent_exp = self.queryset.filter(id=intent_exp_id)
            # Sử dụng select_related và prefetch_related để giảm số lượng query
            intent_exp = intent_exp.select_related(
                'intent').prefetch_related('entitykeyword_set__entity')
            data = [_get_intent_exp_data_detail(i) for i in intent_exp]
            return Response(data)
        return Response({"detail": "Not found."}, status=404)

    def put(self, request, *args, **kwargs):
        intentexample = self.get_object()
        bot = intentexample.bot
        intentexamples = self.queryset.filter(bot=bot)
        old_text = intentexample.text
        new_text = request.data['text']
        intent_exp_filters = intentexamples.filter(text=new_text)
        count = intent_exp_filters.count()
        if count > 1:
            return Response('Câu mẫu đã được sử dụng ở các ý định khác, vui lòng đổi câu khác',
                            status=status.HTTP_400_BAD_REQUEST)
        if len(request.data['text']) > 500:
            return Response("Độ dài của câu mẫu không được quá 500 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        entity_keywords = intentexample.entitykeyword_set.all()
        for entity_keyword in entity_keywords:
            entity_keyword.delete()
        serializer = self.get_serializer(intentexample, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Đã xóa toàn bộ entity keyword của intent example '
                        'muốn sửa nội dung và cập nhật nội dung mới', status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        intentexample = self.get_object()
        entity_keywords = intentexample.entitykeyword_set.all()
        if entity_keywords is not None:
            for entity_keyword in entity_keywords:
                entity_keyword.delete()
        self.perform_destroy(intentexample)
        return Response('Đã xóa intent example ', status=status.HTTP_204_NO_CONTENT)
