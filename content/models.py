from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


# Create your models here.
class Story(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    published = models.BooleanField(default=False)
    title = models.CharField(max_length=256)
    content = models.TextField(max_length=256)


class Picture(models.Model):
    stories = models.ManyToManyField(Story)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    text_id = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    image = models.ImageField()
