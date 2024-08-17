# IMPORT FRAMEWORK / THIRD-PARTY
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max, F

# IMPORT CUSTOM MODULE / LOCAL FILES
from mymap.serializers import MapRootSerializer, MapChildSerializer, MapChildCustomSerializer
from mymap.models import MapRoot, MapChild

# IMPORT PYTHON LIB
from bot.utils import *


class MapRootList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post"]
    serializer_class = MapRootSerializer
    queryset = MapRoot.objects.prefetch_related('mapchild_set').order_by('number_order')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        maproots_data = []
        for maproot in queryset:
            maproot_serializer = self.get_serializer(maproot)
            maproot_data = maproot_serializer.data
            # Lấy tất cả các MapChild liên quan đến MapRoot này
            mapchildren = maproot.mapchild_set.all()
            mapchild_serializer = MapChildSerializer(mapchildren, many=True)
            # Thêm thông tin MapChild vào dữ liệu trả về của MapRoot
            maproot_data['children'] = mapchild_serializer.data
            maproots_data.append(maproot_data)

        return Response(maproots_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name', '')
        description = serializer.validated_data.get('description', '')

        # Kiểm tra độ dài của name và description
        if str(name) =='':
            return Response('Trường name không được trống', status=status.HTTP_400_BAD_REQUEST)
        if len(name) > 200:
            return Response({"name không được quá 200 kí tự"}, status=status.HTTP_400_BAD_REQUEST)

        if len(description) > 500:
            return Response({"description không được quá 500 kí tự"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra xem name đã tồn tại hay chưa
        if MapRoot.objects.filter(name=name).exists():
            return Response({"name đã được sử dụng, vui lòng đổi tên khác"}, status=status.HTTP_400_BAD_REQUEST)

        # Tìm number_order lớn nhất hiện có và tăng thêm 1
        max_order = MapRoot.objects.aggregate(Max('number_order'))['number_order__max']
        if max_order is None:
            max_order = 0
        serializer.save(number_order=max_order + 1)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MapRootDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "put", "delete"]
    serializer_class = MapRootSerializer
    queryset = MapRoot.objects.all()

    def delete(self, request, *args, **kwargs):
        # Lấy đối tượng cần xóa
        instance = self.get_object()
        number_order_to_delete = instance.number_order

        # Xóa đối tượng
        self.perform_destroy(instance)

        # Dịch chuyển lùi các number_order lớn hơn
        MapRoot.objects.filter(number_order__gt=number_order_to_delete).update(number_order=F('number_order') - 1)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        maproot_id = kwargs.get("pk")
        if maproot_id is not None:
            try:
                number_order = request.data.get('number_order')
                description = request.data.get('description')
                new_name = request.data.get('name')
                maproot = self.queryset.get(id=maproot_id)
                maproots = self.queryset.all()
                if len(description) > 500:
                    return Response({"description không được quá 500 kí tự"}, status=status.HTTP_403_FORBIDDEN)
                else:
                    maproot.description = request.data.get('description', maproot.description)
                num_maproot = len(self.queryset.all())
                maproot_name_filters = maproots.filter(name=new_name)
                if len(maproot_name_filters) > 1:
                    return Response('Tên maproot đã được sử dụng, vui lòng đổi tên khác',
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    maproot.name = request.data.get('name', maproot.name)
                maproot.root_name = request.data.get('root_name', maproot.name)
                maproot.save()
                if number_order is not None:
                    if int(number_order) <= 0 or int(number_order) >= num_maproot + 1:
                        return Response({"detail": "number_order ko hợp lệ."}, status=status.HTTP_403_FORBIDDEN)
                    maproots = list(self.queryset.all().order_by('number_order'))
                    for mr in maproots:
                        print(mr.id)
                    maproot = self.queryset.get(id=maproot_id)
                    removed_element = maproots.pop(maproot.number_order - 1)
                    for mr in maproots:
                        print(mr.id)
                    print("maproot đã remove", removed_element)
                    maproots.insert(int(number_order)-1, maproot)
                    i = 1
                    for mr in maproots:
                        print(mr.id)
                        mr.number_order = i
                        i += 1
                        mr.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as bug:
                return Response({"detail": "không tìm thấy maproot."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "maproot ID không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)


class MapChildList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]
    serializer_class = MapChildSerializer
    queryset = MapChild.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name', '')
        description = serializer.validated_data.get('description', '')

        # Kiểm tra độ dài của name và description
        if str(name) == '':
            return Response('Trường name không được trống', status=status.HTTP_400_BAD_REQUEST)

        if len(name) > 200:
            return Response({"name không được quá 200 kí tự"}, status=status.HTTP_400_BAD_REQUEST)

        if len(description) > 500:
            return Response({"description không được quá 500 kí tự"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra xem name đã tồn tại hay chưa
        if MapChild.objects.filter(name=name).exists():
            return Response({"name đã được sử dụng, vui lòng đổi tên khác"}, status=status.HTTP_400_BAD_REQUEST)

        root_name_id = serializer.validated_data['root_name'].id
        max_order = MapChild.objects.filter(root_name_id=root_name_id).aggregate(Max('number_order'))['number_order__max']
        if max_order is None:
            max_order = 0
        serializer.save(number_order=max_order + 1)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MapChildDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "put", "delete"]
    serializer_class = MapChildSerializer
    queryset = MapChild.objects.select_related('root_name')

    def delete(self, request, *args, **kwargs):
        # Lấy đối tượng cần xóa
        instance = self.get_object()
        number_order_to_delete = instance.number_order
        root_name_id = instance.root_name.id

        # Xóa đối tượng
        self.perform_destroy(instance)

        # Dịch chuyển lùi các number_order lớn hơn
        MapChild.objects.filter(root_name_id=root_name_id, number_order__gt=number_order_to_delete).update(number_order=F('number_order') - 1)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        mapchild_id = kwargs.get("pk")
        print("mapchild id: ", mapchild_id)
        if mapchild_id is not None:
            try:
                number_order = request.data.get('number_order')
                description = request.data.get('description')
                new_name = request.data.get('name')
                mapchild = self.queryset.get(id=mapchild_id)
                maproot_id = mapchild.root_name.id
                mapchilds = self.queryset.filter(root_name=maproot_id)
                if len(description) > 500:
                    return Response({"description không được quá 500 kí tự"}, status=status.HTTP_403_FORBIDDEN)
                else:
                    mapchild.description = request.data.get('description', mapchild.description)
                num_mapchild = len(self.queryset.filter(root_name=maproot_id))
                mapchild_name_filters = mapchilds.filter(name=new_name)
                if len(mapchild_name_filters) > 1:
                    return Response('Tên mapchild đã được sử dụng, vui lòng đổi tên khác',
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    mapchild.name = request.data.get('name', mapchild.name)
                mapchild.root_name_id = request.data.get('root_name_id', mapchild.root_name.id)
                mapchild.save()
                if number_order is not None:
                    if int(number_order) <= 0 or int(number_order) >= num_mapchild + 1:
                        return Response({"detail": "number_order ko hợp lệ."}, status=status.HTTP_403_FORBIDDEN)
                    mapchilds = list(self.queryset.filter(root_name_id=maproot_id).order_by('number_order'))
                    for mc in mapchilds:
                        print(mc.id)
                    mapchild = self.queryset.get(id=mapchild_id)
                    removed_element = mapchilds.pop(mapchild.number_order - 1)
                    for mc in mapchilds:
                        print(mc.id)
                    print("mapchild đã remove", removed_element)
                    mapchilds.insert(int(number_order) - 1, mapchild)
                    i = 1
                    for mc in mapchilds:
                        mc.number_order = i
                        i += 1
                        mc.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as bug:
                return Response({"detail": "không tìm thấy mapchild."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "mapchild ID không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        mapchild_id = kwargs.get("pk")
        if mapchild_id:
            list_mapchilds = []
            mapchild = self.queryset.get(id=mapchild_id)
            data = {
                "id": mapchild.id,
                "name": mapchild.name,
                "root_name_id": mapchild.root_name.id,
                "number_order": mapchild.number_order,
                "description": mapchild.description,
                "root_name_name": mapchild.root_name.name
            }
            list_mapchilds.append(data)
            serializers = MapChildCustomSerializer(list_mapchilds, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

