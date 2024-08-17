from uuid import uuid4
from django.db import models


class MapRoot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    root_name = models.CharField(max_length=200, null=False, blank=False, default='Root')
    number_order = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=500, blank=True, default='', verbose_name="Description")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name'], name='unique_maproot_name'),
        ]


class MapChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    root_name = models.ForeignKey(MapRoot, on_delete=models.CASCADE, null=True, related_name='mapchild_set')
    number_order = models.IntegerField(null=True, blank=True)
    description = models.TextField(max_length=500, blank=True, default='', verbose_name="Description")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name'], name='unique_mapchild_name'),
        ]
