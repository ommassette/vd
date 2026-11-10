import os
from django.http import Http404

class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0] # Strip port if present
        
        # Define your main domain root
        main_domain = os.environ.get("MAIN_DOMAIN", "valgusdesigns.com")
        
        # Check if it's the portal subdomain
        if host == f"portal.{main_domain}":
            request.urlconf = 'portal.urls'
        else:
            # Default to main project URLconf
            request.urlconf = 'valgusdesigns.urls'
            
        response = self.get_response(request)
        return response