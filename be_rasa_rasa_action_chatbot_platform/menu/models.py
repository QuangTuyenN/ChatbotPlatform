from django.db import models
from uuid import uuid4


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    nameMenu = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    order = models.IntegerField(blank=False)
    parentId = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    url = models.CharField(max_length=255)
    stt = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

    def __str__(self):
        return self.nameMenu
