from registration.forms import RegistrationFormUniqueEmail
from nocaptcha_recaptcha.fields import NoReCaptchaField
from website import models, profile
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import EmailValidator
from django import template
from django.utils.safestring import mark_safe
# get a way to log the errors:
import logging
# convert the errors to text
from django.utils.encoding import force_text


log = logging.getLogger(__name__)
logging.basicConfig(filename='errorlog.txt')


class NewRegistrationForm(RegistrationFormUniqueEmail):
    captcha = NoReCaptchaField()
    create_both_profiles = forms.BooleanField(label='Both', required=False,
                                             widget=forms.CheckboxInput(attrs={'id': 'select-both-profiles'}))

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
        if not ALLOWED_DOMAINS: # If we allow any domain
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

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('is_individual') and not cleaned_data.get('is_founder'):
            self.add_error('create_both_profiles', 'You must be representing an individual profile or startup')
        return cleaned_data

    class Meta:
        model = models.MyUser
        fields = ['first_name', 'last_name', 'email', 'is_individual', 'is_founder', 'create_both_profiles', 'password1', 'password2']
        labels = {
            'is_individual': 'Create individual profile',
            'is_founder': 'Create startup profile',
            'captcha': '',
        }


class ProfileForm(forms.ModelForm):
    image = forms.ImageField(label='Profile image',required=False, error_messages ={'invalid':"Image files only"}, widget = forms.FileInput)
    def is_valid(self):
        log.info(force_text(self.errors))
        return super(ProfileForm, self).is_valid()

    class Meta:
        model = profile.Profile
        fields = ('image', 'bio', 'position', 'role','alt_email', 'interests', 'skills', 'major', 'courses', 'year', 'hours_week', 'has_startup_exp', 'has_funding_exp', 'linkedin', 'website', 'github')
        labels = {
            'has_startup_exp': 'I have worked at a startup before',
            'has_funding_exp': 'I have experience with funding a startup',
            'bio': 'About me',
            'role': 'Primary role',
            'website': 'Personal website',
            'courses': 'Relevant coursework',
            'major': 'Primary Major',
	    'position': 'Seeking what type of position?',
        }

class FounderForm(forms.ModelForm):
    logo = forms.ImageField(label='Logo',required=False, error_messages ={'invalid':"Image files only"}, widget = forms.FileInput)
    def is_valid(self):
        log.info(force_text(self.errors))
        return super(FounderForm, self).is_valid()
    class Meta:
        model = profile.Founder
        fields = ('startup_name', 'stage', 'employee_count', 'logo', 'description', 'field', 'website', 'facebook', 'display_funding')
        labels = {
            'employee_count': 'Number of employees',
            'stage': 'What stage is your startup in?',
            'hours_wanted': 'Hours per week candidates should have available',
            'seeking': 'Looking for a partner or to hire/contract?'
        }

class ExperienceForm(forms.ModelForm):
    def is_valid(self):
        log.info(force_text(self.errors))
        return super(ExperienceForm, self).is_valid()
    class Meta:
        model = profile.Experience
        fields=('company', 'position','start_date', 'currently_working','end_date', 'description')
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
        fields=('stage', 'raised')

class JobForm(forms.ModelForm):
    def is_valid(self):
        log.info(force_text(self.errors))
        return super(JobForm, self).is_valid()
    class Meta:
        model = profile.Job
        fields=('title', 'level', 'pay', 'description')


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = ''


class ChangeAlternateEmailForm(forms.ModelForm):

    class Meta:
        model = profile.Profile
        fields = ('alt_email',)

