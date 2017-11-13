from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.urls import reverse


# Create your models here.
class Story(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    header_name = models.CharField(max_length=256, null=True, blank=True)
    header_image = models.ForeignKey('Picture', null=True, blank=True)
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=256)
    content = models.TextField()
    youtube_id = models.CharField(max_length=256, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('content:story_detail', kwargs={'slug': self.slug})


class Picture(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    text_id = models.CharField(max_length=256, null=True, blank=True)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='images/content/')
