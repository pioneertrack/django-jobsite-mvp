from django.shortcuts import render
from django.views.generic.base import TemplateView
from search.documents import PeopleDocument
from elasticsearch_dsl import FacetedSearch


# Create your views here.
class SearchView(TemplateView):

    template_name = 'search_view.html'

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)


        res = PeopleDocument.search().query(
            'multi_match',
            query='John Doe',
            type='cross_fields',
            fields =[
                'major',
                'bio',
                'skills',
                'interests',
                'courses',
                'user.first_name',
                'user.last_name',
                'experience_set.company',
                'experience_set.position',
                'experience_set.description',
            ]
        )

        for hit in res:
            a = hit

        # s = PeopleSearch('John Doe');
        # res = s.execute()

        context['result'] = res;

        return context