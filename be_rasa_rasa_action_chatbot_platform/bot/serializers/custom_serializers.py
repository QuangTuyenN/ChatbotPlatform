from rest_framework import serializers
from .serializers import *


class ChitChatCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    int_exps = serializers.ListField(child=serializers.CharField())
    utt_exps = serializers.ListField(child=serializers.CharField())


class StepDataCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    story = serializers.CharField()
    num_order = serializers.IntegerField()
    # created_by = serializers.CharField()
    # updated_by = serializers.CharField()
    intent_name = serializers.CharField()


class StoryCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    bot = serializers.CharField()
    steps = serializers.ListField(child=StepDataCustomSerializer())


class IntentCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    description = serializers.CharField()
    name = serializers.CharField()
    int_exps = serializers.ListField(child=serializers.CharField())


class UnusedIntentCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class EntityCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    extract_type = serializers.CharField()


class EntityKeyWordCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()


class EntityKeyWordBotCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    entity = serializers.CharField()
    extract_type = serializers.CharField()
    keyword = serializers.CharField()


class IntentExampleFilterCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    intent_name = serializers.CharField()
    text = serializers.CharField()
    entity = serializers.ListField(child=serializers.CharField())


class FormCardStepCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    step = serializers.CharField()
    num_order = serializers.IntegerField()
    form_slot = serializers.ListField(child=FormSlotSerializer())


class SelectSlotCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    is_used = serializers.BooleanField()


class SlotPostStepCustomSerializer(serializers.Serializer):
    list_entity = serializers.ListField(child=EntitySerializer())
    list_validate_types = serializers.ListField(child=serializers.CharField())


class ImageCardCustomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    step = serializers.CharField()
    name = serializers.CharField()
    image = serializers.CharField()
    text = serializers.CharField()
    num_order = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()


class UtterStepCustomSerializer(serializers.Serializer):
    textcard = serializers.ListField(child=TextCardSerializer())
    imagecard = serializers.ListField(child=ImageCardCustomSerializer())
    formcard = serializers.ListField(child=FormCardStepCustomSerializer())
    jsoncard = serializers.ListField(child=JsonApiSerializer())
    action = serializers.ListField(child=ActionCardSerializer())


class StepCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    num_order = serializers.IntegerField()
    story_id = serializers.CharField()
    intent_id = serializers.CharField()
    intent_name = serializers.CharField()
    intent_description = serializers.CharField()
    intent_example = serializers.ListField(
        child=IntentExampleSerializer())
    action = serializers.ListField(child=UtterStepCustomSerializer())


class StoryListSerializer(serializers.Serializer):
    list_story = serializers.ListField(child=StoryCustomSerializer())
    recent_step = serializers.ListField(child=StepCustomSerializer())


class IntentExampleCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    # intent = serializers.ListField(child=serializers.CharField())
    # entity = serializers.ListField(child=serializers.CharField())
    intent = serializers.DictField()
    entity = serializers.ListField(child=serializers.DictField())


class EntityKeyWordExtractTypeCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    extract_type = serializers.CharField()
    name = serializers.CharField()
    keyword = serializers.ListField(child=serializers.CharField())


class EntityFilterNameCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    extract_type = serializers.CharField()
    keyword = serializers.ListField(child=serializers.CharField())


class ChitChatIntentExampleCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    bot = serializers.CharField()
    chitchat = serializers.CharField()
    # created_by = serializers.CharField()
    # updated_by = serializers.CharField()


class ChitChatUtterExampleCustomSerializer(serializers.Serializer):
    id = serializers.CharField()
    text = serializers.CharField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    bot = serializers.CharField()
    chitchat = serializers.CharField()
    # created_by = serializers.CharField()
    # updated_by = serializers.CharField()


class SummarySerializer(serializers.Serializer):
    chitchats = serializers.IntegerField()
    chitchat_intent_examples = serializers.IntegerField()
    chitchat_utter_examples = serializers.IntegerField()
    intents = serializers.IntegerField()
    intent_examples = serializers.IntegerField()
    entities = serializers.IntegerField()
    stories = serializers.IntegerField()


class BotCustomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    language = serializers.CharField(max_length=50)
    intent_confidence = serializers.FloatField()
    story_confidence = serializers.FloatField()
    default_answer_low_conf = serializers.CharField()
    last_trained = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    account = serializers.UUIDField()
    # created_by = serializers.UUIDField()
    # updated_by = serializers.UUIDField()
    summary = SummarySerializer()


class EventsCustomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    timestamp = serializers.CharField()
    text = serializers.CharField()
    intent_name = serializers.CharField()
    confidence = serializers.FloatField()


class CustomActionsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    action_type = serializers.CharField()
    action_save_name = serializers.CharField()
    show_fe_name = serializers.CharField()
    link_url = serializers.CharField()
    image_icon = serializers.CharField()
