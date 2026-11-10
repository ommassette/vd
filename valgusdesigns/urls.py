from app.admin import admin_site
from app.sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("siri/", admin_site.urls),
    path("", include(("portal.urls", "portal"), namespace="portal")),
    path("", include("app.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]