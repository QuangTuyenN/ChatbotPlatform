# IMPORT BUILT-IN
import json
import os
import requests
import yaml
import unidecode

# IMPORT FRAMEWORK / THIRD-PARTY
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, permissions, generics
from rest_framework.response import Response

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import BotSerializer
from bot.models import Bot, Slot, CustomAction
from bot.serializers import BotSerializer, BotCustomSerializer
from bot.models import Bot
from bot.utils import _get_summary_data
from bot.utils import create_bot_kube
from bot.utils import delete_bot_kube

from django.db import connection, reset_queries
import time
import functools
from django.db.models import Prefetch

from kubernetes import client, config
from kubernetes.stream import stream

HOST_URL_MEDIA = os.environ.get("HOST_URL_MEDIA", "https://minioupload.prod.dev/chatbotplatform/")
HOST_INGRESS_BOT = os.environ.get("HOST_INGRESS_BOT", "http://cbpapi.prod.dev/")


def exec_command_in_pod(pod_name, namespace='chat', container_name=None, command='ls'):
    config.load_incluster_config()  # Tải cấu hình Kubernetes

    v1 = client.CoreV1Api()

    # Tạo đối tượng Exec
    exec_command = [
        '/bin/sh',
        '-c',
        command
    ]

    # Thực thi lệnh
    resp = stream(
        v1.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        container=container_name,
        command=exec_command,
        stderr=True, stdin=False,
        stdout=True, tty=False
    )
    return resp


def cleanup_models(model_clear, pod_name, namespace='chat'):
    # Lệnh để giữ lại model mới nhất và xóa các model cũ
    commands = f"""
        # Xóa các file model cũ ngoại trừ model_clear
        
        find models -type f ! -name {model_clear} -exec rm -f {{}} \;
        """
    output = exec_command_in_pod(pod_name, namespace=namespace, command=commands)
    return output


def replace_substring(original_string, replacements):
    for start, end, replacement in sorted(replacements, key=lambda x: x[0], reverse=True):
        original_string = original_string[:start] + replacement + original_string[end:]
    return original_string


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


def normalize_vietnamese(text):
    # Loại bỏ dấu tiếng Việt
    text = unidecode.unidecode(text)
    # Chuyển thành chữ thường
    text = text.lower()
    return text


class BotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related("chitchat_set",
                                            "chitchatintentexample_set",
                                            "chitchatutterexample_set",
                                            "intent_set",
                                            "intentexample_set",
                                            "entity_set",
                                            "story_set")

    @extend_schema(
        parameters=[OpenApiParameter(name="account", description="Filter by account", required=True, type=str),
                    OpenApiParameter(name="bot_name", description="Filter by bot name", required=False, type=str)])
    def get(self, request, *args, **kwargs):
        bots = self.queryset
        account = request.query_params.get("account")
        bot_name = request.query_params.get("bot_name")
        if account is not None and (bot_name is None or bot_name == ''):
            bots = bots.filter(account=account)

            bots_list = []
            try:
                for bot in bots:
                    summary = _get_summary_data(bot)
                    bot = BotSerializer(bot).data
                    bot["summary"] = summary
                    bots_list.append(bot)

                page = self.paginate_queryset(bots_list)
                serializer = BotCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            except Exception as bug:
                page = self.paginate_queryset(bots_list)
                serializer = BotCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        elif account is not None and bot_name is not None:
            bots = bots.filter(account=account)

            bots_list = []
            try:
                bot_name_lower = normalize_vietnamese(bot_name)
                print("bot name lower: ", bot_name_lower)
                if bot_name_lower != bot_name:
                    bots = bots.filter(name__icontains=bot_name)
                    for bot in bots:
                        # if bot_name in bot.name:
                        summary = _get_summary_data(bot)
                        bot = BotSerializer(bot).data
                        bot["summary"] = summary
                        bots_list.append(bot)
                else:
                    for bot in bots:
                        if bot_name_lower in normalize_vietnamese(bot.name):
                            summary = _get_summary_data(bot)
                            bot = BotSerializer(bot).data
                            bot["summary"] = summary
                            bots_list.append(bot)

                page = self.paginate_queryset(bots_list)
                serializer = BotCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            except Exception as bug:
                page = self.paginate_queryset(bots_list)
                serializer = BotCustomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        bots = self.queryset.filter(account=request.data['account'])
        if len(request.data['name']) > 200:
            return Response("Độ dài của tên bot không được quá 200 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        for bot in bots:
            if bot.name == request.data['name']:
                return Response("Tên bot đã được tạo ở tài khoản này, vui lòng đổi tên khác.",
                                status=status.HTTP_403_FORBIDDEN)
        if len(request.data['description']) > 500:
            return Response("Độ dài của mô tả không được quá 500 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
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
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BotSerializer

    queryset = Bot.objects.prefetch_related("chitchat_set",
                                            "chitchatintentexample_set",
                                            "chitchatutterexample_set",
                                            "intent_set",
                                            "intentexample_set",
                                            "entity_set",
                                            "story_set")

    def get(self, request, *args, **kwargs):
        bot = self.get_object()
        summary = _get_summary_data(bot)
        bot = self.get_serializer(bot).data
        bot["summary"] = summary
        return Response(bot, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        bot = self.get_object()
        bots = self.queryset.filter(account=request.data['account'])
        if len(request.data['default_answer_low_conf']) > 200:
            return Response("Độ dài của câu trả lời mặc định không được quá 200 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        new_name = request.data['name']
        if len(new_name) > 200:
            return Response("Độ dài của tên bot không được quá 200 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        bot_name_filters = bots.filter(name=new_name)
        count = bot_name_filters.count()
        if count > 1:
            return Response('Tên bot đã được sử dụng, vui lòng đổi tên khác',
                            status=status.HTTP_400_BAD_REQUEST)
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


class BotHtml(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BotSerializer
    queryset = Bot.objects.all()

    def get(self, request, *args, **kwargs):
        bot = self.get_object()
        bot_id_str = str(bot.id)
        link_bot = HOST_INGRESS_BOT + f"webchat/{bot_id_str}"
        html_code = [f"""<div id="rasa-chat-widget" data-websocket-url="{link_bot}"></div>""",
                     """<script src="https://unpkg.com/@rasahq/rasa-chat" type="application/javascript"></script>"""]
        print("html code: ", html_code)
        return Response(html_code, status=status.HTTP_200_OK)


class BotTrain(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related("chitchat_set").prefetch_related("chitchat_set__chitchatintentexample_set",
                                                                             "chitchat_set__chitchatutterexample_set") \
        .prefetch_related("story_set").prefetch_related("story_set__step_set") \
        .prefetch_related("story_set__step_set__textcard_set",
                          "story_set__step_set__imagecard_set",
                          "story_set__step_set__actioncard_set",
                          "story_set__step_set__jsoncard_set") \
        .prefetch_related("entity_set").prefetch_related("entity_set__entitykeyword_set") \
        .prefetch_related("intent_set").prefetch_related("intent_set__intentexample_set") \
        .prefetch_related("intent_set__intentexample_set__entitykeyword_set") \
        .prefetch_related(Prefetch('slot_set', queryset=Slot.objects.select_related('entity')))

    duckling_url = os.environ.get("DUCKLING_URL", "http://duckling-cbp-kube.chat.svc.cluster.local:8000")
    action_query = CustomAction.objects.all()

    @query_debugger
    def get(self, request, *args, **kwargs):
        bot = self.get_object()
        bot_id_str = str(bot.id)
        chitchats = bot.chitchat_set.all()
        intent_conf = bot.intent_confidence
        entities = bot.entity_set.all()
        intents = bot.intent_set.all()
        stories = bot.story_set.all()
        slots = bot.slot_set.all()
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
                         }
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
                     "entities": [],
                     "slots": {},
                     "actions": [
                     ],
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

        for custom_action in self.action_query:
            data_send['actions'].append(custom_action.action_save_name)
        print("--------------data_actions: ", data_send['actions'])

        for chit in chitchats:
            data_send["responses"][f"utter_chitchat/{chit.name}"] = []
            for exp in chit.chitchatutterexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    data_send["responses"][f"utter_chitchat/{chit.name}"].append(
                        {"text": str(exp.text)})
            data_send["nlu"].append(
                {"intent": f"chitchat/{chit.name}", "examples": ""})
            for exp in chit.chitchatintentexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    for i in data_send["nlu"]:
                        if i["intent"] == f"chitchat/{chit.name}":
                            i["examples"] = i["examples"] + \
                                            "- " + str(exp.text) + "\n"

        for intent in intents:
            # print("intent step: ", intent.step.num_order)
            data_send['intents'].append(intent.name)
            data_send['nlu'].append(
                {'intent': f'{intent.name}', 'examples': ''})
            for int_ex in intent.intentexample_set.all():
                for i in data_send['nlu']:
                    if i['intent'] == intent.name:
                        entity_keywords = int_ex.entitykeyword_set.all()
                        text_exp = int_ex.text
                        if entity_keywords:
                            list_tuple = []
                            for entity_keyword in entity_keywords:
                                rep = str(
                                    f'[{entity_keyword.text}]{{"entity": "{entity_keyword.entity.name}"}} ')
                                # text_exp = text_exp.replace(
                                #     entity_keyword.text, rep)
                                list_tuple.append((entity_keyword.start_position, entity_keyword.end_position + 1, rep))
                            text_exp = replace_substring(text_exp, list_tuple)
                        i['examples'] = i['examples'] + \
                                        '- ' + str(text_exp) + '\n'
            for dict_intent_exps in data_send['nlu']:
                if dict_intent_exps['examples'] == '':
                    data_send['nlu'].remove(dict_intent_exps)
        for entity in entities:
            data_send['entities'].append(entity.name)

        for slot in slots:
            data_send['slots'][slot.name] = {"type": slot.validate_type}
            if slot.entity:
                data_send['slots'][slot.name]["mappings"] = [
                    {"type": "from_entity", "entity": slot.entity.name}]

        for story in stories:
            # data_send["stories"].append({"story": f"{story.name}", "steps": []})
            steps = story.step_set.all().order_by('num_order')
            list_steps = []
            for step in steps:
                try:
                    list_step = []
                    intent_name = step.intent.name
                    text_cards_step = step.textcard_set.all()
                    image_cards_step = step.imagecard_set.all()
                    action_cards_step = step.actioncard_set.all()
                    json_cards_step = step.jsoncard_set.all()
                    for text_card_step in text_cards_step:
                        data_send['responses'][f'{text_card_step.name}'] = [
                            {"text": text_card_step.text}]
                        if text_card_step:
                            list_step.append(
                                {"name": text_card_step.name, "num_order": text_card_step.num_order})
                    for image_card_step in image_cards_step:
                        data_send['responses'][f'{image_card_step.name}'] = \
                            [{"text": image_card_step.text,
                              "image": f'{HOST_URL_MEDIA}/media/{str(image_card_step.image)}'}]
                        if image_card_step:
                            list_step.append(
                                {"name": image_card_step.name, "num_order": image_card_step.num_order})
                    for action_card_step in action_cards_step:
                        if action_card_step:
                            list_step.append(
                                {"name": action_card_step.action.action_save_name, "num_order": action_card_step.num_order})
                    for json_card_step in json_cards_step:
                        if json_card_step:
                            list_step.append(
                                {"name": json_card_step.name, "num_order": json_card_step.num_order})
                    list_step = sorted(list_step, key=lambda x: x['num_order'])
                    list_steps.append({"intent": intent_name})
                    for action in list_step:
                        list_steps.append({"action": action["name"]})
                except Exception as bug:
                    print("step don't have intent")
            if len(list_steps) > 1:
                data_send["stories"].append({"story": story.name, "steps": list_steps})
            # if len(list_steps) != 0:
            #     data_send["stories"].append(
            #         {"story": story.name, "steps": list_steps})

        print("---------------------------------")
        print(data_send)
        print("actions: ", data_send['actions'])
        print("---------------------------------")

        try:
            # train
            yaml_content = yaml.dump(data_send, default_flow_style=False)
            api_train = os.environ.get(
                "API_TRAIN_BOT", f"http://bot-{bot_id_str}:5005/model/train")
            headers = {"Content-Type": "application/yaml"}
            response = requests.post(
                api_train, data=yaml_content, headers=headers)

            # replace old with new
            model_name = response.headers["filename"]
            path_model_inside_pod = os.environ.get(
                "BOT_MODEL_PATH", "/app/models/")
            json_put_model = {"model_file": path_model_inside_pod + model_name}
            api_replace_old_model = os.environ.get(
                "API_REPLACE_BOT", f"http://bot-{bot_id_str}:5005/model")
            headers_put = {"Content-Type": "application/json"}
            response2 = requests.put(api_replace_old_model, data=json.dumps(
                json_put_model), headers=headers_put)

            print("Response CODE for PUT Model: ", response2.status_code)

            # Xóa model cũ
            pod_name = f"bot-{bot_id_str}"
            config.load_incluster_config()  # Tải cấu hình Kubernetes
            v1 = client.CoreV1Api()
            pods = v1.list_namespaced_pod(namespace='chat')
            pod_name_official = ''
            for pod in pods.items:
                if pod_name in pod.metadata.name:
                    pod_name_official = pod.metadata.name
            output = cleanup_models(model_name, pod_name_official, namespace='chat')
            print(output)

            return Response({"status": "Huấn luyện thành công!"}, status=status.HTTP_200_OK)

        except Exception as bug:
            print("Error when train model", bug)
            if 'filename' in bug:
                return Response({"status": f"Có lỗi xảy ra trong quá trình huấn luyện: Không đủ bộ nhớ để lưu bot"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": f"Có lỗi xảy ra trong quá trình huấn luyện: {bug}"},
                                status=status.HTTP_400_BAD_REQUEST)

        # return Response(data_send, status=status.HTTP_200_OK)
