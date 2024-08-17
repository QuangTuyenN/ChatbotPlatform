# built-in
import json
import os
import yaml
import time
import requests
import functools
# framework
# from kubernetes import client
from django.http import Http404
from django.db import connection, reset_queries
# from django.db.models import Prefetch
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.exceptions import ParseError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

# custom module
from bot.serializers import *
from core.pagination import StandardResultsSetPagination
from bot.models import *


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print("Function : " + func.__name__)
        print("Number of Queries : {}".format(end_queries - start_queries))
        print("Finished in : {}".format(end - start))

        return result

    return inner_func


def _get_chitchat_data(chit):
    int_exps = [exp.text for exp in chit.chitchatintentexample_set.all() if str(exp.chitchat) == str(chit.name)]
    utt_exps = [exp.text for exp in chit.chitchatutterexample_set.all() if str(exp.chitchat) == str(chit.name)]
    return {"id": chit.id, "name": chit.name, "int_exps": int_exps, "utt_exps": utt_exps}


def _get_intent_data(intent):
    int_exps = [exp.text for exp in intent.intentexample_set.all() if str(exp.intent) == str(intent.name)]
    return {"id": intent.id, "description": intent.description, "name": intent.name, "int_exps": int_exps}


def _get_entities_data(entity):
    entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
    return {"id": entity.id, "name": entity.name, "description": entity.description,
            "extract_type": entity.extract_type, "entities_kw": entities_kw}


def _get_entities_kw_extract_type(entity):
    entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
    return {"id": entity.id, "name": entity.name, "extract_type": entity.extract_type, "keyword": entities_kw}


def _get_entities_filter_name(entity, entity_name):
    if entity_name in entity.name:
        entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
        return {"id": entity.id, "name": entity.name, "description": entity.description,
                "extract_type": entity.extract_type, "keyword": entities_kw}
    else:
        return None


def _get_entities_filter_kw(entity, entity_example_text):
    entities_kw = []
    for kw in entity.entitykeyword_set.all():
        if entity_example_text in kw.text:
            entities_kw.append(kw.text)
    if len(entities_kw) != 0:
        return {"id": entity.id, "name": entity.name, "description": entity.description,
                "extract_type": entity.extract_type, "keyword": entities_kw}
    else:
        return None


def _get_entities_kw_data(entity_kw):
    return {"id": entity_kw.id, "text": entity_kw.text}


def _get_summary_data(bot):
    counts = {
        "chitchats": bot.chitchat_set.count(),
        "chitchat_intent_examples": bot.chitchatintentexample_set.count(),
        "chitchat_utter_examples": bot.chitchatutterexample_set.count(),
        "intents": bot.intent_set.count(),
        "intent_examples": bot.intentexample_set.count(),
        "entities": bot.entity_set.count(),
        "stories": bot.story_set.count()
    }

    return counts


def _get_story_data(story):
    data = {
        "id": story.id,
        "name": story.name,
        "steps": [

        ]

    }


class BotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related("chitchat_set",
                                            "chitchatintentexample_set",
                                            "chitchatutterexample_set",
                                            "intent_set",
                                            "intentexample_set",
                                            "entity_set",
                                            "story_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="account", description="Filter by account", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        bots = self.queryset
        account = request.query_params.get("account")
        if account is not None:
            bots = bots.filter(account=account)

            bots_list = []
            for bot in bots:
                summary = _get_summary_data(bot)
                bot = BotSerializer(bot).data
                bot["summary"] = summary
                bots_list.append(bot)

            return Response(bots_list, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         bot = self.queryset.get(pk=serializer.data["id"])
    #         summary = _get_summary_data(bot)
    #         bot = self.get_serializer(bot).data
    #         bot["summary"] = summary
    #         bot_id = bot["id"]
    #         # tao bot trong kubernetes
    #         create_bot_kube(bot_id=bot_id)
    #         return Response(bot, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bot = self.perform_create(serializer)
        summary = _get_summary_data(bot)
        headers = self.get_success_headers(serializer.data)
        bot_data = serializer.data
        bot_data["summary"] = summary
        return Response(bot_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        bot = serializer.save()
        try:
            create_bot_kube(bot_id=str(bot.id))
            return bot
        except Exception as bug:
            print("Error in perfrom create: ", bug)
            bot.delete()
            delete_bot_kube(bot_id=str(bot.id))
            raise Http404


class BotDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer

    queryset = Bot.objects.prefetch_related("chitchat_set",
                                            "chitchatintentexample_set",
                                            "chitchatutterexample_set",
                                            "intent_set",
                                            "intentexample_set",
                                            "entity_set",
                                            "story_set")

    # def get(self, request, *args, **kwargs):
    #     bot = self.get_object()
    #     summary = _get_summary_data(bot)
    #     bot = self.get_serializer(bot).data
    #     bot["summary"] = summary
    #     return Response(bot)

    def put(self, request, *args, **kwargs):
        bot = self.get_object()
        serializer = self.get_serializer(bot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            summary = _get_summary_data(bot)
            bot = serializer.data
            bot["summary"] = summary
            return Response(bot, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        bot = self.get_object()
        try:
            delete_bot_kube(bot_id=str(bot.id))
            print("Bot deleted!")
            return self.destroy(request, *args, **kwargs)
        except Exception as error:
            print("Error when deleting bot: ", error)
            return self.destroy(request, *args, **kwargs)


class BotTrain(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related("chitchat_set").prefetch_related("chitchat_set__chitchatintentexample_set",
                                                                             "chitchat_set__chitchatutterexample_set")

    duckling_url = os.environ.get("DUCKLING_URL", "http://duckling-cbp-kube.chat.svc.cluster.local:8000")

    def get(self, request, *args, **kwargs):
        bot = self.get_object()
        bot_id_str = str(bot.id)
        chitchats = bot.chitchat_set.all()
        intent_conf = bot.intent_confidence
        entities = bot.entity_set.all()
        intents = bot.intent_set.all()
        stories = bot.story_set.all()
        data_send = {"assistant_id": bot_id_str,
                     "language": "vi",
                     "pipeline": [
                         {"name": "WhitespaceTokenizer"},
                         {"name": "RegexFeaturizer"},
                         {"name": "LexicalSyntacticFeaturizer"},
                         {"name": "CountVectorsFeaturizer"},
                         {
                             "name": "CountVectorsFeaturizer",
                             "analyzer": "char_wb",
                             "min_ngram": 1,
                             "max_ngram": 4
                         },
                         {
                             "name": "DIETClassifier",
                             "epochs": 100,
                             "constrain_similarities": "true"
                         },
                         {"name": "EntitySynonymMapper"},
                         {
                             "name": "ResponseSelector",
                             "epochs": 100,
                             "retrieval_intent": "chitchat"
                         },
                         {
                             "name": "FallbackClassifier",
                             "threshold": intent_conf,
                             "ambiguity_threshold": 0.1
                         },
                         {"name": "DucklingEntityExtractor",
                          "url": f"{self.duckling_url}",
                          "dimensions": ["time", "number", "amount-of-money", "distance"],
                          "locale": "vi_VI",
                          "timezone": "Asia/Ho_Chi_Minh",
                          "timeout": 3}
                     ],
                     "policies": [
                         {"name": "MemoizationPolicy"},
                         {"name": "RulePolicy"},
                         {
                             "name": "UnexpecTEDIntentPolicy",
                             "max_history": 5,
                             "epochs": 100
                         },
                         {
                             "name": "TEDPolicy",
                             "max_history": 5,
                             "epochs": 100,
                             "constrain_similarities": "true"
                         }
                     ],
                     "intents": ["chitchat"],
                     "responses": {
                         "utter_default": [{"text": str(bot.default_answer_low_conf)}]
                     },
                     "session_config": {
                         "session_expiration_time": 60,
                         "carry_over_slots_to_new_session": True
                     },
                     "nlu": [],
                     "rules": [
                         {
                             "rule": "chitchat",
                             "steps": [
                                 {"intent": "chitchat"},
                                 {"action": "utter_chitchat"}
                             ]
                         }
                     ],
                     "stories": [
                         {
                             "story": "chitchat",
                             "steps": [
                                 {"intent": "chitchat"},
                                 {"action": "utter_chitchat"}
                             ]
                         }
                     ]
                     }

        for chit in chitchats:
            data_send["responses"][f"utter_chitchat/{chit.name}"] = []
            for exp in chit.chitchatutterexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    data_send["responses"][f"utter_chitchat/{chit.name}"].append({"text": str(exp.text)})
            data_send["nlu"].append({"intent": f"chitchat/{chit.name}", "examples": ""})
            for exp in chit.chitchatintentexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    for i in data_send["nlu"]:
                        if i["intent"] == f"chitchat/{chit.name}":
                            i["examples"] = i["examples"] + "- " + str(exp.text) + "\n"
        for intent in intents:
            # print("intent step: ", intent.step.num_order)
            data_send['intents'].append(intent.name)
            data_send['nlu'].append({'intent': f'{intent.name}', 'examples': ''})
            for intex in intent.intentexample_set.all():
                for i in data_send['nlu']:
                    if i['intent'] == intent.name:
                        i['examples'] = i['examples'] + '- ' + str(intex.text) + '\n'
                # print("intentexample: ", intex)

        for entity in entities:
            data_send['entities'].append(entity.name)
            data_send['slots'].append(entity.name)

        print("---------------------------------")
        print(data_send)
        print("---------------------------------")

        try:
            # train
            yaml_content = yaml.dump(data_send, default_flow_style=False)
            api_train = os.environ.get("API_TRAIN_BOT", f"http://bot-{bot_id_str}:5005/model/train")
            headers = {"Content-Type": "application/yaml"}
            response = requests.post(api_train, data=yaml_content, headers=headers)

            # replace old with new
            model_name = response.headers["filename"]
            path_model_inside_pod = os.environ.get("BOT_MODEL_PATH", "/app/models/")
            json_put_model = {"model_file": path_model_inside_pod + model_name}
            api_replace_old_model = os.environ.get("API_REPLACE_BOT", f"http://bot-{bot_id_str}:5005/model")
            headers_put = {"Content-Type": "application/json"}
            response2 = requests.put(api_replace_old_model, data=json.dumps(json_put_model), headers=headers_put)

            print("Response CODE for PUT Model: ", response2.status_code)
            return Response({"status": "Huấn luyện thành công!"}, status=status.HTTP_200_OK)

        except Exception as bug:
            print("Error when train model", bug)
            return Response({"status": f"Có lỗi xảy ra trong quá trình huấn luyện: {bug}"},
                            status=status.HTTP_400_BAD_REQUEST)


class ChitChatList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related("chitchatintentexample_set", "chitchatutterexample_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(
                        name='page',
                        type=OpenApiTypes.INT,
                        location=OpenApiParameter.QUERY,
                        required=False,
                        description='A page number within the paginated result set.'
                    ),
                    OpenApiParameter(
                        name='page_size',
                        type=OpenApiTypes.INT,
                        location=OpenApiParameter.QUERY,
                        required=False,
                        description='Number of results to return per page.'
                    ),
                    ],
        responses=ChitChatCustomSerializer(many=True)
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        if bot is not None:
            chitchats = self.queryset.filter(bot=bot)
            chits_list = [_get_chitchat_data(chit) for chit in chitchats]
            page = self.paginate_queryset(chits_list)
            serializer = ChitChatCustomSerializer(page, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            serializer = ChitChatCustomSerializer(chits_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChitChatDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related("chitchatintentexample_set", "chitchatutterexample_set")

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


class ChitChatIntentExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatIntentExampleSerializer
    queryset = ChitChatIntentExample.objects.all()

    @extend_schema(
        parameters=[OpenApiParameter(name="chitchat", description="Filter by chitchat", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        chit = request.query_params.get("chitchat")
        if chit is not None:
            exps = self.queryset.filter(chitchat=chit)
            exps = self.get_serializer(exps, many=True)
            return Response(exps.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ChitChatIntentExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatIntentExampleSerializer
    queryset = ChitChatIntentExample.objects.all()


class ChitChatUtterExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatUtterExampleSerializer
    queryset = ChitChatUtterExample.objects.all()

    @extend_schema(
        parameters=[OpenApiParameter(name="chitchat", description="Filter by chitchat", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        chit = request.query_params.get("chitchat")
        if chit is not None:
            exps = self.queryset.filter(chitchat=chit)
            exps = self.get_serializer(exps, many=True)
            return Response(exps.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ChitChatUtterExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = ChitChatUtterExample.objects.all()
    serializer_class = ChitChatUtterExampleSerializer


class IntentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = IntentSerializer
    queryset = Intent.objects.prefetch_related("intentexample_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        if bot is not None:
            intents = self.queryset.filter(bot=bot)
            print("intent: ", intents)
            intents_list = [_get_intent_data(intent) for intent in intents]
            page = self.paginate_queryset(intents_list)
            serializer = IntentCustomSerializer(page, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            # serializer = IntentCustomSerializer(intents_list, many=True)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class IntentViewSet(viewsets.GenericViewSet):
    queryset = Intent.objects.all()
    http_method_names = ['get']
    serializer_class = IntentSerializer
    pagination_class = StandardResultsSetPagination  # Sử dụng phân trang tùy chỉnh

    @extend_schema(parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str)])
    @action(methods=['get'], detail=False)
    def get_unused_intent(self, request, pk=None):
        bot = request.query_params.get("bot")
        intents_data = []
        if bot is not None:
            # Filter intents where bot matches and step_id is None
            unused_intents = self.queryset.filter(bot=bot, step_id__isnull=True)
            for intent in unused_intents:
                intents_data.append({'id': intent.id, 'name': intent.name})
            serializer = UnusedIntentCustomSerializer(intents_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class IntentDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Intent.objects.all()
    serializer_class = IntentSerializer


class EntityList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = EntitySerializer
    # queryset = Entity.objects.all()
    queryset = Entity.objects.prefetch_related('entitykeyword_set')

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(name="entityExtractType", description="Filter by entity extract type",
                                     required=False, type=str),
                    OpenApiParameter(name="entityName", description="Filter entity name", required=False, type=str),
                    OpenApiParameter(name="entityExampleText", description="Filter entity keyword",
                                     required=False, type=str)])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        extract_type = request.query_params.get("entityExtractType")
        entity_name = request.query_params.get("entityName")
        entity_example_text = request.query_params.get("entityExampleText")
        if bot is not None and extract_type is None and entity_name is None and entity_example_text is None:
            entities = self.queryset.filter(bot=bot)
            entities_list = [_get_entities_data(entity) for entity in entities]
            page = self.paginate_queryset(entities_list)
            serializer = EntityCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        elif extract_type is not None and bot is not None and entity_name is None and entity_example_text is None:
            entities = self.queryset.filter(bot=bot, extract_type=extract_type)
            entities_kw_list = [_get_entities_kw_extract_type(entity) for entity in entities]
            page = self.paginate_queryset(entities_kw_list)
            serializer = EntityKeyWordExtractTypeCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        elif extract_type is None and bot is not None and entity_name is not None and entity_example_text is None:
            entities = self.queryset.filter(bot=bot)
            try:
                entities_filter_list = [_get_entities_filter_name(entity, entity_name) for entity in entities]
                entities_filter_list = [item for item in entities_filter_list if item is not None]
                if len(entities_filter_list) == 0:
                    entities_filter_list = [{"id": "", "name": "", "description": "",
                                             "extract_type": "", "keyword": []}]
            except Exception as bug:
                print("bug: ", bug)
            page = self.paginate_queryset(entities_filter_list)
            serializer = EntityFilterNameCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        elif extract_type is None and bot is not None and entity_name is None and entity_example_text is not None:
            entities = self.queryset.filter(bot=bot)
            entities_filter_kw_list = [_get_entities_filter_kw(entity, entity_example_text) for entity in entities]
            entities_filter_kw_list = [item for item in entities_filter_kw_list if item is not None]
            if len(entities_filter_kw_list) == 0:
                entities_filter_kw_list = [{"id": "", "name": "", "description": "",
                                            "extract_type": "", "keyword": []}]
            page = self.paginate_queryset(entities_filter_kw_list)
            serializer = EntityFilterNameCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer


class EntityKeyWordList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = EntityKeyWordSerializer
    queryset = EntityKeyWord.objects.select_related('entity')

    @extend_schema(
        parameters=[OpenApiParameter(name="entity", description="Filter by entity", required=False, type=str),
                    OpenApiParameter(name="bot", description="Filter by bot", required=False, type=str)])
    def get(self, request, *args, **kwargs):
        entity = request.query_params.get("entity")
        bot = request.query_params.get("bot")
        if entity is not None and bot is None:
            entities_kw = self.queryset.filter(entity=entity)
            print("entities_kw: ", entities_kw)
            entities_kw_list = [_get_entities_kw_data(entity_kw) for entity_kw in entities_kw]
            print("list: ", entities_kw_list)
            page = self.paginate_queryset(entities_kw_list)
            serializer = EntityKeyWordCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if entity is None and bot is not None:
            entities_kw = self.queryset.all()
            print("entities kw: ", entities_kw)
            entities_kw_list_bot = []
            try:
                for entity_kw in entities_kw:
                    entities_kw_list_bot.append({"id": entity_kw.entity.id, "entity": entity_kw.entity.name,
                                                 "extract_type": entity_kw.entity.extract_type,
                                                 "keyword": entity_kw.text})
            except Exception as bug:
                print("bug: ", bug)
        return Response(status=status.HTTP_403_FORBIDDEN)


class EntityKeyWordDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = EntityKeyWord.objects.all()
    serializer_class = EntityKeyWordSerializer


class StoryList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = StorySerializer
    queryset = Story.objects.prefetch_related('step_set')

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(name="storyName", description="Filter by story name", required=False, type=str),
                    OpenApiParameter(name="stepName", description="Filter by step name", required=False, type=str)]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        storyName = request.query_params.get("storyName", '')
        stepName = request.query_params.get('stepName', '')
        data = []
        if bot is not None:
            stories = self.queryset.filter(bot=bot)
            if storyName:
                stories = stories.filter(name__icontains=storyName)
            for story in stories:
                steps_data = []
                steps = story.step_set.all()
                # print("steps value",steps.values())
                for step in steps:
                    intent = Intent.objects.filter(step=step.id)
                    if stepName:
                        # print(stepName.lower())
                        # print(step.name)
                        if stepName.lower() in step.name.lower():
                            steps_data.append({'id': step.id, 'name': step.name, 'intent_name': intent[0].name})
                    else:
                        steps_data.append({'id': step.id, 'name': step.name, 'intent_name': intent[0].name})
                data.append({'id': story.id, 'name': story.name, 'steps': steps_data})
            page = self.paginate_queryset(data)
            serializers = StoryCustomSerializer(page, many=True)
            # if page is not None:
            return self.get_paginated_response(serializers.data)
            # return Response(serializers.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)


class StoryDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Story.objects.all()
    serializer_class = StorySerializer


class StepList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = StepSerializer
    queryset = Step.objects.all()


class StepDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class IntentExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = IntentExampleSerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="intent", description="Filter by intent", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        intent_id = request.query_params.get("intent")
        if intent_id is not None:
            intent_exps = self.queryset.filter(intent=intent_id)
            serializer = self.get_serializer(intent_exps, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class IntentExampleSearch(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = IntentExample.objects.all()
    pagination_class = StandardResultsSetPagination
    serializer_class = IntentExampleSerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(name="intentName", description="Filter by intent name", required=False, type=str),
                    OpenApiParameter(name="entityName", description="Filter by entity name", required=False, type=str),
                    OpenApiParameter(name="intentText", description="Filter by intent text", required=False, type=str)
                    ]
    )
    def get(self, request, *args, **kwargs):
        intent_name = request.query_params.get("intentName", '')
        entity_name = request.query_params.get('entityName', '')
        intent_text = request.query_params.get('intentText', '')
        bot = request.query_params.get("bot")
        data = []
        try:
            if bot is not None:
                intent_exp = self.queryset.filter(bot=bot)
                if intent_name:
                    intent_exp = intent_exp.filter(intent__name__icontains=intent_name)

                if entity_name:
                    intent_exp = intent_exp.filter(entitykeyword__entity__name__icontains=entity_name).distinct()

                if intent_text:
                    intent_exp = intent_exp.filter(text__icontains=intent_text)

                # Sử dụng select_related và prefetch_related để giảm số lượng query
                intent_exp = intent_exp.select_related('intent').prefetch_related('entitykeyword_set__entity')

                for item in intent_exp:
                    intent_name = item.intent.name if item.intent else ""
                    entity_keyword_ids = list(item.entitykeyword_set.values_list('id', flat=True))

                    if len(entity_keyword_ids) > 1:
                        entity_keyword_ids = [entity_keyword_ids[0]]

                    entity_names = ""
                    if entity_keyword_ids:
                        entity_keyword_objs = EntityKeyWord.objects.filter(id__in=entity_keyword_ids).select_related('entity')
                        entity_names = [ek.entity.name for ek in entity_keyword_objs if ek.entity]
                        if entity_names:
                            entity_names = entity_names[0]

                    data.append({
                        'id': item.id,
                        'intent_name': intent_name,
                        'text': item.text,
                        'entity_name': entity_names,
                    })
                serializer = IntentExampleCustomSerializer(data, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="exps", description="List of IDs to delete", required=True, type=str)
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
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = IntentExampleSerializer
    queryset = IntentExample.objects.all()


class TextCardList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = TextCardSerializer
    queryset = TextCard.objects.all()


class TextCardDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = TextCardSerializer
    queryset = TextCard.objects.all()


class ImageCardList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ImageCardSerializer
    queryset = ImageCard.objects.all()


class ImageCardDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ImageCardSerializer
    queryset = ImageCard.objects.all()


class CustomActionList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = CustomActionSerializer
    queryset = CustomAction.objects.all()


class CustomActionDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = CustomActionSerializer
    queryset = CustomAction.objects.all()


class JsonApiList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = JsonApiSerializer
    queryset = JsonApi.objects.all()


class JsonApiDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = JsonApiSerializer
    queryset = JsonApi.objects.all()


# class EventsList(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#
#     serializer_class = EventsSerializer
#     queryset = Events.objects.all().filter(type_name="user")
#
#     @extend_schema(parameters=[OpenApiParameter(name="account", description="Filter by account", required=True, type=str)])
#     def get(self, request, *args, **kwargs):
#         events = self.queryset
#         account = request.query_params.get("account")
#         if account is not None:
#             events = events.filter(sender_id=UUID(account))
#             page = self.paginate_queryset(events)
#             if page is not None:
#                 serializer = self.get_serializer(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#
#             serializer = self.get_serializer(events, many=True)
#             return Response(serializer.data)
#
#         return Response(status=status.HTTP_403_FORBIDDEN)


class EventsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    serializer_class = EventsSerializer
    queryset = Events.objects.all().filter(type_name="user")

    @extend_schema(parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str)])
    def get(self, request, *args, **kwargs):
        events = self.queryset
        bot = request.query_params.get("bot")
        if bot is not None:
            events = events.filter(data__metadata__assistant_id=bot)
            page = self.paginate_queryset(events)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_403_FORBIDDEN)


class EventsList2(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    serializer_class = EventsSerializer
    queryset = Events.objects.all().filter(type_name="user")

# class EventsDetail(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#
#     serializer_class = EventsSerializer
#     queryset = Events.objects.all()
