from django.contrib import admin
from django.utils.html import format_html
from content.forms import *


# Register your models here.
class StoryAdmin(admin.ModelAdmin):
    model = Story
    form = StoryForm
    list_display = ['created_at', 'updated_at', 'published', 'page_url']
    list_filter = ['created_at', 'updated_at', 'published']
    search_fields = ['title']
    fields = ['slug', 'published', 'header_name', 'header_image', 'preview', 'title', 'description', 'content', 'youtube_id' ]
    readonly_fields = ['preview']
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        css = {
            "all": ("admin/css/website.css",)
        }

    def preview(self, obj):
        return format_html('<div class="admin preview"><img src="{url}" /></div>', url=format(obj.header_image.image.url))

    def page_url(self, obj):
        return format_html("<a href='{url}'>{title}</a>", url=obj.get_absolute_url(), title=obj.title)

    page_url.short_description = 'Page'


class PictureAdmin(admin.ModelAdmin):
    model = Picture
    list_display = ['created_at', 'updated_at', 'title', 'image']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title']
    readonly_fields = ['preview']

    class Media:
        css = {
            "all": ("admin/css/website.css",)
        }

    def preview(self, obj):
        return format_html('<div class="admin preview"><img src="{url}" /></div>', url=format(obj.image.url))


class CategoryAdmin(admin.ModelAdmin):
    model = ResourceCategory
    list_display = ['created_at', 'title', 'published',]
    prepopulated_fields = {"slug": ("title",)}


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    form = ResourceForm
    list_display = ['created_at', 'updated_at', 'published', 'page_url']
    list_filter = ['created_at', 'updated_at', 'published']
    search_fields = ['title']
    fields = ['slug', 'published', 'category', 'image', 'preview', 'title', 'url', 'description']
    readonly_fields = ['preview']
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        css = {
            "all": ("admin/css/website.css",)
        }

    def preview(self, obj):
        return format_html('<div class="admin preview"><img src="{url}" /></div>', url=format(obj.image.image.url))

    def page_url(self, obj):
        return format_html("<a href='{url}'>{title}</a>", url=obj.get_absolute_url(), title=obj.title)

    page_url.short_description = 'Resource'


admin.site.register(Picture, PictureAdmin)
admin.site.register(ResourceCategory, CategoryAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Resource, ResourceAdmin)
