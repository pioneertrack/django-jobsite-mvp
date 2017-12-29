from django.conf.urls import url
from content.views import *

urlpatterns = [
    url(r'^stories/$', StoryListView.as_view(), name="stories"),
    url(r'^story/(?P<slug>[\w-]+)/$', StoryDetailView.as_view(), name="story_detail", ),
    url(r'^templates/$', ResourceListView.as_view(), name="templates"),
    url(r'^template/(?P<slug>[\w-]+)/$', ResourceDetailView.as_view(), name="template_detail", ),
    url(r'^picture-autocomplete/$', PictureAutocomplete.as_view(), name='picture-autocomplete', ),
]
