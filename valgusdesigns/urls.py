# valgusdesigns/urls.py
from app.admin import admin_site
from app.sitemaps import StaticViewSitemap, ArticleSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

sitemaps = {
    "static": StaticViewSitemap,
    "articles": ArticleSitemap,
}

urlpatterns = [
    path("siri/", admin_site.urls),
    path("", include("app.urls")),
    path("portal/", include(("portal.urls", "portal"), namespace="portal")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]