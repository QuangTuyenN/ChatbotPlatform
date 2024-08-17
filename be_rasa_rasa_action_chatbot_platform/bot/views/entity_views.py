# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status, permissions, generics
from rest_framework.response import Response
# from rest_framework.exceptions import ParseError

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import EntityCustomSerializer
from bot.serializers import EntityFilterNameCustomSerializer
from bot.serializers import EntityKeyWordExtractTypeCustomSerializer
from bot.serializers import EntitySerializer
from bot.models import Entity
from bot.utils import _get_entities_filter_kw
from bot.utils import _get_entities_kw_extract_type
from bot.utils import _get_entities_filter_name
from bot.utils import _get_entities_data
# IMPORT PYTHON LIB
import uuid
import unidecode


def normalize_vietnamese(text):
    # Loại bỏ dấu tiếng Việt
    text = unidecode.unidecode(text)
    # Chuyển thành chữ thường
    text = text.lower()
    return text


class EntityList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EntitySerializer
    # queryset = Entity.objects.all()
    queryset = Entity.objects.prefetch_related('entitykeyword_set')

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    def post(self, request, *args, **kwargs):
        entities = self.queryset.filter(bot=request.data['bot'])
        for entity in entities:
            if entity.name == request.data['name']:
                return Response("Tên thực thể đã được tạo ở bot này",
                                status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(name="entityExtractType", description="Filter by entity extract type",
                                     required=False, type=str),
                    OpenApiParameter(name="entityName", description="Filter by entity name",
                                     required=False, type=str)
                    ])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        extract_type = request.query_params.get("entityExtractType")
        entity_name = request.query_params.get("entityName")
        if self.is_valid_uuid(str(bot)) is True:
            if bot is not None and (entity_name is None or entity_name == '') and (extract_type is None or extract_type == ''):
                entities = self.queryset.filter(bot=bot).order_by('-created_at')
                entities_list = [_get_entities_data(
                    entity) for entity in entities]
                page = self.paginate_queryset(entities_list)
                serializer = EntityCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            elif extract_type is not None and bot is not None and (entity_name is None or entity_name == ''):
                entities = self.queryset.filter(
                    bot=bot, extract_type=extract_type).order_by('-created_at')
                entities_kw_list = [_get_entities_kw_extract_type(
                    entity) for entity in entities]
                page = self.paginate_queryset(entities_kw_list)
                serializer = EntityKeyWordExtractTypeCustomSerializer(
                    page, many=True)
                return self.get_paginated_response(serializer.data)
            elif (extract_type is None or extract_type == '') and bot is not None and entity_name is not None:
                entities = self.queryset.filter(bot=bot).order_by('-created_at')
                # entities_filter_list = [_get_entities_filter_name(entity, entity_name) for entity in entities]
                # entities_filter_list = [item for item in entities_filter_list if item is not None]
                # if len(entities_filter_list) == 0:
                #     entities_filter_list = [{"id": "", "name": "", "description": "",
                #                              "extract_type": "", "keyword": []}]
                entities_filter_list = []
                try:
                    entity_name_lower = normalize_vietnamese(entity_name)
                    if entity_name_lower != entity_name:
                        entities = entities.filter(name__icontains=entity_name)
                        for entity in entities:
                            # if entity_name in entity.name:
                            entities_kw = [
                                kw.text for kw in entity.entitykeyword_set.all()]
                            entities_filter_list.append({"id": entity.id, "name": entity.name,
                                                        "description": entity.description,
                                                         "extract_type": entity.extract_type, "keyword": entities_kw})
                    else:
                        for entity in entities:
                            if entity_name_lower in normalize_vietnamese(entity.name):
                                entities_kw = [
                                    kw.text for kw in entity.entitykeyword_set.all()]
                                entities_filter_list.append({"id": entity.id, "name": entity.name,
                                                            "description": entity.description,
                                                             "extract_type": entity.extract_type, "keyword": entities_kw})
                except Exception as bug:
                    print("bug: ", bug)
                if len(entities_filter_list) == 0:
                    # entities_filter_list = [{"id": "", "name": "", "description": "",
                    #                         "extract_type": "", "keyword": []}]
                    entities_filter_list = []
                page = self.paginate_queryset(entities_filter_list)
                serializer = EntityFilterNameCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            # elif extract_type is None and bot is not None and entity_name is None and entity_example_text is not None:
            #     entities = self.queryset.filter(bot=bot)
            #     entities_filter_kw_list = [_get_entities_filter_kw(entity, entity_example_text) for entity in entities]
            #     entities_filter_kw_list = [item for item in entities_filter_kw_list if item is not None]
            #     if len(entities_filter_kw_list) == 0:
            #         entities_filter_kw_list = [{"id": "", "name": "", "description": "",
            #                                     "extract_type": "", "keyword": []}]
            #     page = self.paginate_queryset(entities_filter_kw_list)
            #     serializer = EntityFilterNameCustomSerializer(page, many=True)
            #     return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Entity.objects.prefetch_related('entitykeyword_set__intent_example')
    serializer_class = EntitySerializer

    def delete(self, request, *args, **kwargs):
        # Lấy đối tượng cần xóa
        entity = self.get_object()
        for entity_kw in entity.entitykeyword_set.all():
            if entity_kw.intent_example is not None:
                return Response("Thực thể đã được thiết lập trong câu mẫu",
                                status=status.HTTP_403_FORBIDDEN)
        # Nếu không trùng, tiếp tục xóa đối tượng
        self.perform_destroy(entity)
        return Response(status=status.HTTP_204_NO_CONTENT)


