from django.contrib import admin
import content.models as models
from django.utils.html import format_html


# Register your models here.
class StoryAdmin(admin.ModelAdmin):
    model = models.Story
    list_display = ['created_at', 'updated_at', 'published', 'page_url']
    list_filter = ['created_at', 'updated_at', 'published']
    search_fields = ['title']
    fields = [ 'slug', 'published', 'header_name', 'header_image', 'preview', 'title', 'description', 'content', 'youtube_id' ]
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
    model = models.Picture
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


admin.site.register(models.Story, StoryAdmin)
admin.site.register(models.Picture, PictureAdmin)
