from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django import forms
from search.documents import PeopleDocument, StartupDocument, JobDocument
import search.documents as s_docs
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from website.decorators import check_profiles, test_mode
from django.utils import timezone
import website.profile as profile
from django.urls import reverse
import json
import statsy

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
            ('4', 'Freelance'),
            ('M', 'Mentor')
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
    form_class = forms.Form
    post_data = None
    category = None
    per_page = 9
    page = 0
    offset = 0

    def get_request(request):
        statsy.send()

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
        context.update({'items': res.hits.hits, 'search_category': self.category})
        if self.request.method == 'GET' and not self.request.is_ajax() or self.request.method == 'POST' and not self.request.is_ajax():
            context.update(JOB_CONTEXT)

        return context

    @method_decorator(test_mode)
    @method_decorator(check_profiles)
    @method_decorator(vary_on_headers('User-Agent', 'X-Session-Header'))
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            statsy.send(group='index', event='page_view', value=1, user=request.user, url=reverse('search:search'))
        self.page = int(kwargs.get('page', 0))
        self.category = None
        # Check for cookie from get request get category from it if exists
        if not request.COOKIES.get('select-category') is None:
            self.category = request.COOKIES.get('select-category')
            if not request.session.get('post_search_data') is None:
                del request.session['post_search_data']
        # If not it's a get request after initiating search from previous post request
        elif not request.session.get('post_search_data') is None:
            post_data = request.session.get('post_search_data')
            self.post_data = json.loads(post_data)
            self.category = self.post_data['select-category'][0]

        return self.render_to_response(self.get_context_data())

    @method_decorator(test_mode)
    @method_decorator(check_profiles)
    def post(self, request, *args, **kwargs):
        statsy.send(group='index', event='page_view', value=1, user=request.user, url=reverse('search:search'))
        self.page = int(kwargs.get('page', 0))
        post_data = json.dumps(dict(request.POST))
        request.session['post_search_data'] = post_data
        self.post_data = json.loads(post_data)
        self.category = self.post_data['select-category'][0]
        response = self.render_to_response(self.get_context_data())
        # Remove category cookie if exist
        if not request.COOKIES.get('select-category') is None:
            response.set_cookie('select-category', expires=timezone.now() - timezone.timedelta(days=365))

        return response

    def people_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        years = majors = roles = experience = position = hours = []
        if self.post_data:
            if not self.post_data.get('year') is None: years = self.post_data['year']
            if not self.post_data.get('major') is None: majors = self.post_data['major']
            if not self.post_data.get('role') is None: roles = self.post_data['role']
            if not self.post_data.get('experience') is None: experience = self.post_data['experience']
            if not self.post_data.get('position') is None: position = self.post_data['position']
            if not self.post_data.get('hours') is None: hours = self.post_data['hours']
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

        if 'M' in position:
            position.remove('M')
            query['query']['bool']['filter'].append({'term': {'mentor': True}})

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

        query = PeopleDocument.search().from_dict(query)
        # TODO: In some reason query index name is clears
        query._index = s_docs.people_index_name
        return query.execute()

    def startup_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        fields = stage = []
        if self.post_data:
            if not self.post_data.get('fields') is None: fields = self.post_data['fields']
            if not self.post_data.get('stage') is None: stage = self.post_data['stage']
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
        query._index = s_docs.startup_index_name
        return query.execute()

    def job_search(self):
        query_string = self.post_data['query'][0] if self.post_data else ''
        job_category = level = pay = []
        if self.post_data:
            if not self.post_data.get('category') is None: job_category = self.post_data['category']
            if not self.post_data.get('level') is None: level = self.post_data['level']
            if not self.post_data.get('pay') is None: pay = self.post_data['pay']
        self.offset = 0 if self.page == 0 else self.page * self.per_page

        query = {
            'from': self.offset,
            'size': self.per_page,
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'founder.is_filled': True}},
                        {'term': {'founder.user.is_active': True}},
                        {'term': {'founder.user.is_account_disabled': False}},
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
                        'founder.description',
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

        # TODO: In some reason query index name is clears
        query = JobDocument.search().from_dict(query)
        query._index = s_docs.job_index_name
        return query.execute()
