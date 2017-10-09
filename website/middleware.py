import re

cc_delim_re = re.compile(r'\s*,\s*')


def remove_vary_headers(response, headers):
    """
    Adds (or updates) the "Vary" header in the given HttpResponse object.
    newheaders is a list of header names that should be in "Vary". Existing
    headers in "Vary" aren't removed.
    """
    # Note that we need to keep the original order intact, because cache
    # implementations may rely on the order of the Vary contents in, say,
    # computing an MD5 hash.
    if response.has_header('Vary'):
        vary_headers = cc_delim_re.split(response['Vary'])
    else:
        vary_headers = []
    # Use .lower() here so we treat headers as case-insensitive.
    existing_headers = set(header.lower() for header in vary_headers)
    if existing_headers.__contains__(headers.lower()):
        existing_headers.remove(headers.lower())
    if len(vary_headers) > 0:
        response['Vary'] = existing_headers
    elif response.has_header('Vary'):
        response.headers.remove('Vary')

class SessionHeaderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Session-Header'] = request.session.session_key
        return response


class RemoveVaryCookiesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Session-Header'] = request.session.session_key
        remove_vary_headers(response, 'Cookie')
        return response
