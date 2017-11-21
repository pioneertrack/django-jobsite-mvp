import re
from django.conf import settings

MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)


def is_mobile(request):
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return {'is_mobile': True}
    else:
        return {'is_mobile': False}


def search_enabled(request):
    user = request.user
    result = True
    if user.is_authenticated():
        p = lambda val: not val.profile.is_filled if hasattr(val, 'profile') else True
        f = lambda val: not val.founder.is_filled if hasattr(val, 'founder') else True
        if p(user) and user.is_individual:
            result = False
        elif f(user) and user.is_founder:
            result = False
        elif user.is_account_disabled and (not user.is_admin or user.test_mode):
            result = False
    return {'search_enabled': result}


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
