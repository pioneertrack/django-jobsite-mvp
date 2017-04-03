from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from registration.backends.hmac.views import RegistrationView
from django.contrib import messages
from django.forms.models import inlineformset_factory
from django import forms as f
from django.views.decorators.csrf import csrf_exempt


import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import itertools
from random import shuffle

from website import forms
from website import models
from website import profile as prof
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
stemmer = PorterStemmer()
CONTEXT = {
    'years': prof.Profile.YEAR_IN_SCHOOL_CHOICES,
    'majors': prof.Profile.MAJORS,
    'roles': prof.Profile.PRIMARY_ROLE,
    'fields': prof.Founder.CATEGORY,
    'position': prof.POSITION
}
def stem_remove_stop_words(arr):
    return [stemmer.stem(word) for word in arr if word not in stopwords.words('english')]
# Create your views here.
@csrf_exempt
@login_required(login_url='login/')
def connect(request):
    if request.is_ajax():
        user = get_object_or_404(models.MyUser, pk = request.POST['user'])
        if user is not None:
            user.email_user(request.user.first_name + " " + request.user.last_name + " wants to work with you on BearFounders!", request.POST['text'] + "\r\nREPLY TO: "+request.user.email, 'noreply@bearfounders.com')
            message = "success"
        else:
            message='failure'
    else:
        message = "failure"
    return HttpResponse(message)
@login_required(login_url='login/')
def index(request):
    search_index = {}
    skillset = ['python', 'java', 'c', 'c++', 'c#', 'matlab', 'hadoop', 'mongodb', 'javascript', 'node.js', 'angular.js', 'react.js', 'meteor.js', 'aws', 'elasticeearch', 'spark', 'go', 'haskell', 'machine learning',
            'kafka', 'html', 'css', 'word', 'powerpoint', 'ruby', 'rails', 'django', 'flask', 'data', 'd3.js', 'tensorflow', 'theano', 'redis', 'sql', 'mysql', 'sqlite', 'php', '.net', 'laravel', 'jquery', 'ios', 'android']
    user = request.user
    if user.first_login:
        messages.success(request, "Welcome to BearFounders! Please update your profile.")
        return HttpResponseRedirect('/profile/update')
    if request.method == 'POST':
        query = request.POST['query']
        phrase = False
        if (query.startswith("'") and query.endswith("'")) or (query.startswith("'") and query.endswith("'")) and len(query) > 1:
            phrase = True
        words= stem_remove_stop_words(query.translate({ord(c): None for c in string.punctuation}).lower().split())
        # words = stem_remove_stop_words(nltk.word_tokenize(query))
        roles = request.POST.getlist('role') + ['']
        years = request.POST.getlist('year') +['']
        majors = request.POST.getlist('major')
        fields = request.POST.getlist('field') + ['']
        pos = request.POST.getlist('pos') + ['']
        if request.POST['select-category'] == 'people':
            if request.POST.get('startup', False) and request.POST.get('funding', False):
                result = models.MyUser.objects.filter(is_active=True, is_founder = False, profile__major__in=majors, profile__role__in=roles, profile__year__in=years, profile__has_funding_exp = True, profile__has_startup_exp = True, profile__position__in=pos)
            elif request.POST.get('startup', False):
                result = models.MyUser.objects.filter(is_active=True, is_founder = False, profile__major__in=majors, profile__role__in=roles, profile__year__in=years, profile__has_startup_exp = True, profile__position__in=pos)
            elif request.POST.get('funding', False):
                result = models.MyUser.objects.filter(is_active=True, is_founder = False, profile__major__in=majors, profile__role__in=roles, profile__year__in=years, profile__has_funding_exp = True, profile__position__in=pos)
            else:
                result = models.MyUser.objects.filter(is_active=True, is_founder = False, profile__major__in=majors, profile__role__in=roles, profile__year__in=years, profile__position__in=pos)
            for r in result:
                experience = [stem_remove_stop_words(arr) for arr in [x.description.lower().replace('\n', ' ').replace('\r', '').translate({ord(c): None for c in string.punctuation}).split() for x in r.profile.experience_set.all()]]
                attr = [stem_remove_stop_words(arr) for arr in [x.lower().replace('\n', ' ').replace('\r', '').translate({ord(c): None for c in string.punctuation}).split() for x in [r.first_name+" " +r.last_name, str(r.profile.get_major_display), r.profile.bio, r.profile.skills, r.profile.interests, r.profile.courses]]]
                total = list(itertools.chain.from_iterable(attr+experience))
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
                    skills = tuple([s for s in skillset if s in set(r.profile.skills.lower().replace(',','').split())])
                    to_return.add((r, skills))
                    count += 1
                to_return = list(to_return)
                shuffle(to_return)
            elif len(words) == 1:
                if words[0] in search_index:
                    valid_users = set([k[0] for k in search_index[words[0]]])
                    for r in result:
                        if r.id in valid_users:
                            skills = tuple([s for s in skillset if s in set(r.profile.skills.lower().replace(',','').split())])
                            to_return.add((r, skills))
            elif len(words) > 1:
                for word in words:
                    if word in search_index:
                        valid_users = set([k[0] for k in search_index[word]])
                        for r in result:
                            if r.id in valid_users:
                                skills = tuple([s for s in skillset if s in set(r.profile.skills.lower().replace(',','').split())])
                                to_return.add((r, skills))
            vals = roles + years + majors
            return render(request, 'search.html', merge_two_dicts(CONTEXT, {
                'searched': to_return,
                'oldvals': vals,
                'startup': request.POST.get('startup', False),
                'funding': request.POST.get('funding', False),
                'posted': True,
                'founder': False,
            }))
        else:
            result = models.MyUser.objects.filter(is_active = True, is_founder=True, founder__field__in=fields, founder__startup_name__gt='')
            for r in result:
                jobs = [stem_remove_stop_words(arr) for arr in [" ".join([x.description, x.title, str(x.get_level_display), str(x.get_pay_display)]).lower().replace('\n', ' ').replace('\r', '').translate({ord(c): None for c in string.punctuation}).split() for x in r.founder.job_set.all()]]
                attr = [stem_remove_stop_words(arr) for arr in [x.lower().replace('\n', ' ').replace('\r', '').translate({ord(c): None for c in string.punctuation}).split() for x in [r.first_name+" " +r.last_name, r.founder.startup_name, r.founder.description]]]
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
            return render(request, 'search.html', merge_two_dicts(CONTEXT, {
                'searched': to_return,
                'oldvals': vals,
                'posted': False,
                'founder': True,
            }))
    else:
        if user.is_founder:
            return render(request, 'home.html', merge_two_dicts(CONTEXT, {
                'posted': False
            }))
        else:
            return render(request, 'home.html', merge_two_dicts(CONTEXT, {
                'posted': False
            }))
