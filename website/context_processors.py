import re

MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)


def is_mobile(request):
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return {'is_mobile': True}
    else:
        return {'is_mobile': True}
