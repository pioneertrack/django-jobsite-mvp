from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from registration.backends.hmac.views import RegistrationView
from django.contrib import messages
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django import forms as f
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib import admin
from django.conf import settings
import numpy as np
import simplejson as json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import itertools
from random import shuffle

from website import forms
from website import models
from website import profile as prof
from . profile import Founder, Job


def merge_dicts(*args):
    dc = {}
    for item in args:
        dc.update(item)
    return dc


stemmer = PorterStemmer()

CONTEXT = {
    'years': prof.YEAR_IN_SCHOOL_CHOICES,
    'majors': prof.MAJORS,
    'roles': prof.PRIMARY_ROLE,
    'fields': prof.CATEGORY,
    'position': prof.POSITION
}

JOB_CONTEXT = {
    'p_context': [
        ('years', list(prof.YEAR_IN_SCHOOL_CHOICES), {'class': 'label-year', 'name': 'year'}),
        ('majors', list(prof.MAJORS), {'class': 'label-major', 'name': 'major'}),
        ('roles', list(prof.PRIMARY_ROLE), {'class': 'label-role', 'name': 'role'}),
        ('position', list(prof.POSITION), {'class': 'label-position'}),
        ('experience', [('0', 'Has startup experience'), ('1', 'Has funding experience')], {'class': 'label-experience'}),
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


# Create your views here.
@csrf_exempt
@login_required(login_url='login/')
def connect(request):
    if request.is_ajax():
        user = get_object_or_404(models.MyUser, pk=request.POST['user'])
        if user is not None:
            user.email_user(
                request.user.first_name + " " + request.user.last_name + " wants to work with you on BearFounders!",
                request.POST['text'] + "\r\nREPLY TO: " + request.user.email, 'noreply@bearfounders.com')
            message = "success"
        else:
            message = 'failure'
    else:
        message = "failure"
    return HttpResponse(message)


@login_required(login_url='login/')
def index(request):
    search_index = {}
    skillset = ['python', 'java', 'c', 'c++', 'c#', 'matlab', 'hadoop', 'mongodb', 'javascript', 'node.js',
                'angular.js', 'react.js', 'meteor.js', 'aws', 'elasticeearch', 'spark', 'go', 'haskell',
                'machine learning',
                'kafka', 'html', 'css', 'word', 'powerpoint', 'ruby', 'rails', 'django', 'flask', 'data', 'd3.js',
                'tensorflow', 'theano', 'redis', 'sql', 'mysql', 'sqlite', 'php', '.net', 'laravel', 'jquery', 'ios',
                'android']
    user = request.user
    if user.first_login:
        messages.success(request, "Welcome to BearFounders! Please update your profile.")
        redirect_url = 'website:profile_update' if user.is_individual else 'website:startup_update'
        return redirect(redirect_url)
    if request.method == 'POST':
        query = request.POST['query']
        phrase = False
        if (query.startswith("'") and query.endswith("'")) or (query.startswith("'") and query.endswith("'")) and len(
                query) > 1:
            phrase = True
        words = stem_remove_stop_words(query.translate({ord(c): None for c in string.punctuation}).lower().split())
        # words = stem_remove_stop_words(nltk.word_tokenize(query))
        roles = request.POST.getlist('roles')
        # if 'NONE' in roles:
        #     roles = roles + ['']
        years = request.POST.getlist('years')
        # if len(years) == 10:
        #     years = years + ['']
        majors = request.POST.getlist('majors')
        fields = request.POST.getlist('fields')
        tokenized_users = []
        if request.POST['select-category'] == 'people':

            kwargs = {}
            kwargs['is_active'] = True
            kwargs['is_founder'] = False

            years = request.POST.getlist('years')
            position = request.POST.getlist('position')
            experience = request.POST.getlist('experience')
            filter_hidden = request.POST.get('filter_people')
            filter = json.loads('[' + filter_hidden + ']')

            active_selects = []

            if len(majors) > 1:
                kwargs['profile__major__in'] = majors
                active_selects.append('majors');
            if len(roles) > 1:
                kwargs['profile__role__in'] = roles
                active_selects.append('roles');
            if len(years) > 1:
                kwargs['profile__year__in'] = years
                active_selects.append('years')
            if len(position) > 1:
                kwargs['profile__position__in'] = position
                active_selects.append('position')
            if len(experience) > 1:
                active_selects.append('experience')
                for item in experience:
                    if item == '1':
                        kwargs['profile__has_funding_exp'] = True
                    elif item == '0':
                        kwargs['profile__has_startup_exp'] = True

            result = models.MyUser.objects.filter(**kwargs)

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
                    skills = [s for s in skillset if s in set(r.profile.skills.lower().replace(',','').split())]
                    to_return.append((user, skills))
            else:
                to_return = list(to_return)
                shuffle(to_return)
            return render(request, 'search.html',
                          merge_dicts(CONTEXT, JOB_CONTEXT,
                                      {
                                          'searched': to_return,
                                          'oldroles': roles,
                                          'oldmajors': majors,
                                          'oldyears': years,
                                          'startup': request.POST.get('startup', False),
                                          'funding': request.POST.get('funding', False),
                                          'posted': True,
                                          'founder': False,
                                          'filter_people': filter,
                                          'people_hidden': filter_hidden,
                                          'search_category': request.POST['select-category'],
                                          'active_selects': active_selects,
                                      }))
        elif request.POST['select-category'] == 'startups':

            kwargs = {}
            kwargs['is_active'] = True
            kwargs['is_founder'] = True
            kwargs['founder__startup_name__gt'] = ''

            filter_hidden = request.POST.get('filter_startups')
            fields = request.POST.getlist('fields')
            stage = request.POST.getlist('stage')

            filter = json.loads('[' + filter_hidden + ']')

            active_selects = []

            if len(fields) > 1:
                active_selects.append('fields')
                kwargs['founder__field__in'] = fields
            if len(stage) > 1:
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
            vals = roles + years + majors
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
                                  'funded': request.POST.get('been_funded', False),
                                  'startup': request.POST.get('startup', False),
                                  'funding': request.POST.get('funding', False),
                                  'posted': False,
                                  'founder': True,
                                  'filter_startups': filter,
                                  'startups_hidden': filter_hidden,
                                  'search_category': request.POST['select-category'],
                                  'active_selects': active_selects,
                              }
                          ))
        elif request.POST['select-category'] == 'jobs':
            tokenized_jobs = []
            kwargs = {}
            category = request.POST.getlist('category')
            level = request.POST.getlist('level')
            pay = request.POST.getlist('pay')
            filter_hidden = request.POST.get('filter_jobs')

            filter = json.loads('[' + filter_hidden + ']')

            active_selects = []

            if len(level) > 1:
                active_selects.append('level')
                kwargs['level__in'] = level
            if len(pay) > 1:
                active_selects.append('pay')
                kwargs['pay__in'] = pay
            if len(category) > 1:
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
                              'search_category': request.POST['select-category'],
                              'oldfields': fields,
                              'funded': request.POST.get('been_funded', False),
                              'startup': request.POST.get('startup', False),
                              'funding': request.POST.get('funding', False),
                              'posted': False,
                              'founder': True,
                              'filter_jobs': filter,
                              'jobs_hidden': filter_hidden,
                              'active_selects': active_selects,
                          }))
    else:
        if user.is_founder:
            return render(request, 'home.html',
                          merge_dicts(CONTEXT, JOB_CONTEXT, {
                              'posted': False,
                              'reset': True,
                          }))
        else:
            return render(request, 'home.html',
                          merge_dicts(CONTEXT, JOB_CONTEXT, {
                              'posted': False,
                              'reset': True,
                          }))


