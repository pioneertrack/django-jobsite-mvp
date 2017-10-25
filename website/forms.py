# -*- coding: utf-8 -*-
from registration.forms import RegistrationFormUniqueEmail
from nocaptcha_recaptcha.fields import NoReCaptchaField
from website import models, profile
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.forms.fields import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML
# get a way to log the errors:
import logging
# convert the errors to text
from django.utils.encoding import force_text
import base64, uuid
from django.core.files.base import ContentFile
# from rest_framework import serializers

log = logging.getLogger(__name__)
logging.basicConfig(filename='errorlog.txt')


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             # base64 encoded image - decode
#             format, imgstr = data.split(';base64,') # format ~= data:image/X,
#             ext = format.split('/')[-1] # guess file extension
#             id = uuid.uuid4()
#             data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
#         return super(Base64ImageField, self).to_internal_value(data)


class NewRegistrationForm(RegistrationFormUniqueEmail):
    captcha = NoReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
        self.fields['captcha'].label = ''
        self.fields['email'].help_text = "Must be a @berkeley.edu email address"

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(NewRegistrationForm, self).is_valid()

    def clean_email(self):
        submitted_data = self.cleaned_data['email']
        if hasattr(settings, 'ALLOWED_DOMAINS'):
            ALLOWED_DOMAINS = settings.ALLOWED_DOMAINS
        else:
            ALLOWED_DOMAINS = ['berkeley.edu']
        if not ALLOWED_DOMAINS:  # If we allow any domain
            return submitted_data

        domain = submitted_data.split('@')[1]
        if domain == 'bearfounders.com':
            return submitted_data
        if domain not in ALLOWED_DOMAINS:
            raise forms.ValidationError(
                u'You must register using an email address with a valid '
                'berkeley email ({}).'
                    .format(', '.join(ALLOWED_DOMAINS))
            )
        return submitted_data

    class Meta:
        model = models.MyUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'is_individual': 'Create individual profile',
            'is_founder': 'Create startup profile',
            'captcha': '',
        }


class ProfileFormWizard(forms.ModelForm):
    image = forms.ImageField(label='Profile image', required=True, error_messages={'invalid': "Image files only"},
                             widget=forms.FileInput)
    image_decoded = forms.CharField(label='Profile image')

    def __init__(self, *args, **kwargs):
        super(ProfileFormWizard, self).__init__(*args, **kwargs)
        if self.instance.image and len(self.instance.image.name) > 0:
            self.fields['image'].required = False

    class Meta:
        model = profile.Profile
        fields = ('image', 'bio', 'positions', 'role', 'skills', 'year', 'interests',
                  'major', 'courses', 'hours_week', 'has_startup_exp', 'has_funding_exp', 'linkedin', 'website',
                  'github')


class ProfileForm(forms.ModelForm):
    image = forms.ImageField(label='Profile image', required=True, error_messages={'invalid': "Image files only"},
                             widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.initial['alt_email'] = None
        if self.instance.image and len(self.instance.image.name) > 0:
            self.fields['image'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('image', template='forms/image-input.html'))
        self.fields['bio'].widget.attrs.update({
                                                   'placeholder': 'I am a senior who enjoys tech and education. I am looking forward to working with startups and would love to get mentored by Cal alums who have experience with operations.'})
        self.fields['skills'].widget.attrs.update({
                                                      'placeholder': 'Python, javascript, SQL, data analysis, financial modeling, photography, UX/UI, Microsoft office, social media…'})
        self.fields['interests'].widget.attrs.update({'placeholder': 'Sports, writing, edtech, travel, health'})
        self.fields['courses'].widget.attrs.update({'placeholder': 'UGBA 104, CS70, Econ 100B'})

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(ProfileForm, self).is_valid()

    def clean_alt_email(self):
        email = self.cleaned_data['alt_email']
        if email != None and email != '':
            result = profile.Profile.objects.filter(alt_email=email)
            if result.count() > 1 or (result.count() == 1 and result[0].id != self.instance.id):
                raise ValidationError(message='Alt email already used')
        return email

    class Meta:
        model = profile.Profile
        fields = ('image', 'bio', 'positions', 'role', 'skills', 'year', 'alt_email', 'interests',
                  'major', 'courses', 'hours_week', 'has_startup_exp', 'has_funding_exp', 'linkedin', 'website',
                  'github')
        labels = {
            'has_startup_exp': 'I have worked at a startup before',
            'has_funding_exp': 'I have experience with funding a startup',
            'bio': 'About me',
            'role': 'Primary role',
            'website': 'Personal website',
            'courses': 'Relevant coursework',
            'major': 'Primary Major',
            'positions': 'Seeking what type of position?',
            'alt_email': 'Alternate Contact Email',
        }


class FounderForm(forms.ModelForm):
    logo = forms.ImageField(label='Logo', required=True, error_messages={'invalid': "Image files only"},
                            widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(FounderForm, self).__init__(*args, **kwargs)
        self.initial['alt_email'] = None
        if self.instance.logo and len(self.instance.logo.name) > 0:
            self.fields['logo'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('logo', template='forms/image-input.html'))

    def clean_alt_email(self):
        email = self.cleaned_data['alt_email']
        if email != None and email != '':
            result = profile.Founder.objects.filter(alt_email=email)
            if result.count() > 1 or (result.count() == 1 and result[0].id != self.instance.id):
                raise ValidationError(message='Alt email already used')
        return email

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(FounderForm, self).is_valid()

    class Meta:
        model = profile.Founder
        fields = ('startup_name', 'stage', 'employee_count', 'logo', 'description', 'field', 'alt_email',
                  'website', 'facebook', 'display_funding')
        labels = {
            'employee_count': 'Number of employees',
            'stage': 'What stage is your startup in?',
            'hours_wanted': 'Hours per week candidates should have available',
            'seeking': 'Looking for a partner or to hire/contract?',
            'alt_email': 'Alternate Contact Email',
        }


class ExperienceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExperienceForm, self).__init__(*args, **kwargs)
        self.fields['company'].widget.attrs.update({'placeholder': 'Visa'})
        self.fields['position'].widget.attrs.update({'placeholder': 'Analyst'})
        self.fields['description'].widget.attrs.update(
            {'placeholder': 'Used SQL to create weekly reports to focus on core team metrics.'})

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(ExperienceForm, self).is_valid()

    class Meta:
        model = profile.Experience
        fields = ('company', 'position', 'start_date', 'currently_working', 'end_date', 'description')
        widgets = {
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput()
        }


class FundingForm(forms.ModelForm):

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(FundingForm, self).is_valid()

    class Meta:
        model = profile.Funding
        fields = ('stage', 'raised')


class JobForm(forms.ModelForm):

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(JobForm, self).is_valid()

    class Meta:
        model = profile.Job
        fields = ('title', 'level', 'pay', 'description')


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = ''


class ChangeAlternateEmailForm(forms.ModelForm):
    class Meta:
        model = profile.Profile
        fields = ('alt_email',)


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(required=True)
