from rest_framework import serializers
from mymap.models import MapRoot
from mymap.models import MapChild


class MapRootSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapRoot
        fields = ['id', 'name', 'root_name', 'number_order', 'description']
        #read_only_fields = ['id', 'number_order']  # number_order sẽ chỉ đọc


class MapChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapChild
        fields = ['id', 'name', 'root_name', 'number_order', 'description']
        #read_only_fields = ['id', 'number_order']  # number_order sẽ chỉ đọc

