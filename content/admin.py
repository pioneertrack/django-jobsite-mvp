from django.contrib import admin
import content.models as models


# Register your models here.
class StoryAdmin(admin.ModelAdmin):
    model = models.Story
    prepopulated_fields = {"slug": ("title",)}


class PictureAdmin(admin.ModelAdmin):
    model = models.Picture
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(models.Story, StoryAdmin)
admin.site.register(models.Picture, PictureAdmin)
