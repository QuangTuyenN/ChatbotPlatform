from rest_framework import serializers
from bot.models import Bot
from bot.models import ChitChat
from bot.models import ChitChatIntentExample
from bot.models import ChitChatUtterExample
from bot.models import Story
from bot.models import Step
from bot.models import Intent
from bot.models import IntentExample
from bot.models import Entity
from bot.models import EntityKeyWord
from bot.models import Vocabulary
from bot.models import Synonym
from bot.models import TextCard
from bot.models import ImageCard
from bot.models import ActionCard
from bot.models import CustomAction
from bot.models import JsonCard
from bot.models import CarouselCard
from bot.models import FormCard
from bot.models import FormSlot
from bot.models import Slot
from bot.models import Button
from bot.models import Events
from rest_framework.validators import UniqueTogetherValidator


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Bot.objects.all(),
                fields=['account', 'name']
            )
        ]


class ChitChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChitChat
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ChitChat.objects.all(),
                fields=['bot', 'name']
            )
        ]


class ChitChatIntentExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChitChatIntentExample
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ChitChatIntentExample.objects.all(),
                fields=['chitchat', 'text']
            )
        ]


class ChitChatUtterExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChitChatUtterExample
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ChitChatUtterExample.objects.all(),
                fields=['chitchat', 'text']
            )
        ]


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Story.objects.all(),
                fields=['bot', 'name']
            )
        ]


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Step.objects.all(),
        #         fields=['story', 'name', 'num_order']
        #     )
        # ]


class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Intent.objects.all(),
                fields=['bot', 'name']
            )
        ]


class IntentExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentExample
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=IntentExample.objects.all(),
                fields=['text', 'intent']
            )
        ]


class IntentExampleCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    intent_name = serializers.CharField()
    entity_name = serializers.CharField()

    class Meta:
        model = IntentExample
        fields = '__all__'


class IntentExampleFilterCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    entity = serializers.ListField(child=serializers.CharField())


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'


class EntityKeyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityKeyWord
        fields = '__all__'


class EntityKeyWordCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()


class EntityFilterNameCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    extract_type = serializers.CharField()
    keyword = serializers.ListField(child=serializers.CharField())


class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = '__all__'


class SynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Synonym
        fields = '__all__'


class TextCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextCard
        fields = '__all__'


class ImageCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCard
        fields = '__all__'


class CustomActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAction
        fields = '__all__'


class ActionCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionCard
        fields = '__all__'


class JsonApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonCard
        fields = '__all__'


class CarouselCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselCard
        fields = '__all__'


class FormCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormCard
        fields = '__all__'


class FormSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSlot
        fields = '__all__'


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
