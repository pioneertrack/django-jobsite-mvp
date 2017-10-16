from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.urls import reverse_lazy
from registration.backends.hmac.views import RegistrationView
from django.contrib import messages
from django.utils import timezone
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django import forms as f
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.conf import settings
from django.http import Http404, HttpResponseServerError
import numpy as np
import simplejson as json
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import itertools
from django.core import signing
from random import shuffle
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from smtplib import SMTPException
from urllib.parse import urlparse
import re

from .models import MyUser
from .forms import ResendActivationEmailForm
from website import forms
from website import models
from website import profile as prof
from .profile import Founder, Job
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


from .utils import ValidatePostItems


def merge_dicts(*args):
    dc = {}
    for item in args:
        dc.update(item)
    return dc


stemmer = PorterStemmer()

JOB_CONTEXT = {
    'p_context': [
        ('year', list(prof.YEAR_IN_SCHOOL_CHOICES), {'class': 'label-year', 'name': 'affiliation'}),
        ('major', list(prof.MAJORS), {'class': 'label-major', 'name': 'major'}),
        ('role', list(prof.PRIMARY_ROLE), {'class': 'label-role', 'name': 'role'}),
        ('experience', [('0', 'Has startup experience'), ('1', 'Has funding experience')],
         {'class': 'label-experience'}),
        ('position', [
            ('0', 'Partner'),
            ('1', 'Intern'),
            ('2', 'Part-Time'),
            ('3', 'Full-Time'),
            ('4', 'Freelance')
        ], {'class': 'label-position'}),
        ('hours', list(prof.HOURS_AVAILABLE), {'class': 'label-hours', 'name': 'Available'})
    ],
    'f_context': [
        ('stage', list(prof.STAGE), {'class': 'label-stage'}),
        ('fields', list(prof.CATEGORY), {'class': 'label-field', 'name': 'field'})
    ],
    'job_context': [
        ('category', list(prof.CATEGORY), {'class': 'label-category'}),
        ('level', list(prof.LEVELS), {'class': 'label-level'}),
        ('pay', list(prof.POSITION), {'class': 'label-pay'})
    ]
}


def stem_remove_stop_words(arr):
    return [stemmer.stem(word) for word in arr if word not in stopwords.words('english')]


def term_frequency(word, tokenized_str):
    return tokenized_str.count(word)


def idf_values(tokenized_users, term_index):
    val = {}
    for word in term_index:
        count = sum([1 for x in tokenized_users if word in tokenized_users])
        idf = np.log(len(term_index.keys()) / (count + 1))
        val[word] = idf
    return val


def similarity(word_vector, query_vector):
    return np.dot(np.array([word_vector]).T, np.array([query_vector]))[0][0]


def tf_idf(tokenized_users, query, term_index):
    idf_dict = idf_values([x[1] for x in tokenized_users], term_index)
    all_users_tfidf = []
    for user, tokens in tokenized_users:
        user_tfidf = []
        if len(tokens) == 0:
            continue
        for word in idf_dict.keys():
            freq = term_frequency(word, tokens) / len(tokens)
            user_tfidf.append(freq * idf_dict[word])
        all_users_tfidf.append((user, user_tfidf))
    search_vector = []
    for word in idf_dict.keys():
        freq = term_frequency(word, query) / len(query)
        search_vector.append(freq * idf_dict[word])
    return [tup[0] for tup in sorted(all_users_tfidf, key=lambda x: similarity(x[1], search_vector), reverse=True)]