@login_required(login_url='login/')
@user_passes_test(lambda user: user.is_individual, login_url='/')
def user_profile(request):
    last_login = request.user.last_login
    experience = request.user.profile.experience_set.order_by('-end_date')

    # in case user click on fill out later button in profile update
    if request.user.first_login:
        request.user.set_first_login()

    return render(request, 'profile.html',
                  merge_dicts(CONTEXT, JOB_CONTEXT, {
                      'profile': True,
                      'experience': experience,
                      'reset': True,
                      'last_login': last_login,
                  }))


@login_required(login_url='login/')
@user_passes_test(lambda user: user.is_founder, login_url='/')
def startup_profile(request):
    last_login = request.user.last_login
    jobs = request.user.founder.job_set.order_by('created_date')
    total_funding = request.user.founder.funding_set.aggregate(total=Sum('raised'))
    
    # in case user click on fill out later button in profile update
    if request.user.first_login:
        request.user.set_first_login()

    return render(request, 'founder.html',
                  merge_dicts(CONTEXT, JOB_CONTEXT, {
                      'profile': True,
                      'jobs': jobs,
                      'reset': True,
                      'total_funding': total_funding.get('total'),
                      'last_login': last_login,
                  }))


@login_required(login_url='login/')
@user_passes_test(lambda user: user.is_individual, login_url='/')
def profile_update(request):
    user = request.user
    is_first_login = user.first_login

    ExperienceFormSet = inlineformset_factory(prof.Profile, prof.Experience, form=forms.ExperienceForm,
                                              widgets={'start_date': f.DateInput(), 'end_date': f.DateInput()},
                                              error_messages={'start_date': {
                                                  'invalid': 'Please enter a date with the form MM/DD/YY'},
                                                              'end_date': {
                                                                  'invalid': 'Please enter a date with the form MM/DD/YY'}},
                                              max_num=5, extra=1)

    profile_form = forms.ProfileForm(instance=request.user.profile)
    experience_form = ExperienceFormSet(instance=request.user.profile)

    if request.method == 'POST':
        profile_form = forms.ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        experience_form = ExperienceFormSet(request.POST, instance=request.user.profile)
        if profile_form.is_valid() and experience_form.is_valid():
            for k in experience_form.deleted_forms:
                s = k.save(commit=False)
                # messages.success(request, "Removed " +str(s.company) + " from experience")
                s.delete()
            objs = experience_form.save(commit=False)
            for obj in objs:
                # messages.success(request, "Added " +str(obj.company) + " to experience")
                if obj.company != '':
                    obj.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            user.save()

            if user.is_founder and user.first_login:
                return redirect('website:startup_update')

            user.set_first_login()
            return HttpResponseRedirect('/profile')
        else:
            messages.error(request, "There was an error processing your request")

    return render(request, 'profile_form.html',
                  merge_dicts(CONTEXT, JOB_CONTEXT, {
                      'profile_form': profile_form,
                      'experience': experience_form,
                      'show_exp': True,
                      'reset': True,
                      'is_first_login': is_first_login,
                      'next_url': reverse('website:startup_update') if user.is_founder else reverse('website:profile')
                  }))


