import json
import os

import yaml
from kubernetes import config, dynamic, client
from kubernetes.client import api_client
from django.http import Http404
from uuid import UUID
import requests
from bot.serializers_shorter import *
from rest_framework import permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.pagination import StandardResultsSetPagination
from django.db import connection, reset_queries
import time
import functools
from rest_framework.exceptions import ParseError
from drf_spectacular.utils import extend_schema, OpenApiParameter


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
    int_exps = [exp.text for exp in chit.chitchatintentexample_set.all() if str(
        exp.chitchat) == str(chit.name)]
    utt_exps = [exp.text for exp in chit.chitchatutterexample_set.all() if str(
        exp.chitchat) == str(chit.name)]
    return {'id': chit.id, 'name': chit.name, 'int_exps': int_exps, 'utt_exps': utt_exps}


def _get_summary_data(bot):
    counts = {
        'chitchats': bot.chitchat_set.count(),
        'chitchat_intent_examples': bot.chitchatintentexample_set.count(),
        'chitchat_utter_examples': bot.chitchatutterexample_set.count(),
        'intents': bot.intent_set.count(),
        'intent_examples': bot.intentexample_set.count(),
        'entities': bot.entity_set.count(),
        'stories': bot.story_set.count()
    }

    return counts


# def create_bot_kube(bot_id, namespace="chat"):
#     client = dynamic.DynamicClient(api_client.ApiClient(configuration=config.load_kube_config()))
#
#     bot_deploy_yaml = yaml.safe_load(f'''
#     apiVersion: apps/v1
#     kind: Deployment
#     metadata:
#       labels:
#         app: {bot_id}
#       name: {bot_id}
#     spec:
#       replicas: 1
#       selector:
#         matchLabels:
#           app: {bot_id}
#       template:
#         metadata:
#           labels:
#             app: {bot_id}
#         spec:
#           containers:
#           - name: {bot_id}
#             image: xuandaikk113/rasa-kube-blank:1.0.0
#             ports:
#             - containerPort: 5005
#             command: ["rasa", "run", "--enable-api", "--cors", "*"]
#             resources:
#               limits:
#                 cpu: "0.7"
#                 memory: 1.5Gi
#               requests:
#                 cpu: "0.4"
#                 memory: 0.8Gi
#     ''')
#
#     bot_svc_yaml = yaml.safe_load(f'''
#     apiVersion: v1
#     kind: Service
#     metadata:
#       name: {bot_id}
#     spec:
#       ports:
#       - port: 5005
#         targetPort: 5005
#       selector:
#         app: {bot_id}
#     ''')
#
#     bot_ingress_yaml = yaml.safe_load(f'''
#     apiVersion: networking.k8s.io/v1
#     kind: Ingress
#     metadata:
#       name: {bot_id}
#       annotations:
#         nginx.ingress.kubernetes.io/rewrite-target:  /$2
#
#     spec:
#       ingressClassName: nginx
#       rules:
#       - http:
#           paths:
#           - path: /webchat/{bot_id}(/|$)(.*)
#             pathType: Prefix
#             backend:
#               service:
#                 name: {bot_id}
#                 port:
#                   number: 5005
#     ''')
#
#     api_deploy = client.resources.get(api_version="apps/v1", kind="Deployment")
#     api_service = client.resources.get(api_version="v1", kind="Service")
#     api_ingress = client.resources.get(api_version="networking.k8s.io/v1", kind="Ingress")
#
#     deployment = api_deploy.create(body=bot_deploy_yaml, namespace=namespace)
#     print("Deployment created. status='%s'" % deployment.metadata.name)
#
#     service = api_service.create(body=bot_svc_yaml, namespace=namespace)
#     print("Service created. status='%s'" % service.metadata.name)
#
#     ingress_deploy = api_ingress.create(body=bot_ingress_yaml, namespace=namespace)
#     print("Ingress created. status='%s'" % ingress_deploy.metadata.name)

