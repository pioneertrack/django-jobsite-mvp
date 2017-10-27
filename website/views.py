from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import Context
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
from django.core import signing
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
from website.decorators import check_profiles

import base64, uuid
from django.core.files.base import ContentFile


def merge_dicts(*args):
    dc = {}
    for item in args:
        dc.update(item)
    return dc


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


# Create your views here.
@csrf_exempt
@login_required(login_url='login/')
def connect(request):
    if request.is_ajax():
        url = urlparse(request.META.get('HTTP_REFERER'))
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


@login_required
@check_profiles
@never_cache
def user_profile(request):
    last_login = request.user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    experience = request.user.profile.experience_set.order_by('-end_date')

    # TODO: need to remember normal alg for that
    positions = []
    for item in request.user.profile.positions:
        positions.append(prof.POSITIONS.__getitem__(int(item))[1])

    return render(request, 'profile.html', merge_dicts(JOB_CONTEXT, {
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
@user_passes_test(lambda user: user.first_login, '/', redirect_field_name=None)
@never_cache
def profile_step(request):
    user = request.user
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
    formDat["hasStartup"] = (("yes", 'Yes'), ("no", 'No'))

    profile = None if not hasattr(user, 'profile') else user.profile
    if profile is None:
        user = MyUser.objects.get(pk=request.user.id)
        profile = prof.Profile(user=user)

    profile_form = forms.ProfileFormWizard(instance=profile)

    if request.method == 'POST':
        # TODO: Implement Base64EncodedImage form field
        if request.POST.get('image_decoded'):
            image = request.POST.get('image_decoded')
            if image.startswith('data:image'):
                # base64 encoded image - decode
                format, imgstr = image.split(';base64,')  # format ~= data:image/X,
                ext = format.split('/')[-1]  # guess file extension
                id = uuid.uuid4()
                request.FILES[u'image'] = ContentFile(base64.b64decode(imgstr), name=id.urn[9:] + '.' + ext)

        profile_form = forms.ProfileFormWizard(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.check_is_filled()

            request.session['clear_client_profile'] = True
            if request.POST["startupProfile"] == "no":
                user.set_first_login()
                response = HttpResponseRedirect('/')
            else:
                response = HttpResponseRedirect('/startup/update')
            response.set_cookie('clear_profile', '1')
            return response

    return render(request, 'profile_steps.html', merge_dicts(JOB_CONTEXT, {
        'formDat': formDat,
        'errors': errors,
        'form': profile_form,
    }))


@login_required
@never_cache
def profile_update(request):
    user = request.user
    cancel_url = request.META.get('HTTP_REFERER')
    if user.first_login:
        cancel_url = reverse('landing:home')

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
    if profile is None:
        user = MyUser.objects.get(pk=request.user.id)
        profile = prof.Profile(user=user)

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
        'next_url': reverse('website:startup_update') if user.is_founder else reverse('website:profile'),
        'cancel_url': cancel_url,
    }))


@login_required
@never_cache
def startup_update(request):
    user = request.user
    cancel_url = request.META.get('HTTP_REFERER')
    if user.first_login:
        user.set_first_login()
        cancel_url = reverse('landing:home')

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
    if founder is None:
        user = MyUser.objects.get(pk=request.user.id)
        founder = prof.Founder(user=user)

    startup_form = forms.FounderForm(instance=founder)
    funding_form = FundingFormSet(instance=founder)
    job_form = JobFormSet(instance=founder)

    if request.method == 'POST':
        profile_form = forms.FounderForm(request.POST, request.FILES, instance=founder)
        funding_form = FundingFormSet(request.POST, instance=founder)
        job_form = JobFormSet(request.POST, instance=founder)
        if profile_form.is_valid() and job_form.is_valid() and funding_form.is_valid():
            founder = profile_form.save(commit=False)
            user.set_is_founder()

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

    return render(request, 'profile_form.html', merge_dicts(JOB_CONTEXT, {
        'profile_form': startup_form,
        'funding': funding_form,
        'jobs': job_form,
        'show_exp': False,
        'reset': True,
        'is_first_login': is_first_login,
        'title': 'Update Startup',
        'profile_edit': True,
        'next_url': reverse('website:startup_profile'),
        'cancel_url': cancel_url,
    }))


@login_required
@check_profiles
def get_profile_view(request, id):
    profile = get_object_or_404(prof.Profile, pk=id)
    last_login = profile.user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    # TODO: need to remember normal alg for that
    positions = []
    for item in profile.positions:
        positions.append(prof.POSITIONS.__getitem__(int(item))[1])
    exp = profile.experience_set.order_by('-end_date')
    return render(request, 'profile_info.html', merge_dicts(JOB_CONTEXT, {
        'profile': profile,
        'experience': exp,
        'reset': True,
        'last_login': last_login,
        'positions_display': positions,
        'cd': cd,
    }))


@login_required
@check_profiles
def get_startup_view(request, id):
    founder = get_object_or_404(prof.Founder, pk=id)
    last_login = founder.user.last_login
    current_time = timezone.now()
    cr = current_time - last_login
    cd = cr.total_seconds() < 86400
    jobs = founder.job_set.order_by('title')
    return render(request, 'founder_info.html', merge_dicts(JOB_CONTEXT, {
        'founder': founder,
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
        context.update(**JOB_CONTEXT)
        return context

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password updated')
        return super(Settings, self).form_valid(form)


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
