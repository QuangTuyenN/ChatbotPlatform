# IMPORT FRAMEWORK / THIRD-PARTY
from rest_framework import permissions, generics, status

# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.serializers import CustomActionsSerializer, CustomActionSerializer
from bot.models import CustomAction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from bot.utils import *
import os
from rest_framework.response import Response

HOST_URL_MEDIA = os.environ.get(
    "HOST_URL_MEDIA", "http://10.14.16.30:31003/chatbotplatform/")


class CustomActionList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomActionSerializer
    queryset = CustomAction.objects.all()

    @extend_schema(
        parameters=[OpenApiParameter(name="action_type", description="Filter by action type", required=False, type=str)])
    def get(self, request, *args, **kwargs):
        action_type = request.query_params.get("action_type", '')
        list_customactions = []
        customactions = self.queryset.all().order_by('-created_at')
        if action_type:
            customactions = self.queryset.filter(action_type=action_type)
        for customaction in customactions:
            list_customactions.append({"id": customaction.id,
                                       "action_type": customaction.action_type,
                                       "action_save_name": customaction.action_save_name,
                                       "show_fe_name": customaction.show_fe_name,
                                       "link_url": customaction.link_url,
                                       "image_icon": str(f'{HOST_URL_MEDIA}{customaction.image_icon}')})
        page = self.paginate_queryset(list_customactions)
        serializer = CustomActionsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        customactions = self.queryset.all()
        if len(request.data['action_save_name']) > 250:
            return Response("Độ dài của tên để lưu huấn luyện không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        if len(request.data['show_fe_name']) > 250:
            return Response("Độ dài của tên để hiển thị không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        if request.data['link_url'] is not None and len(request.data['link_url']) > 250:
            return Response("Độ dài của link không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        for customaction in customactions:
            if customaction.action_save_name == request.data['action_save_name']:
                return Response("Tên custom action để train đã tồn tại, vui lòng đổi tên", status=status.HTTP_403_FORBIDDEN)
            if customaction.show_fe_name == request.data['show_fe_name']:
                return Response("Tên custom action để hiển thị đã tồn tại, vui lòng đổi tên", status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class CustomActionDetail(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomActionSerializer
    queryset = CustomAction.objects.all()

    def get(self, request, *args, **kwargs):
        customaction_id = kwargs.get("pk")
        if customaction_id:
            list_customactions = []
            customaction = self.queryset.filter(id=customaction_id).first()
            if customaction.image_icon == "":
                image_icon = ""
            else:
                image_icon = str(f'{HOST_URL_MEDIA}{customaction.image_icon}')
            data = {"id": customaction.id,
                    "action_type": customaction.action_type,
                    "action_save_name": customaction.action_save_name,
                    "show_fe_name": customaction.show_fe_name,
                    "link_url": customaction.link_url,
                    "image_icon": image_icon
                    }
            list_customactions.append(data)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        customaction = self.get_object()
        customactions = self.queryset.all()
        new_action_save_name = request.data['action_save_name']
        new_show_fe_name = request.data['show_fe_name']
        customaction_action_save_name_filters = customactions.filter(
            action_save_name=new_action_save_name)
        count_1 = customaction_action_save_name_filters.count()
        if len(request.data['action_save_name']) > 250:
            return Response("Độ dài của tên để lưu huấn luyện không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        if len(request.data['show_fe_name']) > 250:
            return Response("Độ dài của tên để hiển thị không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        if request.data['link_url'] is not None and len(request.data['link_url']) > 250:
            return Response("Độ dài của link không được quá 250 ký tự, vui lòng sửa lại.",
                            status=status.HTTP_403_FORBIDDEN)
        if count_1 > 1:
            return Response('Tên lưu để huấn luyện đã được sử dụng vui lòng đổi tên khác.',
                            status=status.HTTP_400_BAD_REQUEST)
        customaction_show_fe_name_filters = customactions.filter(
            show_fe_name=new_show_fe_name)
        count_2 = customaction_show_fe_name_filters.count()
        if count_2 > 1:
            return Response('Tên lưu để hiển thị đã được sử dụng vui lòng đổi tên khác.',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(
            customaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Đã PUT customaction', status=status.HTTP_204_NO_CONTENT)