def create_bot_kube(bot_id):
    config.load_incluster_config()
    api_deploy = client.AppsV1Api()
    api_service = client.CoreV1Api()
    api_ingress = client.NetworkingV1Api()
    rasa_port = int(os.environ.get("RASA_PORT", 5005))
    namespace = os.environ.get("BOT_NAME_SPACE", "chat")
    rasa_img = os.environ.get("RASA_IMAGE", "xuandaikk113/rasa-cbp:1.0.0")

    rasa_deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(
            name=f"bot-{bot_id}", labels={"app": f"bot-{bot_id}"}
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={
                    "app": f"bot-{bot_id}"
                }
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        "app": f"bot-{bot_id}"
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=f"bot-{bot_id}",
                            image=rasa_img,
                            ports=[
                                client.V1ContainerPort(
                                    container_port=rasa_port
                                )
                            ],
                            command=["rasa", "run",
                                     "--enable-api", "--cors", "*"]
                        )
                    ]
                )
            )
        )
    )

    deploy_result = api_deploy.create_namespaced_deployment(
        namespace=namespace, body=rasa_deployment)
    print("\nDeployment created. status='%s'\n" % deploy_result.metadata.name)

    rasa_service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=f"bot-{bot_id}"
        ),
        spec=client.V1ServiceSpec(
            selector={"app": f"bot-{bot_id}"},
            ports=[client.V1ServicePort(
                port=rasa_port,
                target_port=rasa_port
            )]
        )
    )

    svc_result = api_service.create_namespaced_service(
        namespace=namespace, body=rasa_service)
    print("\nService created. status='%s'\n" % svc_result.metadata.name)

    bot_ingress = client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=f"bot-{bot_id}",
                                     annotations={
                                         "nginx.ingress.kubernetes.io/rewrite-target": "/$2"
                                     }),
        spec=client.V1IngressSpec(
            rules=[client.V1IngressRule(
                http=client.V1HTTPIngressRuleValue(
                    paths=[client.V1HTTPIngressPath(
                        path=f"/webchat/{bot_id}(/|$)(.*)",
                        path_type="Prefix",
                        backend=client.V1IngressBackend(
                            service=client.V1IngressServiceBackend(
                                port=client.V1ServiceBackendPort(
                                    number=rasa_port,
                                ),
                                name=f"bot-{bot_id}")
                        )
                    )]
                )
            )
            ],
            ingress_class_name="nginx"
        )
    )

    ingress_result = api_ingress.create_namespaced_ingress(
        namespace=namespace, body=bot_ingress)
    print("\nIngress created. status='%s'\n" % ingress_result.metadata.name)


# def delete_bot_kube(bot_id):
#     client = dynamic.DynamicClient(api_client.ApiClient(configuration=config.load_kube_config()))
#     namespace = "chat"
#
#     api_deploy = client.resources.get(api_version="apps/v1", kind="Deployment")
#     api_service = client.resources.get(api_version="v1", kind="Service")
#     api_ingress = client.resources.get(api_version="networking.k8s.io/v1", kind="Ingress")
#
#     deployment_deleted = api_deploy.delete(name=bot_id, body={}, namespace=namespace)
#     print("Deployments deleted.")
#     service_deleted = api_service.delete(name=bot_id, body={}, namespace=namespace)
#     print("Services deleted.")
#     ingress_deleted = api_ingress.delete(name=bot_id, body={}, namespace=namespace)
#     print("Ingresses deleted.")

def delete_bot_kube(bot_id):
    config.load_incluster_config()
    namespace = os.environ.get("BOT_NAME_SPACE", "chat")

    api_deploy = client.AppsV1Api()
    api_service = client.CoreV1Api()
    api_ingress = client.NetworkingV1Api()

    api_deploy.delete_namespaced_deployment(
        name=f"bot-{bot_id}", namespace=namespace)
    api_service.delete_namespaced_service(
        name=f"bot-{bot_id}", namespace=namespace)
    api_ingress.delete_namespaced_ingress(
        name=f"bot-{bot_id}", namespace=namespace)
    print(f"\nAll resources of bot with {bot_id} were deleted!\n")


class BotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related('chitchat_set',
                                            'chitchatintentexample_set',
                                            'chitchatutterexample_set',
                                            'intent_set',
                                            'intentexample_set',
                                            'entity_set',
                                            'story_set')

    @extend_schema(parameters=[OpenApiParameter(name='account', description='Filter by account', required=True, type=str)])
    def get(self, request, *args, **kwargs):
        bots = self.queryset
        account = request.query_params.get('account')
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
        try:
            bot = serializer.save()
            # create_bot_kube(bot_id=str(bot.id))
            return bot
        except Exception as bug:
            print("Error in perfrom create: ", bug)
            raise Http404


class BotDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer

    queryset = Bot.objects.prefetch_related('chitchat_set',
                                            'chitchatintentexample_set',
                                            'chitchatutterexample_set',
                                            'intent_set',
                                            'intentexample_set',
                                            'entity_set',
                                            'story_set')

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
            return self.destroy(request, *args, **kwargs)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BotTrain(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = BotSerializer
    queryset = Bot.objects.prefetch_related('chitchat_set').prefetch_related('chitchat_set__chitchatintentexample_set',
                                                                             'chitchat_set__chitchatutterexample_set')

    def get(self, request, *args, **kwargs):
        bot = self.get_object()
        bot_id_str = str(bot.id)
        chitchats = bot.chitchat_set.all()
        intent_conf = bot.intent_confidence
        data_send = {'assistant_id': bot_id_str,
                     'language': 'vi',
                     'pipeline': [
                         {'name': 'WhitespaceTokenizer'},
                         {'name': 'RegexFeaturizer'},
                         {'name': 'LexicalSyntacticFeaturizer'},
                         {'name': 'CountVectorsFeaturizer'},
                         {
                             "name": "CountVectorsFeaturizer",
                             "analyzer": "char_wb",
                             "min_ngram": 1,
                             "max_ngram": 4
                         },
                         {
                             "name": "DIETClassifier",
                             "epochs": 100,
                             "constrain_similarities": 'true'
                         },
                         {'name': 'EntitySynonymMapper'},
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
                     'policies': [
                         {'name': 'MemoizationPolicy'},
                         {'name': 'RulePolicy'},
                         {
                             "name": "UnexpecTEDIntentPolicy",
                             "max_history": 5,
                             "epochs": 100
                         },
                         {
                             "name": "TEDPolicy",
                             "max_history": 5,
                             "epochs": 100,
                             "constrain_similarities": 'true'
                         }
                     ],
                     'intents': ['chitchat'],
                     'responses': {
                         'utter_default': [{'text': str(bot.default_answer_low_conf)}]
                     },
                     "session_config": {
                         "session_expiration_time": 60,
                         "carry_over_slots_to_new_session": True
                     },
                     'nlu': [],
                     'rules': [
                         {
                             'rule': 'chitchat',
                             'steps': [
                                 {'intent': 'chitchat'},
                                 {'action': 'utter_chitchat'}
                             ]
                         }
                     ],
                     'stories': [
                         {
                             'story': 'chitchat',
                             'steps': [
                                 {'intent': 'chitchat'},
                                 {'action': 'utter_chitchat'}
                             ]
                         }
                     ]
                     }

        for chit in chitchats:
            data_send['responses'][f'utter_chitchat/{chit.name}'] = []
            for exp in chit.chitchatutterexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    data_send['responses'][f'utter_chitchat/{chit.name}'].append(
                        {'text': str(exp.text)})
            data_send['nlu'].append(
                {'intent': f'chitchat/{chit.name}', 'examples': ''})
            for exp in chit.chitchatintentexample_set.all():
                if str(exp.chitchat) == str(chit.name):
                    for i in data_send['nlu']:
                        if i['intent'] == f'chitchat/{chit.name}':
                            i['examples'] = i['examples'] + \
                                '- ' + str(exp.text) + '\n'

        try:
            # train
            yaml_content = yaml.dump(data_send, default_flow_style=False)
            api_train = os.environ.get(
                "API_TRAIN_BOT", f"http://bot-{bot_id_str}:5005/model/train")
            headers = {'Content-Type': 'application/yaml'}
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
            return Response({"status": "Huấn luyện thành công!"}, status=status.HTTP_200_OK)

        except Exception as bug:
            print("Error when train model", bug)
            return Response({"status": f"Có lỗi xảy ra trong quá trình huấn luyện: {bug}"}, status=status.HTTP_400_BAD_REQUEST)


class ChitChatList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related(
        'chitchatintentexample_set', 'chitchatutterexample_set')

    @extend_schema(parameters=[OpenApiParameter(name='bot', description='Filter by bot', required=True, type=str)])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get('bot')
        if bot is not None:
            chitchats = self.queryset.filter(bot=bot)
            chits_list = [_get_chitchat_data(chit) for chit in chitchats]
            return Response(chits_list, status=status.HTTP_200_OK)
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
    http_method_names = ['post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatSerializer
    queryset = ChitChat.objects.prefetch_related(
        'chitchatintentexample_set', 'chitchatutterexample_set')

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

    @extend_schema(parameters=[OpenApiParameter(name='chitchat', description='Filter by chitchat', required=True, type=str)])
    def get(self, request, *args, **kwargs):
        chit = request.query_params.get('chitchat')
        if chit is not None:
            exps = self.queryset.filter(chitchat=chit)
            exps = self.get_serializer(exps, many=True)
            return Response(exps.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ChitChatIntentExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatIntentExampleSerializer
    queryset = ChitChatIntentExample.objects.all()


class ChitChatUtterExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ChitChatUtterExampleSerializer
    queryset = ChitChatUtterExample.objects.all()

    @extend_schema(parameters=[OpenApiParameter(name='chitchat', description='Filter by chitchat', required=True, type=str)])
    def get(self, request, *args, **kwargs):
        chit = request.query_params.get('chitchat')
        if chit is not None:
            exps = self.queryset.filter(chitchat=chit)
            exps = self.get_serializer(exps, many=True)
            return Response(exps.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ChitChatUtterExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = ChitChatUtterExample.objects.all()
    serializer_class = ChitChatUtterExampleSerializer


class EventsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    serializer_class = EventsSerializer
    queryset = Events.objects.all().filter(type_name="user")

    @extend_schema(parameters=[OpenApiParameter(name='account', description='Filter by account', required=True, type=str)])
    def get(self, request, *args, **kwargs):
        events = self.queryset
        account = request.query_params.get('account')
        if account is not None:
            events = events.filter(sender_id=UUID(account))
            page = self.paginate_queryset(events)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(events, many=True)
            return Response(serializer.data)

# class EventsDetail(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#
#     serializer_class = EventsSerializer
#     queryset = Events.objects.all()
