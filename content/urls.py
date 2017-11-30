from django.conf.urls import url
from content.views import *

urlpatterns = [
    url(r'^stories/$', StoryListView.as_view(), name="stories"),
    url(r'^story/(?P<slug>[\w-]+)/$', StoryDetailView.as_view(), name="story_detail", ),
    url(r'^resources/$', ResourceListView.as_view(), name="resources"),
    url(r'^resource/(?P<slug>[\w-]+)/$', ResourceDetailView.as_view(), name="resource_detail", ),
    url(r'^picture-autocomplete/$', PictureAutocomplete.as_view(), name='picture-autocomplete', ),
]