@login_required(login_url='login/')
@user_passes_test(lambda user: user.is_founder, login_url='/')
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

    startup_form = forms.FounderForm(instance=request.user.founder)
    funding_form = FundingFormSet(instance=request.user.founder)
    job_form = JobFormSet(instance=request.user.founder)

    if request.method == 'POST':
        profile_form = forms.FounderForm(request.POST, request.FILES, instance=request.user.founder)
        funding_form = FundingFormSet(request.POST, instance=request.user.founder)
        job_form = JobFormSet(request.POST, instance=request.user.founder)
        if profile_form.is_valid() and job_form.is_valid() and funding_form.is_valid():
            for k in job_form.deleted_forms:
                s = k.save(commit=False)
                s.delete()
            for l in funding_form.deleted_forms:
                t = l.save(commit=False)
                t.delete()
            objs = job_form.save(commit=False)
            for obj in objs:
                if obj.title != '':
                    obj.save()
            objs2 = funding_form.save(commit=False)
            for obj2 in objs2:
                if obj2.raised > 0:
                    obj2.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            user.save()
            user.set_first_login()
            return redirect('website:startup_profile')
        else:
            messages.error(request, 'There was an error processing your request')

    return render(request, 'profile_form.html',
                  merge_dicts(CONTEXT, JOB_CONTEXT, {
                      'profile_form': startup_form,
                      'funding': funding_form,
                      'jobs': job_form,
                      'show_exp': False,
                      'reset': True,
                      'is_first_login': is_first_login,
                      'next_url': reverse('website:startup_profile')
                  }))


@login_required(login_url='login/')
def get_user_view(request, id):
    user = get_object_or_404(models.MyUser, pk=id)
    last_login = user.last_login
    if user is None:
        return HttpResponseRedirect('/')
    if user.is_founder:
        jobs = user.founder.job_set.order_by('title')
        return render(request, 'founder.html',
                      merge_dicts(CONTEXT, JOB_CONTEXT, {
                          'user': user,
                          'profile': False,
                          'jobs': jobs,
                          'reset': True,
                          'last_login':last_login,
                      }))
    else:
        exp = user.profile.experience_set.order_by('-end_date')
        return render(request, 'profile.html',
                      merge_dicts(CONTEXT, JOB_CONTEXT, {
                          'user': user,
                          'profile': False,
                          'experience': exp,
                          'reset': True,
                          'last_login':last_login,
                      }))


class MyRegistrationView(RegistrationView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(MyRegistrationView, self).dispatch(request, *args, **kwargs)


def google_analytics(request):
    """
    Use the variables returned in this function to
    render your Google Analytics tracking code template.
    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    ga_domain = getattr(settings, 'GOOGLE_ANALYTICS_DOMAIN', False)
    if not settings.DEBUG and ga_prop_id and ga_domain:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': ga_prop_id,
            'GOOGLE_ANALYTICS_DOMAIN': ga_domain,
        }
    return {}

def job_list(request, pk):
    founder = get_object_or_404(Founder, pk=pk)
    jobs = Job.objects.filter(founder=founder).values().order_by('created_date')
    return render(request, 'job_list.html', {'founder': founder, 'jobs':jobs})