def check_profiles(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user = request.user
        redirect_url = None
        if user.first_login:
            if user.is_individual and not hasattr(user, 'profile') or user.profile.is_filled == False:
                messages.success(request, "Welcome to BearFounders! Please tell us about yourself.")
                redirect_url = 'website:profile_step'
            elif user.is_founder and not hasattr(user, 'founder') or user.founder.is_filled == False:
                messages.success(request, "Welcome to BearFounders! Please tell us about you startup.")
                redirect_url ='website:profile_step'
        else:
            p = lambda val: not val.profile.is_filled if hasattr(val, 'profile') else True
            f = lambda val: not val.founder.is_filled if hasattr(val, 'founder') else True
            if p(user) and user.is_individual:
                messages.success(request, "Please fill in the information about yourself.")
                redirect_url = 'website:profile_update'
            elif f(user) and user.is_founder:
                messages.success(request, "Please fill in the information about you startup.")
                redirect_url ='website:startup_update'
        if redirect_url is not None:
            return redirect(redirect_url)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func


# Create your views here.
@csrf_exempt
@login_required(login_url='login/')
def connect(request):
    if request.is_ajax():
        url = urlparse(request.META.get('HTTP_REFERER'));
        from_startup = re.match(r'.*/startups/.*', url.path) is not None;
        receiver = get_object_or_404(models.MyUser, pk=request.POST['user_page_id'])
        sender = request.user
        text = request.POST['text']
        if receiver is not None:
            try:
                receiver.email_user(
                    sender.first_name + " " + sender.last_name + " wants to work with you on BearFounders!",
                    request.POST['text'] + "\r\nREPLY TO: " + sender.email, 'noreply@bearfounders.com')
                prof.Connection.objects.create(sender=sender, receiver=receiver, to_startup=from_startup, message=text)
                message = "success"
                return HttpResponse(message)
            except SMTPException as err:
                message = err
        else:
            message = 'failure'
        return HttpResponseServerError(message)
    else:
        raise Http404()


@login_required(login_url='login/')
@check_profiles
@vary_on_headers('User-Agent')
def index(request):
    user = request.user

    return render(request, 'home.html',
                  merge_dicts(JOB_CONTEXT, {
                      'posted': False,
                      'reset': True,
                      'without_padding': True,
                  }))


@login_required(login_url='login/')
@check_profiles
@vary_on_headers('User-Agent', 'X-Session-Header')
def search(request):
    search_index = {}
    skillset = ['python', 'java', 'c', 'c++', 'c#', 'matlab', 'hadoop', 'mongodb', 'javascript', 'node.js',
                'angular.js', 'react.js', 'meteor.js', 'aws', 'elasticeearch', 'spark', 'go', 'haskell',
                'machine learning',
                'kafka', 'html', 'css', 'word', 'powerpoint', 'ruby', 'rails', 'django', 'flask', 'data', 'd3.js',
                'tensorflow', 'theano', 'redis', 'sql', 'mysql', 'sqlite', 'php', '.net', 'laravel', 'jquery', 'ios',
                'android']

    post = request.method == 'POST'
    select_category = request.COOKIES.get('select-category')

    query = ''
    tokenized_users = []
    if post:
        request.session['post_search_data'] = json.dumps(dict(request.POST))
        request.session['post_filter_people'] = request.POST['filter_people']
        request.session['post_filter_jobs'] = request.POST['filter_jobs']
        request.session['post_filter_startups'] = request.POST['filter_startups']

        response = HttpResponseRedirect(reverse('website:search'))
        return response
    else:
        post_data = json.loads(request.session.get('post_search_data')) if select_category == 'None' else None
        if post_data:
            select_category = post_data['select-category'][0]
            query = post_data['query'][0]

    phrase = False
    if (query.startswith("'") and query.endswith("'")) or (query.startswith("'") and query.endswith("'")) and len(
            query) > 1:
        phrase = True
    words = stem_remove_stop_words(query.translate({ord(c): None for c in string.punctuation}).lower().split())

    if select_category == 'people':

        kwargs = {'is_active': True, 'is_individual': True, 'is_account_disabled': False,
                  'profile__is_filled': True }

        years = majors = roles = filter = filter_hidden = active_selects = filter_mobile = None
        if post_data:
            active_selects = []
            filter_hidden = request.session.get('post_filter_people')

            years = post_data['year']
            majors = post_data['major']
            roles = post_data['role']
            experience = post_data['experience']
            position = post_data['position']
            hours = post_data['hours']

            filter = None
            if filter_hidden != None:
                filter = json.loads('[' + filter_hidden + ']')

            filter_mobile = {
                'year': years,
                'major': majors,
                'role': roles,
                'experience': experience,
                'position': position,
                'hours': hours
            }

            if len(years) > 1 or (not '' in years and len(years) > 0):
                kwargs['profile__year__in'] = years
                active_selects.append('year')
            if len(majors) > 1 or (not '' in majors and len(majors) > 0):
                kwargs['profile__major__in'] = majors
                active_selects.append('major')
            if len(roles) > 1 or (not '' in roles and len(roles) > 0):
                kwargs['profile__role__in'] = roles
                active_selects.append('role')
            if len(position) > 1 or (not '' in position and len(position) > 0):
                kwargs['profile__positions__overlap'] = position
                active_selects.append('position')
            if len(hours) > 1 or (not '' in hours and len(hours) > 0):
                kwargs['profile__hours_week__in'] = hours
                active_selects.append('hours')
            if len(experience) > 1 or (not '' in experience and len(experience) > 0):
                active_selects.append('experience')
                for item in experience:
                    if item == '1':
                        kwargs['profile__has_funding_exp'] = True
                    elif item == '0':
                        kwargs['profile__has_startup_exp'] = True

        result = models.MyUser.objects.filter(**kwargs).exclude(profile__positions__exact=['5'])

        for r in result:
            experience = [stem_remove_stop_words(arr) for arr in [
                x.description.lower().replace('\n', ' ').replace('\r', '').translate(
                    {ord(c): None for c in string.punctuation}).split() for x in r.profile.experience_set.all()]]
            attr = [stem_remove_stop_words(arr) for arr in [
                x.lower().replace('\n', ' ').replace('\r', '').translate(
                    {ord(c): None for c in string.punctuation}).split() for x in
                [r.first_name + " " + r.last_name, r.profile.get_major_display(), r.profile.bio, r.profile.skills,
                 r.profile.interests, r.profile.courses]]]
            total = list(itertools.chain.from_iterable(attr + experience))
            for i, word in enumerate(total):
                if word in search_index:
                    seen = False
                    for k in search_index.get(word):
                        if k[0] == r.id:
                            k[1].append(i)
                            seen = True
                            break
                    if not seen:
                        search_index.get(word).append([r.id, [i]])
                else:
                    search_index[word] = [[r.id, [i]]]
            # TODO: Remember normal alg for that
            positions = []
            for item in r.profile.positions:
                positions.append(prof.POSITIONS.__getitem__(int(item))[1])
            r.positions_display = positions;
        to_return = set()
        if len(words) == 0:
            count = 0
            for r in result:
                if count > 100:
                    break
                skills = tuple([s for s in skillset if s in set(r.profile.skills.lower().replace(',', '').split())])
                to_return.add((r, skills))
                count += 1
        elif len(words) == 1:
            if words[0] in search_index:
                valid_users = set([k[0] for k in search_index[words[0]]])
                for r in result:
                    if r.id in valid_users:
                        skills = tuple(
                            [s for s in skillset if s in set(r.profile.skills.lower().replace(',', '').split())])
                        to_return.add((r, skills))
        elif len(words) > 1:
            for word in words:
                if word in search_index:
                    valid_users = set([k[0] for k in search_index[word]])
                    for r in result:
                        if r.id in valid_users:
                            skills = tuple([s for s in skillset if
                                            s in set(r.profile.skills.lower().replace(',', '').split())])
                            to_return.add((r, skills))
        if len(words) > 0:
            for user, skills in list(to_return):
                experience = [stem_remove_stop_words(arr) for arr in [
                    x.description.lower().replace('\n', ' ').replace('\r', '').translate(
                        {ord(c): None for c in string.punctuation}).split() for x in
                    user.profile.experience_set.all()]]
                attr = [stem_remove_stop_words(arr) for arr in [
                    x.lower().replace('\n', ' ').replace('\r', '').translate(
                        {ord(c): None for c in string.punctuation}).split() for x in
                    [user.first_name + " " + user.last_name, user.profile.get_major_display(), user.profile.bio,
                     user.profile.skills, user.profile.interests, user.profile.courses]]]
                total = list(itertools.chain.from_iterable(attr + experience))
                tokenized_users.append((user, total))
            to_return = []
            for user in tf_idf(tokenized_users, words, search_index):
                skills = [s for s in skillset if s in set(r.profile.skills.lower().replace(',', '').split())]
                to_return.append((user, skills))
        else:
            to_return = list(to_return)
            shuffle(to_return)
        return render(request, 'search.html',
                      merge_dicts(JOB_CONTEXT,
                                  {
                                      'search_enabled': True,
                                      'searched': to_return,
                                      'oldroles': roles,
                                      'oldmajors': majors,
                                      'oldyears': years,
                                      'posted': True,
                                      'founder': False,
                                      'filter_people': filter,
                                      'people_hidden': filter_hidden,
                                      'search_category': select_category,
                                      'active_selects': active_selects,
                                      'mobile_filter': filter_mobile,
                                  }))
    elif select_category == 'startups':

        kwargs = {
            'is_active': True,
            'is_founder': True,
            'is_account_disabled': False,
            'founder__is_filled': True,
            'founder__startup_name__gt': '',
        }

        fields = active_selects = filter = filter_hidden = filter_mobile = None
        if post_data:
            active_selects = []
            filter_hidden = request.session.get('post_filter_startups')
            fields = post_data['fields']
            stage = post_data['stage']

            filter_mobile = {
                'fields': fields,
                'stage': stage,
            }
            filter = None
            if filter_hidden != None:
                filter = json.loads('[' + filter_hidden + ']')


            if len(fields) > 1 or (not '' in fields and len(fields) > 0):
                active_selects.append('fields')
                kwargs['founder__field__in'] = fields
            if len(stage) > 1 or (not '' in stage and len(stage) > 0):
                active_selects.append('stage')
                kwargs['founder__stage__in'] = stage

        result = models.MyUser.objects.filter(**kwargs)
        for r in result:
            jobs = [stem_remove_stop_words(arr) for arr in [
                " ".join([x.description, x.title, x.get_level_display(), x.get_pay_display()]).lower().replace('\n',
                                                                                                               ' ').replace(
                    '\r', '').translate({ord(c): None for c in string.punctuation}).split() for x in
                r.founder.job_set.all()]]
            attr = [stem_remove_stop_words(arr) for arr in [
                x.lower().replace('\n', ' ').replace('\r', '').translate(
                    {ord(c): None for c in string.punctuation}).split() for x in
                [r.first_name + " " + r.last_name, r.founder.startup_name, r.founder.description]]]
            total = list(itertools.chain.from_iterable(jobs + attr))
            for i, word in enumerate(total):
                if word in search_index:
                    seen = False
                    for k in search_index.get(word):
                        if k[0] == r.id:
                            k[1].append(i)
                            seen = True
                            break
                    if not seen:
                        search_index.get(word).append([r.id, [i]])
                else:
                    search_index[word] = [[r.id, [i]]]
        to_return = set()
        if len(words) == 0:
            count = 0
            for r in result:
                if count > 100:
                    break
                to_return.add((r, None))
                count += 1
            to_return = list(to_return)
            shuffle(to_return)
        elif len(words) == 1:
            if words[0] in search_index:
                valid_users = set([k[0] for k in search_index[words[0]]])
                for r in result:
                    if r.id in valid_users:
                        to_return.add((r, None))
        elif len(words) > 1:
            for word in words:
                if word in search_index:
                    valid_users = set([k[0] for k in search_index[word]])
                    for r in result:
                        if r.id in valid_users:
                            to_return.add((r, None))
        # vals = roles + years + majors
        if len(words) > 0:
            for user, skills in list(to_return):
                jobs = [stem_remove_stop_words(arr) for arr in [
                    " ".join([x.description, x.title, x.get_level_display(), x.get_pay_display()]).lower().replace(
                        '\n', ' ').replace('\r', '').translate({ord(c): None for c in string.punctuation}).split()
                    for x in user.founder.job_set.all()]]
                attr = [stem_remove_stop_words(arr) for arr in [
                    x.lower().replace('\n', ' ').replace('\r', '').translate(
                        {ord(c): None for c in string.punctuation}).split() for x in
                    [user.first_name + " " + user.last_name, user.founder.startup_name, user.founder.description]]]
                total = list(itertools.chain.from_iterable(jobs + attr))
                tokenized_users.append((user, total))
            to_return = [(x, None) for x in tf_idf(tokenized_users, words, search_index)]
        else:
            to_return = list(to_return)
            shuffle(to_return)

        return render(request, 'search.html',
                      merge_dicts(JOB_CONTEXT,
                                  {
                                      'searched': to_return,
                                      'oldfields': fields,
                                      'posted': False,
                                      'founder': True,
                                      'filter_startups': filter,
                                      'startups_hidden': filter_hidden,
                                      'search_category': select_category,
                                      'active_selects': active_selects,
                                      'mobile_filter': filter_mobile
                                  }
                                  ))
    elif select_category == 'jobs':
        tokenized_jobs = []
        kwargs = {
            'founder__user__is_account_disabled': False,
            'founder__is_filled': True,
        }

        category = level = pay = active_selects = filter = filter_hidden = filter_mobile = None
        if post_data:
            active_selects = []
            category = post_data['category']
            level = post_data['level']
            pay = post_data['pay']
            filter_hidden = request.session.get('post_filter_jobs')

            filter = None
            if filter_hidden != None:
                filter = json.loads('[' + filter_hidden + ']')

            filter_mobile = {
                'category': category,
                'level': level,
                'pay': pay,
            }

            if len(level) > 1 or (not '' in level and len(level) > 0):
                active_selects.append('level')
                kwargs['level__in'] = level
            if len(pay) > 1 or (not '' in pay and len(pay) > 0):
                active_selects.append('pay')
                kwargs['pay__in'] = pay
            if len(category) > 1 or (not '' in category and len(category) > 0):
                active_selects.append('category')
                kwargs['founder__field__in'] = category

        result = prof.Job.objects.filter(**kwargs)
        for r in result:
            attr = [stem_remove_stop_words(arr) for arr in
                    [x.lower().replace('\n', ' ').replace('\r', '').translate(
                        {ord(c): None for c in string.punctuation}).split() for x in
                     [r.founder.startup_name, r.founder.description, r.title, r.description]]]
            attr = list(itertools.chain.from_iterable(attr))
            for i, word in enumerate(attr):
                if word in search_index:
                    seen = False
                    for k in search_index.get(word):
                        if k[0] == r.id:
                            k[1].append(i)
                            seen = True
                            break
                    if not seen:
                        search_index.get(word).append([r.id, [i]])
                else:
                    search_index[word] = [[r.id, [i]]]

        to_return = set();
        if len(words) == 0:
            count = 0
            for r in result:
                if count > 100:
                    break
                to_return.add((r, None))
                count += 1
            to_return = list(to_return)
            shuffle(to_return)
        elif len(words) == 1:
            if words[0] in search_index:
                valid_users = set([k[0] for k in search_index[words[0]]])
                for r in result:
                    if r.id in valid_users:
                        to_return.add((r, None))
        elif len(words) > 1:
            for word in words:
                if word in search_index:
                    valid_users = set([k[0] for k in search_index[word]])
                    for r in result:
                        if r.id in valid_users:
                            to_return.add((r, None))
        if len(words) > 0:
            for job in list(to_return):
                attr = [stem_remove_stop_words(arr) for arr in
                        [x.lower().replace('\n', ' ').replace('\r', '').translate(
                            {ord(c): None for c in string.punctuation}).split() for x in
                         [r.founder.startup_name, r.founder.description, r.title, r.description]]]
                attr = list(itertools.chain.from_iterable(attr))
                tokenized_jobs.append((job, attr))
            to_return = tf_idf(tokenized_jobs, words, search_index)
        else:
            to_return = list(to_return)
            shuffle(to_return)

        return render(request, 'search.html',
                      merge_dicts(JOB_CONTEXT, {
                          'searched': to_return,
                          'search_category': select_category,
                          'posted': False,
                          'founder': True,
                          'filter_jobs': filter,
                          'jobs_hidden': filter_hidden,
                          'active_selects': active_selects,
                          'mobile_filter': filter_mobile
                      }))
    else:
        return render(request, 'search.html',
                      merge_dicts(JOB_CONTEXT, {
                          'posted': False,
                          'reset': True,
                      }))


@login_required
@check_profiles
@never_cache
def user_profile(request):
    last_login = request.user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    experience = request.user.profile.experience_set.order_by('-end_date')

    # in case user click on fill out later button in profile update
    # if request.user.first_login:
    #     request.user.set_first_login()

    # TODO: need to remember normal alg for that
    positions = []
    for item in request.user.profile.positions:
        positions.append(prof.POSITIONS.__getitem__(int(item))[1])

    return render(request, 'profile.html', merge_dicts(JOB_CONTEXT , {
                      'profile': True,
                      'experience': experience,
                      'reset': True,
                      'last_login': last_login,
                      'positions_display': positions,
                      'cd': cd,
                  }))


@login_required
@check_profiles
@never_cache
def startup_profile(request):
    user = get_object_or_404(models.MyUser, pk=request.user.id)
    last_login = user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    jobs = request.user.founder.job_set.order_by('created_date')
    total_funding = request.user.founder.funding_set.aggregate(total=Sum('raised'))

    # in case user click on fill out later button in profile update
    # if request.user.first_login:
    #     request.user.set_first_login()

    return render(request, 'founder.html', merge_dicts(JOB_CONTEXT, {
                      'profile': True,
                      'jobs': jobs,
                      'reset': True,
                      'total_funding': total_funding.get('total'),
                      'last_login': last_login,
                      'cd': cd,
                  }))


@login_required
@never_cache
def profile_update(request):
    user = request.user
    is_first_login = user.first_login

    ExperienceFormSet = inlineformset_factory(prof.Profile, prof.Experience, form=forms.ExperienceForm,
                                              widgets={
                                                  'start_date': f.DateInput(format='%m/%d/%y'),
                                                  'end_date': f.DateInput(format='%m/%d/%y'),
                                              },
                                              error_messages={
                                                  'start_date': {
                                                      'invalid': 'Please enter a date with the form MM/DD/YY'},
                                                  'end_date': {
                                                      'invalid': 'Please enter a date with the form MM/DD/YY'}
                                              },
                                              max_num=5, extra=1)

    profile = None if not hasattr(user, 'profile') else user.profile
    profile_form = forms.ProfileForm(instance=profile)
    experience_form = ExperienceFormSet(instance=profile)

    if request.method == 'POST':
        profile_form = forms.ProfileForm(request.POST, request.FILES, instance=profile)
        experience_form = ExperienceFormSet(request.POST, instance=profile)

        alt_email = profile_form["alt_email"]
        if user.email == alt_email:
            profile_form._errors["alt_email"] = ["Account for email address is not registered or already activated."]

        if profile_form.is_valid() and experience_form.is_valid():
            profile = profile_form.save(commit=False)
            if not hasattr(profile, 'user'):
                profile.user = user
            profile.save()

            for k in experience_form.deleted_forms:
                s = k.save(commit=False)
                s.delete()
            objs = experience_form.save(commit=False)
            for obj in objs:
                if obj.company != '':
                    obj.profile = profile
                    obj.save()

            if not user.is_individual:
                user.is_individual = True
                user.save()

            profile.check_is_filled()

            if user.is_founder and user.first_login:
                messages.success(request, "Welcome to BearFounders! Please tell us about you startup.")
                return redirect('website:startup_update')

            messages.success(request, 'Your profile was successfully updated!')
            user.set_first_login()
            return redirect('website:profile')
        else:
            print(profile_form.errors, experience_form.errors)
            messages.error(request, "There was an error processing your request")

    return render(request, 'profile_form.html', merge_dicts(JOB_CONTEXT, {
                      'profile_form': profile_form,
                      'experience': experience_form,
                      'show_exp': True,
                      'reset': True,
                      'title': 'Update your profile',
                      'is_first_login': is_first_login,
                      'profile_edit': True,
                      'next_url': reverse('website:startup_update') if user.is_founder else reverse('website:profile')
                  }))

@login_required
def profile_breadcrumbs_update_step(request, updatedStep):

    profile = None if not hasattr(request.user, 'profile') else request.user.profile
    # if profile == None or int(profile.profile_step) < int(updatedStep):
    #     return JsonResponse({"success" : False, "error" : "No profile on this account"})

    # profile.profile_step = int(updatedStep)
    # print (updatedStep)
    # profile.save()

    request.session['userstep'] = str(updatedStep)
    return JsonResponse({'success': True})

@login_required
@csrf_exempt
def profile_step_image(request):
    user = request.user

    if request.method == "POST":
        if request.FILES and request.FILES.get('profileimage'):
            profile = None if not hasattr(user, 'profile') else user.profile

            if profile:
                profile.image= request.FILES.get('profileimage')
                profile.save()
            else:
                profile = prof.Profile.objects.create(user=user, positions=["5"], image=request.FILES["profileimage"])
                profile.save()
                user.profile = profile
                user.save()



    return JsonResponse({'success': True})

@login_required
def profile_step(request):
    formDat = {}
    errors = []
    formDat["hours_available"] = prof.HOURS_AVAILABLE
    formDat["primary_majors"] = prof.MAJORS
    formDat["position_types"] = prof.POSITIONS
    formDat["primary_roles"] = prof.PRIMARY_ROLE
    formDat["cal_affiliation"] = prof.YEAR_IN_SCHOOL_CHOICES
    formDat["startup_history"] = (
        ("has_startup_exp", "I have worked at a startup before"),
        ("has_funding_exp", "I have experience funding a startup")
    )
    formDat["hasStartup"] = (("yes", 'Yes'), ("no" , 'No'))
    if request.method == "POST":
        user = request.user
        profile = None if not hasattr(user, 'profile') else user.profile

        if not profile:
            errors.append({"Need Image" : "Please go to step 1 and re add your profile image"})
        else:

            expected = {"primaryroles" : "role",
                     "skills" : "skills",
                       "major" : "major",
                       "bio" : "bio",
                       "numberhoursinput" : "hours_week",
                       "linkedin" : "linkedin",
                       "relcoursework" : "courses",
                       "calaffiliation" : "year",
                       "githuburl" : "github",
                       "personalwebsite" : "website",
                       "interests" : "interests",

                        }
            checkboxes = {"positions_check[]" : "positions"}
            optional = {}
            # print (expected)
            try:
                ValidatePostItems(expectedFields=expected, optionalFields=optional, request=request, checkboxes=checkboxes, saveObj = profile)
                profile.is_filled=True
                print (request.POST["startupProfile"])
                profile.save()
                if request.POST["startupProfile"] == "no":
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect('/startup/update')


            except Exception as e:
                errors.append({"strong" : "missing fields!", "text" : "please fill out all required fields!"})


    return render(request, 'profile_steps.html', merge_dicts(JOB_CONTEXT, {"formDat" : formDat, "errors" : errors}))


@login_required
@never_cache
def startup_update(request):
    user = request.user
    is_first_login = user.first_login

    FundingFormSet = inlineformset_factory(prof.Founder, prof.Funding, form=forms.FundingForm,
                                           error_messages={
                                               'raised': {'invalid': 'Please enter an amount greater than 0'}},
                                           labels={'stage': 'Funding round', 'raised': 'Amount raised'}, max_num=5,
                                           extra=1)
    JobFormSet = inlineformset_factory(prof.Founder, prof.Job, form=forms.JobForm,
                                       labels={'level': 'Job position', 'title': 'Job title', 'pay': 'Job pay',
                                               'description': 'Job description'}, max_num=5, extra=1)

    founder = None if not hasattr(user, 'founder') else user.founder
    startup_form = forms.FounderForm(instance=founder)
    funding_form = FundingFormSet(instance=founder)
    job_form = JobFormSet(instance=founder)

    if request.method == 'POST':
        profile_form = forms.FounderForm(request.POST, request.FILES, instance=founder)
        funding_form = FundingFormSet(request.POST, instance=founder)
        job_form = JobFormSet(request.POST, instance=founder)
        if profile_form.is_valid() and job_form.is_valid() and funding_form.is_valid():
            founder = profile_form.save(commit=False)
            if not hasattr(founder, 'user'):
                founder.user = user
            founder.save()
            if not user.is_founder:
                user.is_founder = True
                user.save()

            for k in job_form.deleted_forms:
                s = k.save(commit=False)
                s.delete()
            for l in funding_form.deleted_forms:
                t = l.save(commit=False)
                t.delete()
            objs = job_form.save(commit=False)
            for obj in objs:
                print(obj.__dict__)
                if obj.title != '':
                    obj.save()
            objs2 = funding_form.save(commit=False)
            for obj2 in objs2:
                if obj2.raised > 0:
                    obj2.save()

            founder.check_is_filled()
            messages.success(request, 'Your startup profile was successfully updated!')
            user.set_first_login()
            return redirect('website:startup_profile')
        else:
            messages.error(request, 'There was an error processing your request')

    return render(request, 'profile_form.html', merge_dicts(JOB_CONTEXT ,{
                      'profile_form': startup_form,
                      'funding': funding_form,
                      'jobs': job_form,
                      'show_exp': False,
                      'reset': True,
                      'is_first_login': is_first_login,
                      'title': 'Update Startup',
                      'profile_edit': True,
                      'next_url': reverse('website:startup_profile')
                  }))


@login_required
@check_profiles
def get_profile_view(request, id):
    user = get_object_or_404(models.MyUser, pk=id)
    last_login = user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    if user is None:
        return HttpResponseRedirect('/')
    # TODO: need to remember normal alg for that
    positions = []
    for item in user.profile.positions:
        positions.append(prof.POSITIONS.__getitem__(int(item))[1])
    exp = user.profile.experience_set.order_by('-end_date')
    return render(request, 'profile_info.html', merge_dicts(JOB_CONTEXT, {
                      'profile': user.profile,
                      'experience': exp,
                      'reset': True,
                      'last_login': last_login,
                      'positions_display': positions,
                      'cd': cd,
                  }))


@login_required
@check_profiles
def get_startup_view(request, id):
    user = get_object_or_404(models.MyUser, pk=id)
    last_login = user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    if user is None:
        return HttpResponseRedirect('/')
    jobs = user.founder.job_set.order_by('title')
    return render(request, 'founder_info.html', merge_dicts(JOB_CONTEXT, {
                      'founder': user.founder,
                      'profile': False,
                      'jobs': jobs,
                      'reset': True,
                      'last_login': last_login,
                      'cd': cd,
                  }))

@method_decorator(never_cache, name='dispatch')
class MyRegistrationView(RegistrationView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(MyRegistrationView, self).dispatch(request, *args, **kwargs)


@never_cache
def resend_activation_email(request):
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'

    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')

    context = Context()

    form = None
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = MyUser.objects.filter(email=email, is_active=0)

            if not users.count():
                form._errors["email"] = ["Account for email address is not registered or already activated."]

            REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')
            for user in users:
                activation_key = signing.dumps(
                    obj=getattr(user, user.USERNAME_FIELD),
                    salt=REGISTRATION_SALT,
                )
                context = {}
                context['activation_key'] = activation_key
                context['expiration_days'] = settings.ACCOUNT_ACTIVATION_DAYS
                context['site'] = get_current_site(request)

                subject = render_to_string(email_subject_template,
                                           context)
                # Force subject to a single line to avoid header-injection
                # issues.
                subject = ''.join(subject.splitlines())
                message = render_to_string(email_body_template,
                                           context)
                user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
                return render(request, 'registration/resend_activation_email_done.html')

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form": form})
    return render(request, 'registration/resend_activation_email_form.html', context)


def job_list(request, pk):
    founder = get_object_or_404(Founder, pk=pk)
    jobs = Job.objects.filter(founder=founder).values().order_by('created_date')
    return render(request, 'job_list.html', {'founder': founder, 'jobs': jobs})


@method_decorator(never_cache, name='dispatch')
class Settings(LoginRequiredMixin, generic.FormView):
    success_url = reverse_lazy('website:settings')
    form_class = forms.ChangePasswordForm
    # alternate_email_form_class = forms.ChangeAlternateEmailForm
    template_name = 'settings.html'

    def get_form_kwargs(self):
        kwargs = super(Settings, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Settings, self).get_context_data(**kwargs)
        # if self.request.user.is_individual and hasattr(self.request.user, 'profile'):
        #     context['alternate_email_form'] = self.alternate_email_form_class(
        #         initial={'alt_email': self.request.user.profile.alt_email})
        # context.update(**CONTEXT)
        context.update(**JOB_CONTEXT)
        return context

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password updated')
        return super(Settings, self).form_valid(form)


# class ChangeAlternateEmail(Settings, UserPassesTestMixin):
#     form_class = forms.ChangeAlternateEmailForm
#     http_method_names = ['post']
#
#     def test_func(self):
#         return self.request.user.is_individual
#
#     def get_form_kwargs(self):
#         kwargs = super(Settings, self).get_form_kwargs()
#         kwargs['instance'] = self.request.user.profile
#         return kwargs
#
#     def form_valid(self, form):
#         form.save()
#         messages.success(self.request, 'Alternate email updated')
#         return redirect(self.get_success_url())


@method_decorator(never_cache, name='dispatch')
class ChangeAccountStatus(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy('website:settings')

    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_account_disabled = True if kwargs.get('status') == 'disable' else False
        user.save()
        messages.success(request, 'Your account has been {}d'.format(kwargs.get('status')))
        return super(ChangeAccountStatus, self).post(request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class DeleteProfile(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy('website:settings')

    def post(self, request, *args, **kwargs):
        user = request.user
        selected_account = request.POST.get('selected_account')
        if selected_account == 'personal':
            user.profile.delete()
            user.is_individual = False
        if selected_account == 'startup':
            user.founder.delete()
            user.is_founder = False

        user.save()
        messages.success(request, 'Your {} profile has been deleted'.format(selected_account.capitalize()))
        return super(DeleteProfile, self).post(request, *args, **kwargs)


def test_mail(request):
    user = request.user
    message = render_to_string('email/user_profile_incomplete.txt', {'profile': user.profile})
    user.email_user('You personal profile is incomplete', message, 'noreply@bearfounders.com')
    message = render_to_string('email/startup_profile_incomplete.txt', {'profile': user.profile})
    user.email_user('You startup profile is incomplete', message, 'noreply@bearfounders.com')
    return HttpResponseRedirect('/')
