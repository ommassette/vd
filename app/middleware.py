import os
from django.http import Http404

class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        main_domain = os.environ.get("MAIN_DOMAIN", "valgusdesigns.com")
        
        # Allow /siri/ to use main urls even on portal subdomain
        if host == f"portal.{main_domain}" and not request.path.startswith('/siri/'):
            request.urlconf = 'portal.urls'
        else:
            request.urlconf = 'valgusdesigns.urls'
            
        response = self.get_response(request)
        return response