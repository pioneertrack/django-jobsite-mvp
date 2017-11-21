from django.contrib import messages
from django.shortcuts import redirect
from website.context_processors import is_mobile
from django.http import Http404


def check_profiles(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user = request.user
        redirect_url = None
        p = lambda val: not val.profile.is_filled if hasattr(val, 'profile') else True
        f = lambda val: not val.founder.is_filled if hasattr(val, 'founder') else True
        if user.first_login:
            mobile = is_mobile(request)['is_mobile']
            if not user.is_individual:
                user.set_is_individual()
            if user.is_individual and p(user):
                # messages.success(request, "Welcome to BearFounders! Please tell us about yourself.")
                redirect_url = 'website:profile_update' if mobile else 'website:profile_step'
            elif user.is_founder and f(user):
                # messages.success(request, "Welcome to BearFounders! Please tell us about you startup.")
                redirect_url ='website:startup_update'
        else:
            if p(user) and user.is_individual:
                messages.success(request, "Please fill in the information about yourself.")
                redirect_url = 'website:profile_update'
            elif f(user) and user.is_founder:
                messages.success(request, "Please fill in the information about you startup.")
                redirect_url = 'website:startup_update'
            elif user.is_account_disabled and (not user.is_admin or user.test_mode):
                if not request.resolver_match.url_name in ['profile', 'startup_profile']:
                    redirect_url = 'website:settings'

        if redirect_url is not None:
            return redirect(redirect_url)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def test_mode(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            return view_func(request, *args, **kwargs)
        elif not request.resolver_match.url_name in ['get_test_profile_view', 'search_test']:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404
    return _wrapped_view_func
