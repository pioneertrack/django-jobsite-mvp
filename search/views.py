from django.shortcuts import render
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django import forms
from search.documents import PeopleDocument
from elasticsearch_dsl import FacetedSearch
import website.profile as profile

JOB_CONTEXT = {
    'p_context': [
        ('year', list(profile.YEAR_IN_SCHOOL_CHOICES), {'class': 'label-year', 'name': 'year'}),
        ('major', list(profile.MAJORS), {'class': 'label-major', 'name': 'major'}),
        ('role', list(profile.PRIMARY_ROLE), {'class': 'label-role', 'name': 'role'}),
        ('experience', [('0', 'Has startup experience'), ('1', 'Has funding experience')],
         {'class': 'label-experience'}),
    ],
    'e_context': [
        ('position', [
            ('1', 'Intern'),
            ('2', 'Part-Time'),
            ('3', 'Full-Time')
        ], {'class': 'label-position'}),
    ],
    'f_context': [
        ('stage', list(profile.STAGE), {'class': 'label-stage'}),
        ('fields', list(profile.CATEGORY), {'class': 'label-field', 'name': 'field'})
    ],
    'job_context': [
        ('category', list(profile.CATEGORY), {'class': 'label-category'}),
        ('level', list(profile.LEVELS), {'class': 'label-level'}),
        ('pay', list(profile.POSITION), {'class': 'label-pay'})
    ]
}


# Create your views here.
class SearchView(FormView):
    template_name = 'search_view.html'
    form_class = forms.Form

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context

    def post(self, request, page=0, *args, **kwargs):
        current_page = int(page)
        category = request.POST.get('select-category', 'partners')
        query_string = request.POST.get('query', '')

        position = request.POST.getlist('position_' + category)
        years = request.POST.getlist('year_' + category)
        majors =  request.POST.getlist('major_' + category)
        roles = request.POST.getlist('role_' + category)
        experience = request.POST.getlist('experience_' + category)

        per_page = 6
        current_offset = (current_page * per_page) - 1

        if (current_offset < 0):
            current_offset = 0

        query = {
            'from': current_offset,
            'size': per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'user.is_active': True}},
                        {'term': {'user.is_individual': True}},
                        {'term': {'user.is_account_disabled': False}},
                        {'terms': {'positions': ['0', '1', '4']}},
                        #{'terms': {'year': years}},
                        #{'terms': {'role': roles}},
                        {'terms': {'major': ['eecs']}}
                    ]
                }
            }
        }

        if (len(query_string) > 0):
            query['query']['bool']['must'] = {
                'multi_match': {
                    'query': query_string,
                    'type': 'cross_fields',
                    'fields': [
                        'major',
                        'major_display',
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
                }
            }

        #if '' in majors:
        #    majors.remove('')

        #if len(majors) > 0:
        #    query['query']['bool']['filter'].append({'terms': {'major': ['CS', 'EECS']}})


        res = PeopleDocument.search().from_dict(query).execute()

        search_response = {}
        for hit in res:
            id = hit.meta.id
            search_response[id] = hit.to_dict()

        return JsonResponse(search_response)
