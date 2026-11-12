# app/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.models import Article, Project, ServiceItem

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['index', 'services', 'portfolio', 'contact', 'privacy_policy', 'terms', 'articles']

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return reverse('article_detail', kwargs={'slug': obj.slug})