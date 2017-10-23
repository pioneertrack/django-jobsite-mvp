from django.contrib import messages
from django.shortcuts import redirect


def check_profiles(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        user = request.user
        redirect_url = None
        p = lambda val: not val.profile.is_filled if hasattr(val, 'profile') else True
        f = lambda val: not val.founder.is_filled if hasattr(val, 'founder') else True
        if user.first_login:
            if user.is_individual and p(user):
                messages.success(request, "Welcome to BearFounders! Please tell us about yourself.")
                redirect_url = 'website:profile_step'
            elif user.is_founder and f(user):
                messages.success(request, "Welcome to BearFounders! Please tell us about you startup.")
                redirect_url ='website:startup_update'
        else:
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
