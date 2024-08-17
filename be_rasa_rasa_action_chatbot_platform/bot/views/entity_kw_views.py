# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import EntityKeyWordSerializer
from bot.serializers import EntityKeyWordBotCustomSerializer
from bot.serializers import EntityKeyWordCustomSerializer
from bot.models import EntityKeyWord
from bot.utils import _get_entities_kw_data

# IMPORT PYTHON LIB
import uuid
import unidecode


def normalize_vietnamese(text):
    # Loại bỏ dấu tiếng Việt
    text = unidecode.unidecode(text)
    # Chuyển thành chữ thường
    text = text.lower()
    return text


class EntityKeyWordList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EntityKeyWordSerializer
    queryset = EntityKeyWord.objects.select_related('entity')

    def post(self, request, *args, **kwargs):
        if len(request.data['text']) > 200:
            return Response("Độ dài của từ khóa không được quá 200 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    @extend_schema(
        parameters=[OpenApiParameter(name="entity", description="Filter by entity", required=False, type=str),
                    OpenApiParameter(
                        name="bot", description="Filter by bot", required=False, type=str),
                    OpenApiParameter(
                        name="entityName", description="Filter by entity name", required=False, type=str),
                    OpenApiParameter(name="entityExampleText", description="Filter by entity example text",
                                     required=False, type=str)])
    def get(self, request, *args, **kwargs):   # phần get entity keywords
        entity = request.query_params.get("entity")
        bot = request.query_params.get("bot")
        entity_search_name = request.query_params.get("entityName")
        entity_example_text = request.query_params.get("entityExampleText")
        if entity is not None and (bot is None or bot == '') and (entity_search_name is None or entity_search_name == '') and (entity_example_text is None or entity_example_text == ''):
            entities_kw = self.queryset.filter(entity=entity).order_by('-created_at')
            print("entities_kw: ", entities_kw)
            entities_kw_list = [_get_entities_kw_data(
                entity_kw) for entity_kw in entities_kw]
            print("list: ", entities_kw_list)
            page = self.paginate_queryset(entities_kw_list)
            serializer = EntityKeyWordCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if (entity is None or entity == '') and bot is not None and (entity_search_name is None or entity_search_name == '') and (entity_example_text is None or entity_example_text == ''):
            entities_kw = self.queryset.filter(entity__bot=bot).order_by('-created_at')
            entities_kw_list_bot = []
            try:
                for entity_kw in entities_kw:
                    entities_kw_list_bot.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                 "extract_type": entity_kw.entity.extract_type,
                                                 "keyword": entity_kw.text})
            except Exception as bug:
                print("bug: ", bug)
            if len(entities_kw_list_bot) == 0:
                # entities_kw_list_bot = [
                #     {"id": "", "entity": "", "extract_type": "", "keyword": ""}]
                entities_kw_list_bot = []
            page = self.paginate_queryset(entities_kw_list_bot)
            serializer = EntityKeyWordBotCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if (entity is None or entity == '') and bot is not None and entity_search_name is not None and (entity_example_text is None or entity_example_text == ''):
            entities_kw = self.queryset.filter(entity__bot=bot).order_by('-created_at')
            entities_kw_list_filter_name = []
            try:
                entity_search_name_lower = normalize_vietnamese(entity_search_name)
                if entity_search_name_lower != entity_search_name:
                    entities_kw = entities_kw.filter(entity__name__icontains=entity_search_name)
                    for entity_kw in entities_kw:
                        # if entity_search_name in entity_kw.entity.name:
                        entities_kw_list_filter_name.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                             "extract_type": entity_kw.entity.extract_type,
                                                             "keyword": entity_kw.text})
                else:
                    for entity_kw in entities_kw:
                        if entity_search_name_lower in normalize_vietnamese(entity_kw.entity.name):
                            entities_kw_list_filter_name.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                                 "extract_type": entity_kw.entity.extract_type,
                                                                 "keyword": entity_kw.text})
            except Exception as bug:
                print("bug: ", bug)
            if len(entities_kw_list_filter_name) == 0:
                # entities_kw_list_filter_name = [
                #     {"id": "", "entity": "", "extract_type": "", "keyword": ""}]
                entities_kw_list_filter_name = []
            page = self.paginate_queryset(entities_kw_list_filter_name)
            serializer = EntityKeyWordBotCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if (entity is None or entity == '') and bot is not None and (entity_search_name is None or entity_search_name == '') and entity_example_text is not None:
            entities_kw = self.queryset.filter(entity__bot=bot).order_by('-created_at')
            entities_kw_list_filter_text = []
            try:
                entity_example_text_lower = normalize_vietnamese(entity_example_text)
                if entity_example_text_lower != entity_example_text:
                    entities_kw = entities_kw.filter(text__icontains=entity_example_text)
                    for entity_kw in entities_kw:
                        # if entity_example_text in entity_kw.text:
                        entities_kw_list_filter_text.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                             "extract_type": entity_kw.entity.extract_type,
                                                             "keyword": entity_kw.text})
                else:
                    for entity_kw in entities_kw:
                        if entity_example_text_lower in normalize_vietnamese(entity_kw.text):
                            entities_kw_list_filter_text.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                                 "extract_type": entity_kw.entity.extract_type,
                                                                 "keyword": entity_kw.text})
            except Exception as bug:
                print("bug: ", bug)
            if len(entities_kw_list_filter_text) == 0:
                # entities_kw_list_filter_text = [
                #     {"id": "", "entity": "", "extract_type": "", "keyword": ""}]
                entities_kw_list_filter_text = []
            page = self.paginate_queryset(entities_kw_list_filter_text)
            serializer = EntityKeyWordBotCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if (entity is None or entity == '') and bot is not None and entity_search_name is not None \
                and entity_example_text is not None:
            entities_kw = self.queryset.filter(entity__bot=bot).order_by('-created_at')
            entities_kw_list_filter_text = []
            try:
                entity_search_name_lower = normalize_vietnamese(entity_search_name)
                entity_example_text_lower = normalize_vietnamese(entity_example_text)
                if entity_example_text_lower != entity_example_text and entity_search_name_lower != entity_search_name:
                    entities_kw = entities_kw.filter(entity__name__icontains=entity_search_name)
                    entities_kw = entities_kw.filter(text__icontains=entity_example_text)
                    for entity_kw in entities_kw:
                        # if entity_example_text_lower in normalize_vietnamese(entity_kw.text) \
                        #         and entity_search_name_lower in normalize_vietnamese(entity_kw.entity.name):
                        entities_kw_list_filter_text.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                             "extract_type": entity_kw.entity.extract_type,
                                                             "keyword": entity_kw.text})
                else:
                    for entity_kw in entities_kw:
                        if entity_example_text_lower in normalize_vietnamese(entity_kw.text) \
                                and entity_search_name_lower in normalize_vietnamese(entity_kw.entity.name):
                            entities_kw_list_filter_text.append({"id": entity_kw.id, "entity": entity_kw.entity.name,
                                                                 "extract_type": entity_kw.entity.extract_type,
                                                                 "keyword": entity_kw.text})
            except Exception as bug:
                print("bug: ", bug)
            if len(entities_kw_list_filter_text) == 0:
                # entities_kw_list_filter_text = [
                #     {"id": "", "entity": "", "extract_type": "", "keyword": ""}]
                entities_kw_list_filter_text = []
            page = self.paginate_queryset(entities_kw_list_filter_text)
            serializer = EntityKeyWordBotCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class EntityKeyWordDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = EntityKeyWord.objects.all()
    serializer_class = EntityKeyWordSerializer
