# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, permissions, generics
from rest_framework.response import Response
import uuid
# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import StorySerializer
from bot.serializers import StoryCustomSerializer
from bot.serializers import StoryListSerializer
from bot.models import Story, Intent, Step, IntentExample, TextCard, ImageCard, FormCard, ActionCard, JsonCard, FormSlot
from bot.utils import *


class StoryList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Story.objects.prefetch_related('step_set')
    http_method_names = ["get", "post"]
    serializer_class = StorySerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="bot", description="Filter by bot", required=True, type=str),
                    OpenApiParameter(
                        name="story_name", description="Filter by story name", required=False, type=str),
                    OpenApiParameter(
                        name="step_name", description="Filter by step name", required=False, type=str),
                    OpenApiParameter(
                        name="step_id", description="Filter by step", required=False, type=str)
                    ]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        story_name = request.query_params.get("story_name", '')
        step_name = request.query_params.get('step_name', '')
        step_id = request.query_params.get('step_id', '')
        story_name_removed = normalize_vietnamese(story_name)
        step_name_removed = normalize_vietnamese(step_name)
        data = []
        step_data = []
        story_list = []
        if bot is not None and is_valid_uuid(str(bot)) is True:
            stories = self.queryset.filter(bot=bot).order_by('-created_at')
            if story_name:
                temp_stories = stories
                if story_name == story_name_removed:
                    stories = []
                    for story in temp_stories:
                        if story_name.lower() in normalize_vietnamese(story.name).lower():
                            stories.append(story)
                else:
                    stories = stories.filter(
                        name__icontains=str(story_name)).order_by('-created_at')

            for story in stories:
                steps_data = []
                steps = story.step_set.all().order_by('num_order')

                for step in steps:
                    intent = Intent.objects.filter(step=step.id)
                    if len(intent) == 0:
                        intent_name = ''
                    else:
                        intent_name = intent[0].name
                    if step_name:
                        if step_name == step_name_removed:
                            if step_name.lower() in normalize_vietnamese(step.name).lower():
                                steps_data.append(
                                    {'id': step.id, 'story': step.story.id, 'num_order': step.num_order, 'name': step.name, 'intent_name': intent_name})
                        else:
                            if step_name.lower() in step.name.lower():
                                steps_data.append(
                                    {'id': step.id, 'story': step.story.id, 'num_order': step.num_order, 'name': step.name, 'intent_name': intent_name})
                    else:
                        steps_data.append(
                            {'id': step.id, 'story': step.story.id, 'num_order': step.num_order, 'name': step.name, 'intent_name': intent_name})
                    if step_id is not None and is_valid_uuid(str(step_id)) is True:
                        if str(step.id) == str(step_id):
                            intent_main = Intent.objects.filter(
                                step_id=step_id)
                            intent_example = []
                            intent_id = ''
                            intent_name = ''
                            intent_description = ''
                            if len(intent_main) > 0:
                                intent_exps = IntentExample.objects.filter(
                                    intent_id=intent_main[0].id).order_by('-created_at')[:2]
                                for it in intent_exps:
                                    intent_example.append({
                                        "id": it.id,
                                        "bot": it.bot.id,
                                        "intent": it.intent.id,
                                        "text": it.text,
                                        "created_at": it.created_at,
                                        "updated_at": it.updated_at
                                    })
                                intent_name = intent_main[0].name
                                intent_id = intent_main[0].id
                                intent_description = intent_main[0].description

                            text_card = TextCard.objects.filter(
                                step_id=step_id)
                            text_card_data = []
                            for tc in text_card:
                                text_card_data.append({
                                    "id": tc.id,
                                    "type": "textcard",
                                    "step": tc.step.id,
                                    "name":  tc.name,
                                    "text": tc.text,
                                    "num_order": tc.num_order,
                                    "created_at": tc.created_at,
                                    "updated_at": tc.updated_at
                                })

                            image_card = ImageCard.objects.filter(
                                step_id=step_id)
                            imagecard_data = []
                            for imagecard in image_card:
                                if imagecard.image == "":
                                    image_url = ""
                                else:
                                    image_url = f'{HOST_URL_MEDIA}{imagecard.image}'
                                imagecard_data.append({
                                    "id": imagecard.id,
                                    "type": "imagecard",
                                    "name": imagecard.name,
                                    "image": image_url,
                                    "text": imagecard.text,
                                    "num_order": imagecard.num_order,
                                    "created_at": imagecard.created_at,
                                    "updated_at": imagecard.updated_at,
                                    "step": imagecard.step.id
                                })

                            form_card = FormCard.objects.filter(
                                step_id=step_id)
                            form_card_data = []
                            for fc in form_card:
                                form_slot = FormSlot.objects.filter(
                                    form_id=fc.id)
                                form_card_data.append({'id': fc.id, "type": "formcard", 'num_order': fc.num_order,
                                                       'step': fc.step, 'name': fc.name, 'form_slot': form_slot})

                            action = ActionCard.objects.filter(step_id=step_id)
                            action_data = []
                            for ac in action:
                                action_id = ''
                                if ac.action is not None:
                                    action_id = ac.action.id
                                action_data.append({
                                    "id": ac.id,
                                    "type": "actioncard",
                                    "step": ac.step.id,
                                    "action": action_id,
                                    "name": ac.name,
                                    "num_order": ac.num_order,
                                    "created_at": ac.created_at,
                                    "updated_at":  ac.updated_at

                                })

                            json_card = JsonCard.objects.filter(
                                step_id=step_id)
                            json_card_data = []
                            for jc in json_card:
                                json_card_data.append({
                                    "id": jc.id,
                                    "type": "jsoncard",
                                    "step": jc.step.id,
                                    "name": jc.name,
                                    "num_order": jc.num_order,
                                    "TYPES": jc.TYPES,
                                    "send_method": jc.send_method,
                                    "url": jc.url,
                                    "headers": jc.headers,
                                    "data": jc.data,
                                    "use_entity": jc.use_entity,
                                    "created_at": jc.created_at,
                                    "updated_at": jc.updated_at,
                                })

                            response_data = []
                            if len(text_card_data) > 0:
                                for tx in text_card_data:
                                    response_data.append(tx)
                            if len(imagecard_data) > 0:
                                for img in imagecard_data:
                                    response_data.append(img)
                            if len(action_data) > 0:
                                for ac in action_data:
                                    response_data.append(ac)
                            if len(form_card_data) > 0:
                                for fc in form_card_data:
                                    response_data.append(fc)
                            if len(json_card_data) > 0:
                                for jc in json_card_data:
                                    response_data.append(jc)
                            response_data = sorted(
                                response_data, key=lambda x: x['created_at'])
                            step_data.append({'id': step.id, 'name': step.name, 'num_order': step.num_order, 'story_id': step.story.id, 'intent_id': intent_id,
                                              'intent_name': intent_name, 'intent_description': intent_description, 'intent_example': intent_example, 'action': response_data})
                data.append({'id': story.id, 'bot': story.bot.id,
                            'name': story.name, 'steps': steps_data})
            story_list.append({'list_story': data, 'recent_step': step_data})
            return Response(story_list[0], status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):

        try:
            story_name = request.data.get('name')
            if story_name is not None:
                if len(story_name) > 200:
                    return Response('Tên kịch bản không được vượt quá 200 ký tự',
                                    status=status.HTTP_400_BAD_REQUEST)
            bot = request.data.get('bot')
            story = self.queryset.filter(bot=bot)
            if str(request.data.get('name')) == "":
                return Response('Tên kịch bản không được trống', status=status.HTTP_400_BAD_REQUEST)
            for st in story:
                if str(st.name) == str(story_name):
                    return Response('Tên kịch bản đã tồn tại ở bot này, vui lòng đổi tên khác', status=status.HTTP_400_BAD_REQUEST)
            serializer = StorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)


class StoryDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def get(self, request, *args, **kwargs):
        story_id = kwargs.get("pk")
        if story_id is not None and is_valid_uuid(str(story_id)) is True:
            story = self.queryset.get(id=story_id)
            steps = story.step_set.all()
            steps_data = []
            data = []
            for step in steps:
                intent = Intent.objects.filter(step=step.id)
                if len(intent) == 0:
                    intent_name = ''
                else:
                    intent_name = intent[0].name
                    steps_data.append(
                        {'id': step.id, 'story': step.story.id, 'num_order': step.num_order, 'name': step.name, 'intent_name': intent_name})
            data.append(
                {'id': story.id, 'bot': story.bot.id, 'name': story.name, 'steps': steps_data})
            serializers = StoryCustomSerializer(data, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        try:
            story_id = kwargs.get("pk")
            story_name = request.data.get('name')
            if story_name is not None:
                if len(story_name) > 200:
                    return Response('Tên kịch bản không được vượt quá 200 ký tự',
                                    status=status.HTTP_400_BAD_REQUEST)
            bot = request.data.get('bot')
            story = self.queryset.filter(bot=bot)
            if str(request.data.get('name')) == "":
                return Response('Tên kịch bản không được trống', status=status.HTTP_400_BAD_REQUEST)
            for st in story:
                if str(st.name) == str(story_name) and str(st.id) != str(story_id):
                    return Response('Tên kịch bản đã tồn tại ở bot này, vui lòng đổi tên khác', status=status.HTTP_400_BAD_REQUEST)
            serializer = StorySerializer(data=request.data)
           # Retrieve the existing instance
            instance = self.get_object()

            # Update the instance with the new data
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)
