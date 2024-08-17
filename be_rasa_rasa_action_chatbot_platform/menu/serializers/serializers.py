from rest_framework import serializers
from menu.models import Menu
from rest_framework.validators import UniqueTogetherValidator


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Menu.objects.all(),
        #         fields=['nameMenu', 'parentId']
        #     )
        # ]