@login_required(login_url='login/')
def profile(request):
    if request.user.is_founder:
        jobs = request.user.founder.job_set.order_by('title')
        return render(request, 'founder.html', merge_two_dicts(CONTEXT,{'profile': True, 'jobs': jobs}))
    experience = request.user.profile.experience_set.order_by('-start_date')
    return render(request, 'profile.html', merge_two_dicts(CONTEXT, {'profile': True, 'experience': experience}))
@login_required(login_url='login/')
def profile_update(request):
    user = request.user
    ExperienceFormSet = inlineformset_factory(prof.Profile, prof.Experience, form=forms.ExperienceForm,
        widgets={'start_date': f.DateInput(), 'end_date': f.DateInput()},
        error_messages={'start_date': {'invalid':'Please enter a date with the form MM/DD/YY'}, 'end_date': {'invalid':'Please enter a date with the form MM/DD/YY'}}, max_num=5, extra=1)
    JobFormSet = inlineformset_factory(prof.Founder, prof.Job, form=forms.JobForm, labels={'level': 'Job position', 'title': 'Job title', 'pay': 'Job pay', 'description': 'Job description'}, max_num=5, extra=1)
    if user.first_login:
        user.set_first_login()
    if not user.is_founder and request.method == 'POST':
        profile_form = forms.ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        experience_form = ExperienceFormSet(request.POST, instance=request.user.profile)
        if profile_form.is_valid() and experience_form.is_valid():
            for k in experience_form.deleted_forms:
                s = k.save(commit = False)
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
            return HttpResponseRedirect('/profile')
        else:
            messages.error(request, "There was an error processing your request")
    elif user.is_founder and request.method == 'POST':
        profile_form = forms.FounderForm(request.POST, request.FILES, instance=request.user.founder)
        job_form = JobFormSet(request.POST, instance=request.user.founder)
        if profile_form.is_valid() and job_form.is_valid():
            for k in job_form.deleted_forms:
                s = k.save(commit=False)
                s.delete()
            objs = job_form.save(commit=False)
            for obj in objs:
                if obj.title != '':
                    obj.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            user.save()
            return HttpResponseRedirect('/profile')
        else:
            messages.error(request, 'There was an error processing your request')
    elif user.is_founder:
        profile_form = forms.FounderForm(instance=request.user.founder)
        job_form = JobFormSet(instance=request.user.founder)
    else:
        profile_form = forms.ProfileForm(instance=request.user.profile)
        experience_form = ExperienceFormSet(instance = request.user.profile)
    if not user.is_founder:
        return render(request, 'profile_form.html', merge_two_dicts(CONTEXT, {
            'profile_form': profile_form,
            'experience': experience_form,
            'show_exp': True
        }))
    else:
        return render(request, 'profile_form.html', merge_two_dicts(CONTEXT, {
            'profile_form':profile_form,
            'jobs': job_form,
            'show_exp': False
        }))
@login_required(login_url='login/')
def get_user_view(request, id):
    user = get_object_or_404(models.MyUser, pk = id)
    # user = models.MyUser.objects.get(pk = id)
    if user is None:
        return HttpResponseRedirect('/')
    if user.is_founder:
        jobs = user.founder.job_set.order_by('title')
        return render(request, 'founder.html', merge_two_dicts(CONTEXT, {
            'user': user,
            'profile': False,
            'jobs': jobs
        }))
    else:
        exp = user.profile.experience_set.order_by('-start_date')
        return render(request, 'profile.html', merge_two_dicts(CONTEXT, {
            'user': user,
            'profile': False,
            'experience': exp
        }))
class MyRegistrationView(RegistrationView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        return super(MyRegistrationView, self).dispatch(request, *args, **kwargs)
