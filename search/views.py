from django.db.models.functions.base import Lower
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django import forms
from search.documents import PeopleDocument, StartupDocument, JobDocument
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
class SearchView(LoginRequiredMixin, FormView):
    template_name = 'search_view.html'
    form_class = forms.Form

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update(JOB_CONTEXT)
        return context

    def post(self, request, page=0, *args, **kwargs):
        category = request.POST.get('select-category', 'partners')
        query_string = request.POST.get('query', '')
        current_page = int(page)
        per_page = 9
        current_offset = (current_page * per_page) - 1
        if current_offset < 0:
            current_offset = 0

        if category == 'partners' or category == 'employees' or category == 'freelancers':
            res = self.people_search(request, category, query_string, per_page, current_offset)

        elif category == 'startups':
            res = self.startup_search(request, query_string, per_page, current_offset)

        elif category == 'jobs':
            res = self.job_search(request, query_string, per_page, current_offset)

        else:
            return JsonResponse({'error': 'Unknown request'})

        search_response = {
            'category': category,
            'items': {}
        }
        for hit in res:
            id = hit.meta.id
            search_response['items'][id] = hit.to_dict()

        return JsonResponse(search_response)

    def people_search(self, request, category, query_string, per_page, current_offset):
        position = request.POST.getlist('position_' + category)
        years = request.POST.getlist('year_' + category)
        majors = request.POST.getlist('major_' + category)
        roles = request.POST.getlist('role_' + category)
        experience = request.POST.getlist('experience_' + category)

        query = {
            'from': current_offset,
            'size': per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'user.is_active': True}},
                        {'term': {'user.is_individual': True}},
                        {'term': {'user.is_account_disabled': False}},
                    ]
                }
            }
        }

        if len(query_string) > 0:
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

        if '' in position:
            position.remove('')

        if len(position) > 0:
            query['query']['bool']['filter'].append({'terms': {'positions': position}})

        if '' in years:
            years.remove('')

        if len(years) > 0:
            query['query']['bool']['filter'].append({'terms': {'year': years}})

        if '' in majors:
            majors.remove('')

        if len(majors) > 0:
            query['query']['bool']['filter'].append({'terms': {'major': majors}})

        if '' in roles:
            roles.remove('')

        if len(roles) > 0:
            query['query']['bool']['filter'].append({'terms': {'role': roles}})

        if len(experience) > 1 or ('' not in experience and len(experience) > 0):
            for item in experience:
                if item == '1':
                    query['query']['bool']['filter'].append({'term': {'has_funding_exp': True}})
                elif item == '0':
                    query['query']['bool']['filter'].append({'term': {'has_startup_exp': True}})
        return PeopleDocument.search().from_dict(query).execute()

    def startup_search(self, request, query_string, per_page, current_offset):

        fields = request.POST.getlist('fields')
        stage = request.POST.getlist('stage')

        query = {
            'from': current_offset,
            'size': per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'user.is_active': True}},
                        {'term': {'user.is_account_disabled': False}},
                        {'term': {'user.is_founder': True}},
                    ]
                }
            }
        }

        if len(query_string) > 0:
            query['query']['bool']['must'] = {
                'multi_match': {
                    'query': query_string,
                    'type': 'cross_fields',
                    'fields': [
                        'startup_name',
                        'description',
                    ]
                }
            }

        if '' in fields:
            fields.remove('')

        if len(fields) > 0:
            query['query']['bool']['filter'].append({'terms': {'field': fields}})

        if '' in stage:
            stage.remove('')

        if len(stage) > 0:
            query['query']['bool']['filter'].append({'terms': {'stage': stage}})

        query = StartupDocument.search().from_dict(query)
        # TODO: In some reason query index name is clears
        query._index = 'startup'
        return query.execute()

    def job_search(self, request, query_string, per_page, current_offset):
        query = {
            'from': current_offset,
            'size': per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'founder.is_filled': True}}
                    ]
                }
            }
        }

        if len(query_string) > 0:
            query['query']['bool']['must'] = {
                'multi_match': {
                    'query': query_string,
                    'type': 'cross_fields',
                    'fields': [
                        'title',
                        'description',
                        'founder.startup_name',
                    ]
                }
            }

        job_category = request.POST.getlist('category')
        level = request.POST.getlist('level')
        pay = request.POST.getlist('pay')

        if '' in level:
            level.remove('')

        if '' in pay:
            pay.remove('')

        if '' in job_category:
            job_category.remove('')

        if len(level) > 0:
            query['query']['bool']['filter'].append({'terms': {'level': level}})

        if len(pay) > 0:
            query['query']['bool']['filter'].append({'terms': {'pay': pay}})

        if len(job_category) > 0:
            query['query']['bool']['filter'].append({'terms': {'founder.field': job_category}})

        return JobDocument.search().from_dict(query).execute()
