from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django import forms
from search.documents import PeopleDocument, StartupDocument, JobDocument
import website.profile as profile
import json

JOB_CONTEXT = {
    'p_context': [
        ('year', list(profile.YEAR_IN_SCHOOL_CHOICES), {'class': 'label-year', 'name': 'year'}),
        ('major', list(profile.MAJORS), {'class': 'label-major', 'name': 'major'}),
        ('role', list(profile.PRIMARY_ROLE), {'class': 'label-role', 'name': 'role'}),
        ('experience', [('0', 'Has startup experience'), ('1', 'Has funding experience')],
         {'class': 'label-experience'}),
        ('position', [
            ('0', 'Partner'),
            ('1', 'Intern'),
            ('2', 'Part-Time'),
            ('3', 'Full-Time'),
            ('4', 'Freelance')
        ], {'class': 'label-position'}),
        ('hours', list(profile.HOURS_AVAILABLE), {'class': 'label-hours', 'name': 'Available'})
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


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context), safe=False,
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return context


# Create your views here.
class SearchView(LoginRequiredMixin, JSONResponseMixin, FormView):
    template_name = 'search.html'
    form_class = forms.Form
    post_data = None
    category = None
    per_page = 9
    page = 0
    offset = 0

    def render_to_response(self, context):
        if self.request.is_ajax():
            return self.render_to_json_response(context.get('items'))
        else:
            return super(SearchView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        if self.category == 'people':
            res = self.people_search()
        elif self.category == 'startups':
            res = self.startup_search()
        elif self.category == 'jobs':
            res = self.job_search()
        context.update({'items': res.hits.hits })
        if self.request.method == 'GET' and not self.request.is_ajax():
            context.update(JOB_CONTEXT)

        return context

    def get(self, request, *args, **kwargs):
        self.page = int(kwargs.get('page', 0))
        post_data = request.session.get('post_search_data') if request.is_ajax() else None
        self.post_data = json.loads(post_data) if not post_data is None else None
        if post_data:
            self.category = self.post_data['select-category'][0]
        else:
            self.category = request.COOKIES.get('select-category') if request.COOKIES.get('select-category') else 'people'

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.page = int(kwargs.get('page', 0))
        post_data = json.dumps(dict(request.POST))
        request.session['post_search_data'] = post_data
        self.post_data = json.loads(post_data)
        self.category = self.post_data['select-category'][0]

        return self.render_to_response(self.get_context_data())

    def people_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        years = majors = roles = experience = position = hours = []
        if self.post_data:
            years = self.post_data['year']
            majors = self.post_data['major']
            roles = self.post_data['role']
            experience = self.post_data['experience']
            position = self.post_data['position']
            hours = self.post_data['hours']
        self.offset = 0 if self.page == 0 else self.page * self.per_page

        query = {
            'from': self.offset,
            'size': self.per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'user.is_active': True}},
                        {'term': {'user.is_individual': True}},
                        {'term': {'user.is_account_disabled': False}},
                        {'term': {'is_filled': True}},
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

    def startup_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        fields = stage = []
        if self.post_data:
            fields = self.post_data['fields']
            stage = self.post_data['stage']
        self.offset = 0 if self.page == 0 else self.page * self.per_page

        query = {
            'from': self.offset,
            'size': self.per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'user.is_active': True}},
                        {'term': {'user.is_account_disabled': False}},
                        {'term': {'user.is_founder': True}},
                        {'term': {'is_filled': True}},
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
                        'user.first_name',
                        'user.last_name'
                        'job_set.title',
                        'job_set.description',
                        'job_set.level',
                        'job_set.pay',
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

    def job_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        if self.post_data:
            job_category = self.post_data['category']
            level = self.post_data['level']
            pay = self.post_data['pay']

        query = {
            'from': self.offset,
            'size': self.per_page,
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
