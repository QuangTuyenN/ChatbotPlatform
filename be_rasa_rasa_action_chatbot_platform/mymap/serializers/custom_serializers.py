from rest_framework import serializers
from .serializers import *


class MapChildCustomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    root_name_id = serializers.CharField()
    number_order = serializers.IntegerField()
    description = serializers.CharField()
    root_name_name = serializers.CharField()




