# app/context_processors.py (create this file)
from .models import SiteSettings

def site_settings(request):
    return {'site_settings': SiteSettings.objects.first()}