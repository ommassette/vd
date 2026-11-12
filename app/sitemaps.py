from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['index', 'services', 'portfolio', 'contact', 'privacy_policy', 'terms', 'articles', 'article_detail']

    def location(self, item):
        return reverse(item)