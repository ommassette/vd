import os

class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        main_domain = os.environ.get("MAIN_DOMAIN", "valgusdesigns.com")
        
        if request.path.startswith('/siri'):
            request.urlconf = 'valgusdesigns.urls'
        elif host == f"portal.{main_domain}":
            request.urlconf = 'portal.urls'
        else:
            request.urlconf = 'valgusdesigns.urls'
            
        return self.get_response(request)