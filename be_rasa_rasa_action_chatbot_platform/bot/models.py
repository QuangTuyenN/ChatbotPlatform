from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod
from uuid import uuid4
from django.db import models
from account.models import Account


class Bot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.CharField(max_length=200, null=False)
    name = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=500, blank=True, default='')
    LANGUAGES = [("en", "English"), ("vi", "Tiếng Việt")]
    language = models.CharField(
        max_length=40, choices=LANGUAGES, blank=False, null=False)
    intent_confidence = models.FloatField(default=0.2)
    story_confidence = models.FloatField(default=0.2)
    default_answer_low_conf = models.CharField(
        max_length=200, null=False, default="Not understand/Bot không hiểu")
    last_trained = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'name'], name='unique_bot_name')
        ]


class ChitChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'name'], name='unique_chitchat_name')
        ]

        verbose_name = "Chithat"
        verbose_name_plural = "Chithats"


class ChitChatIntentExample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    chitchat = models.ForeignKey(
        'ChitChat', on_delete=models.CASCADE, null=False)
    text = models.TextField(max_length=500, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['chitchat', 'text'], name='unique_cc_intent_example')
        ]

        verbose_name = "Chithat Intent Example"
        verbose_name_plural = "Chithat Intent Examples"


class ChitChatUtterExample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    chitchat = models.ForeignKey(
        'ChitChat', on_delete=models.CASCADE, null=False)
    text = models.TextField(max_length=1000, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['chitchat', 'text'], name='unique_cc_utter_example')
        ]

        verbose_name = "Chithat Utter Example"
        verbose_name_plural = "Chithat Utter Examples"


class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'name'], name='unique_story_name')
        ]

        verbose_name = "Story"
        verbose_name_plural = "Stories"


class Step(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    story = models.ForeignKey('Story', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['story', 'name'], name='unique_step_name'),
    #         models.UniqueConstraint(
    #             fields=['story', 'num_order'], name='unique_step_order')
    #     ]


class Intent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    step = models.OneToOneField(
        'Step', on_delete=models.SET_NULL, null=True, default=None)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(max_length=500, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'name'], name='unique_intent_name')
        ]


class IntentExample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    intent = models.ForeignKey(
        'Intent', on_delete=models.SET_NULL, null=True, default=None)
    text = models.TextField(max_length=500, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['intent', 'text'], name='unique_intent_example')
        ]


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(max_length=300, blank=True, default='')
    TYPES = [("duckling", "Thực thể hệ thống"),
             ("policy", "Trích xuất theo tiên đoán")]
    extract_type = models.CharField(
        max_length=40, choices=TYPES, blank=False, null=False, default="policy")
    # intent_example = models.ManyToManyField('IntentExample')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'name'], name='unique_entity')
        ]

        verbose_name = "Entity"
        verbose_name_plural = "Entities"


class EntityKeyWord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE, null=False)
    text = models.TextField(max_length=200, null=False)
    intent_example = models.ManyToManyField('IntentExample')
    start_position = models.IntegerField(null=False, blank=False)
    end_position = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text}"

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['entity', 'text'], name='unique_entity_key_word')
    #     ]


class Vocabulary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    word = models.CharField(max_length=200, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.word}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'word'], name='unique_vocab')
        ]

        verbose_name = "Vocabulary"
        verbose_name_plural = "Vocabularies"


class Synonym(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vocab = models.ForeignKey(
        'Vocabulary', on_delete=models.CASCADE, null=False)
    word = models.CharField(max_length=200, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.word}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['vocab', 'word'], name='unique_vocab_synonym')
        ]


class TextCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    text = models.TextField(max_length=1000, null=True, blank=True)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_textcard_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_textcard_order')
        ]


class ImageCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    # carousel = models.ForeignKey('CarouselCard', on_delete=models.SET_NULL, null=True, default=None)
    name = models.CharField(max_length=200, null=True, blank=False)
    image = models.ImageField(upload_to='bot_image_cards', blank=True)

    text = models.TextField(max_length=500, null=False, blank=True)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_imgcard_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_imgcard_order')
        ]


class ActionCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    action = models.ForeignKey(
        'CustomAction', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_action_card_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_action_card_order')
        ]


