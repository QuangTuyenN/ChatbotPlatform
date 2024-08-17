import os
import uuid
import unicodedata
import unidecode


HOST_URL_MEDIA = os.environ.get(
    "HOST_URL_MEDIA", "http://10.14.16.30:31003/chatbotplatform/")


def is_valid_uuid(input_string):
    try:
        uuid_obj = uuid.UUID(input_string)
        return str(uuid_obj) == input_string
    except ValueError:
        return False


def normalize_vietnamese(text):
    # Loại bỏ dấu tiếng Việt
    text = unidecode.unidecode(text)
    # Chuyển thành chữ thường
    text = text.lower()
    return text
