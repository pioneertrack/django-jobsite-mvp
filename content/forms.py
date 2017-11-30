from dal import autocomplete
from django import forms
from content.models import *


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = '__all__'
        widgets = {
            'header_image': autocomplete.ModelSelect2(url='content:picture-autocomplete', attrs={'data-html': True})
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'
        widgets = {
            'image': autocomplete.ModelSelect2(url='content:picture-autocomplete', attrs={'data-html': True})
        }