# class CustomAction(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     # name = models.CharField(max_length=200, null=False, blank=False)
#     TYPES = [("action_happy_face", "Biểu cảm vui vẻ"), ("action_sad_face", "Biểu cảm buồn"),
#              ("action_close_eyes_face", "Biểu cảm nhắm mắt"), ("action_sleepy_face", "Biểu cảm buồn ngủ"),
#              ("action_wake_up_face", "Biểu cảm thức dậy"), ("action_heart_eyes_face", "Biểu cảm mắt trái tim"),
#              ("action_angry_face", "Biểu cảm tức giận"), ("action_adorable_sulking_face", "Biểu cảm hạnh phúc"),
#              ("action_supprised_face", "Biểu cảm ngạc nhiên"), ("action_dizzy_face", "Biểu cảm chóng mặt"),
#              ("action_turn_on_youtube", "Bật màn hình youtube"), ("action_turn_on_google", "Bật màn hình google"),
#              ("action_turn_on_google_map", "Bật màn hình google map"), ("action_record_video_feature", "Bật màn hình quay video"),
#              ("action_take_picture_feature", "Bật màn hình chụp ảnh"), ("action_what_time_is_it", "Hỏi giờ hiện tại"),
#              ("action_what_date_is_it", "Hỏi ngày dương lịch hôm nay"), ("action_guide_direction", "Bật tính năng dẫn đường"),
#              ("action_today_lunar_day", "Hỏi ngày âm lịch hôm nay"), ("action_temperature", "Hỏi nhiệt độ phòng"),
#              ("action_weekdays", "Hỏi thứ trong tuần hôm nay"), ("action_this_year_zodiac_animal", "Hỏi năm con giáp năm nay"),
#              ("action_money_exchange", "Quy đổi tiền tệ"), ("action_holiday_number", "Hỏi ngày lễ trong năm"),
#              ("action_video_dinh_huong", "Phát video định hướng Thaco Industries"),
#              ("action_video_kinh_doanh", "Phát video sản phẩm kinh doanh Thaco Industries"),
#              ("action_video_chat_luong", "Phát video chứng nhận chất lượng Thaco Industries"),
#              ("action_video_thanh_tuu", "Phát video thành tựu Thaco Industries")]
#     name = models.CharField(max_length=40, choices=TYPES, blank=False, null=False, default="")
#     created_by = models.ForeignKey(Account, related_name='customaction_crt_by', on_delete=models.CASCADE, null=False)
#     updated_by = models.ForeignKey(Account, related_name='customaction_upd_by', on_delete=models.CASCADE, null=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['name'], name='unique_custom_action')
#         ]

class CustomAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # name = models.CharField(max_length=200, null=False, blank=False)
    TYPES = [("face_emotion", "Biểu cảm khuôn mặt"), ("touch_monitor", "Màn hình bụng"),
             ("other_request", "Action gọi ngoài")]
    action_type = models.CharField(
        max_length=40, choices=TYPES, blank=False, null=False, default='')
    action_save_name = models.CharField(
        max_length=250, null=False, blank=False, default='')
    show_fe_name = models.CharField(
        max_length=250, null=False, blank=False, default='')
    link_url = models.CharField(max_length=250, null=True, blank=False)
    image_icon = models.ImageField(upload_to='icon_image', default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.action_save_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['action_save_name'], name='unique_custom_action')
        ]


class JsonCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    num_order = models.IntegerField(null=False, blank=False)
    TYPES = [('POST', 'POST'), ('GET', 'GET')]
    send_method = models.CharField(
        max_length=40, choices=TYPES, blank=False, null=False)
    url = models.CharField(max_length=200, null=False, blank=False)
    headers = models.JSONField(null=False, blank=False)
    data = models.JSONField(null=True, blank=False)
    use_entity = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_jsonapi_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_jsonapi_order')
        ]


class CarouselCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_carouselcard_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_carouselcard_order')
        ]


class FormCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    step = models.ForeignKey('Step', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    num_order = models.IntegerField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['step', 'name'], name='unique_formcard_name'),
            models.UniqueConstraint(
                fields=['step', 'num_order'], name='unique_formcard_order')
        ]


class FormSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    form = models.ForeignKey('FormCard', on_delete=models.CASCADE, null=False)
    slot = models.ForeignKey('Slot', on_delete=models.CASCADE, null=False)
    utter_to_get_slot = models.TextField(max_length=300, null=False)
    utter_again_if_not_valid = models.TextField(
        max_length=300, null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.utter_to_get_slot}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['form', 'slot'], name='unique_formslot')
        ]


class Slot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    entity = models.ForeignKey('Entity', on_delete=models.SET_NULL, null=True)
    VALIDATE_TYPES = [("text", "Text"),
                      ("email", "Email"),
                      ("number", "Number"),
                      ("datetime", "Datetime"),
                      ("url", "Url"),
                      ("cmnd", "CMND"),
                      ("vn_phone_number", "VN-PhoneNumber")]
    validate_type = models.CharField(
        max_length=40, choices=VALIDATE_TYPES, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['bot', 'name'], name='unique_slot_name')
        ]


class Button(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    text_card = models.ForeignKey(
        'TextCard', on_delete=models.CASCADE, null=True)
    image_card = models.ForeignKey(
        'ImageCard', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=70, null=False, blank=False)
    payload = models.ForeignKey('Intent', on_delete=models.CASCADE, null=False)
    slot = models.ManyToManyField('Slot')
    url = models.CharField(max_length=500, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Events(PostgresPartitionedModel):
    class PartitioningMeta:
        db_table = 'events'
        method = PostgresPartitioningMethod.RANGE
        key = ["timestamp"]
    sender_id = models.CharField(max_length=255)
    type_name = models.CharField(max_length=255)
    timestamp = models.FloatField(blank=True, null=True)
    intent_name = models.CharField(max_length=255, blank=True, null=True)
    action_name = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'events'  # Ensure the table name is correct
        managed = False
