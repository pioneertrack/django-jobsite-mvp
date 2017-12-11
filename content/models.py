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


class ResourceCategory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=256)
    def __unicode__(self):
        return self.title


class Resource(models.Model):
    category = models.ForeignKey(ResourceCategory, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    image = models.ForeignKey('Picture', null=True, blank=True)
    title = models.CharField(max_length=256)
    url = models.URLField(max_length=2048)
    description = models.TextField()

    def get_absolute_url(self):
        return reverse('content:story_detail', kwargs={'slug': self.slug})


class Picture(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    text_id = models.CharField(max_length=256, null=True, blank=True)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='images/content/')
    def __unicode__(self):
        return self.title
