# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import ImageCardSerializer
from bot.serializers import TextCardSerializer
from bot.serializers import ActionCardSerializer
from bot.models import ImageCard
from bot.models import TextCard
from bot.models import ActionCard
from bot.models import JsonCard
from bot.models import FormCard
from bot.models import FormSlot
from bot.utils import *


class ActionCardList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ActionCard.objects.all()
    serializer_class = ActionCardSerializer

    def get(self, request, *args, **kwargs):
        action_list = self.queryset.order_by('-created_at')
        page = self.paginate_queryset(action_list)
        serializers = ActionCardSerializer(page, many=True)
        return self.get_paginated_response(serializers.data)

    def post(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            if name is not None:
                if len(name) > 200:
                    return Response('Tên ActionCard không được vượt quá 200 ký tự',
                                    status=status.HTTP_400_BAD_REQUEST)
                if name == "":
                    return Response('Tên ActionCard không được rỗng',
                                    status=status.HTTP_400_BAD_REQUEST)
            step_id = request.data.get('step_id')
            actions = self.queryset.filter(step_id=step_id)
            for action in actions:
                if action.name == name:
                    return Response("Tên ActionCard đã tồn tại ở bước này, vui lòng đổi tên khác", status=status.HTTP_403_FORBIDDEN)
            serializer = ActionCardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)


class ActionCardDetail(generics.RetrieveUpdateDestroyAPIView):

    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = ActionCard.objects.all()
    serializer_class = ActionCardSerializer

    def delete(self, request, *args, **kwargs):
        actioncard_id = kwargs.get("pk")
        if actioncard_id is not None and is_valid_uuid(str(actioncard_id)):
            try:
                action_card = self.queryset.get(id=actioncard_id)
                step_id = ''
                if action_card is not None:
                    action_card.delete()
                    if action_card.step is not None:
                        step_id = action_card.step.id
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
                i = 1
                for data in response_data:
                    if data['type'] == "imagecard":
                        print(data)
                        # Retrieve the existing ImageCard instance
                        image_card_instance = ImageCard.objects.get(
                            id=data['id'])
                        serializer = ImageCardSerializer(image_card_instance, data={
                            'num_order': i}, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                    if data['type'] == "textcard":
                        print(data)
                        # Retrieve the existing ImageCard instance
                        text_card_instance = TextCard.objects.get(
                            id=data['id'])
                        serializer = TextCardSerializer(text_card_instance, data={
                                                        'num_order': i}, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                    if data['type'] == "actioncard":
                        print(data)
                        # Retrieve the existing ImageCard instance
                        action_card_instance = ActionCard.objects.get(
                            id=data['id'])
                        serializer = ActionCardSerializer(action_card_instance, data={
                            'num_order': i}, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                    i += 1
                print(response_data)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ActionCard.DoesNotExist:
                return Response({"detail": "ActionCard not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Invalid actioncard ID."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            actioncard_id = kwargs.get("pk")
            if actioncard_id is not None and is_valid_uuid(str(actioncard_id)):
                action_card = self.queryset.get(id=actioncard_id)
                if action_card is not None:
                    name = request.data.get('name')
                    if name is not None:
                        if len(name) > 200:
                            return Response('Tên ActionCard không được vượt quá 200 ký tự',
                                            status=status.HTTP_400_BAD_REQUEST)
                        if name == "":
                            return Response('Tên ActionCard không được rỗng',
                                            status=status.HTTP_400_BAD_REQUEST)
                    step_id = action_card.step.id
                    actioncard_list = self.queryset.filter(step_id=step_id)
                    for ac in actioncard_list:
                        if str(ac.name) == str(name) and str(ac.id) != str(action_card.id):
                            return Response('Tên ActionCard đã tồn tại ở bước này, vui lòng đổi tên khác', status=status.HTTP_400_BAD_REQUEST)
                    instance = self.get_object()

                    # Update the instance with the new data
                    serializer = self.get_serializer(
                        instance, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("Invalid Textcard id", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_403_FORBIDDEN)