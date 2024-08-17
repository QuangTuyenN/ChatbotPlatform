# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import transaction

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import StepSerializer
from bot.serializers import StepCustomSerializer
from bot.serializers import IntentSerializer
from bot.serializers import IntentExampleSerializer
from bot.serializers import SelectSlotCustomSerializer
from bot.models import Step
from bot.models import Intent
from bot.models import TextCard
from bot.models import ImageCard
from bot.models import FormCard
from bot.models import ActionCard
from bot.models import JsonCard
from bot.models import FormSlot
from bot.models import IntentExample
from bot.models import Slot

# IMPORT PYTHON LIB
from bot.utils import *


class StepList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StepSerializer
    queryset = Step.objects.all()
    http_method_names = ["get", "post"]

    def post(self, request, *args, **kwargs):

        try:
            step_name = request.data.get('name')
            if step_name is not None:
                if len(step_name) > 200:
                    return Response('Tên bước không được vượt quá 200 ký tự',
                                    status=status.HTTP_400_BAD_REQUEST)
            num_order = request.data.get('num_order')
            story = request.data.get('story')
            step = self.queryset.filter(story_id=story)

            if str(request.data.get('name')) == "":
                return Response('Tên bước không được trống', status=status.HTTP_400_BAD_REQUEST)
            for st in step:
                if str(st.name) == str(step_name):
                    return Response('Tên bước đã tồn tại ở kịch bản này, vui lòng đổi tên khác',
                                    status=status.HTTP_400_BAD_REQUEST)
                if int(st.num_order) == int(num_order):
                    return Response('Thứ tự bước này đã tồn tại, vui lòng tạo với thứ tự khác',
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer = StepSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)


class StepDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Step.objects.all()
    serializer_class = StepSerializer

    def get(self, request, *args, **kwargs):
        step_id = kwargs.get("pk")
        try:
            step = self.queryset.get(id=step_id)
            if step_id is not None and is_valid_uuid(str(step_id)) is True:
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
                    print(f'{HOST_URL_MEDIA}{imagecard.image}')
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

                step_data = []
                step_data.append({'id': step.id, 'name': step.name, 'num_order': step.num_order, 'story_id': step.story.id, 'intent_id': intent_id,
                                  'intent_name': intent_name, 'intent_description': intent_description, 'intent_example': intent_example, 'action': response_data})
                return Response(step_data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        step_id = kwargs.get("pk")
        if step_id is not None and is_valid_uuid(str(step_id)):
            try:
                step = self.queryset.get(id=step_id)
                story_id = step.story_id

                # Delete the step
                step.delete()

                # Retrieve remaining steps in the same story, ordered by num_order
                steps = self.queryset.filter(
                    story_id=story_id).order_by('num_order')

                # Update num_order for the remaining steps
                for idx, step in enumerate(steps, start=1):
                    step.num_order = idx
                    step.save()

                return Response(status=status.HTTP_204_NO_CONTENT)

            except self.queryset.model.DoesNotExist:
                return Response({"detail": "Step not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Invalid step ID."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        step_id = kwargs.get("pk")
        # Ensure position is an integer
        if step_id is not None and is_valid_uuid(str(step_id)):
            try:
                name = request.data.get('name')
                if name is not None:
                    if len(name) > 200:
                        return Response('Tên bước không được vượt quá 200 ký tự',
                                        status=status.HTTP_400_BAD_REQUEST)
                num_order = request.data.get('num_order')
                step = self.queryset.get(id=step_id)
                story_id = step.story_id
                print("story_id: ", step.story_id)
                print("story_id2: ", step.story.id)
                num_step = len(self.queryset.filter(story_id=story_id))
                step.name = request.data.get('name', step.name)
                steps = self.queryset.all()
                if str(request.data.get('name')) == "":
                    return Response('Tên bước không được trống', status=status.HTTP_400_BAD_REQUEST)
                for st in steps:
                    if str(st.name) == str(request.data.get('name')) and str(st.id) != str(step_id):
                        return Response('Tên bước đã tồn tại ở kịch bản này, vui lòng đổi tên khác', status=status.HTTP_400_BAD_REQUEST)
                step.story_id = request.data.get('story_id', step.story_id)
                step.created_at = request.data.get(
                    'created_at', step.created_at)
                step.updated_at = request.data.get(
                    'updated_at', step.updated_at)
                step.save()
                if num_order is not None:
                    print("go here")
                    if int(num_order) <= 0 or int(num_order) >= num_step+1:
                        return Response({"detail": "Invalid position."}, status=status.HTTP_403_FORBIDDEN)
                    steps = list(self.queryset.filter(
                        story_id=story_id).order_by('num_order'))
                    print("Ban đầu")
                    for st in steps:
                        print(st.id)
                    step = self.queryset.get(id=step_id)
                    removed_element = steps.pop(step.num_order-1)
                    print("Sau khi xóa")
                    for st in steps:
                        print(st.id)
                    print("step đã remove", removed_element)
                    steps.insert(int(num_order)-1, step)
                    i = 1
                    for st in steps:
                        print(st.id)
                        st.num_order = i
                        i += 1
                        st.save()
                instance = self.get_object()

                # Update the instance with the new data
                serializer = self.get_serializer(
                    instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except self.queryset.model.DoesNotExist:
                return Response({"detail": "Step not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Invalid step ID."}, status=status.HTTP_400_BAD_REQUEST)


class CustomStepIntentList(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @extend_schema(
        parameters=[OpenApiParameter(
            name="bot", description="Filter by bot", required=True, type=str)]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        if bot is not None and is_valid_uuid(str(bot)) is True:
            intents = Intent.objects.filter(bot_id=bot)
            unused_intents = intents.filter(
                bot=bot, step_id__isnull=True)
            serializer = IntentSerializer(unused_intents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CustomStepIntentExampleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @extend_schema(
        parameters=[OpenApiParameter(
            name="intent", description="Filter by intent", required=True, type=str)]
    )
    def get(self, request, *args, **kwargs):
        intent = request.query_params.get("intent")
        if intent is not None and is_valid_uuid(str(intent)) is True:
            intent_examples = IntentExample.objects.filter(
                intent_id=intent)[:2]
            serializer = IntentExampleSerializer(intent_examples, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CustomStepSlotList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @extend_schema(
        parameters=[OpenApiParameter(
            name="bot", description="Filter by bot", required=True, type=str),
            OpenApiParameter(
            name="form", description="Filter by form", required=True, type=str)]
    )
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        if bot is not None and is_valid_uuid(str(bot)) is True:
            form = request.query_params.get("form")
            slot = Slot.objects.filter(bot=bot)
            form_slot = FormSlot.objects.filter(form=form)
            slot_list = [form_slot.slot.id for form_slot in form_slot]
            data = []
            for sl in slot:
                is_used = False
                if sl.id in slot_list:
                    is_used = True
                data.append({'id': sl.id, 'name': sl.name, 'is_used': is_used})
            serializer = SelectSlotCustomSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)
