# app/admin.py
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import (
    Article,             # ← add
    ArticlePageContent,
    ContactMessage,
    ContactPageContent,
    FeedbackMessage,
    HeroWord,
    HomePageContent,
    IndustryItem,
    PortfolioPageContent,
    Project,
    ProjectImage,
    ServiceItem,
    ServicesPageContent,
    SiteSettings,
    Testimonial,
)


class OTPAdmin(OTPAdminSite):
    pass


admin_site = OTPAdmin(name='OTPAdmin')

# Register built-in auth and OTP device models
admin_site.register(User)
admin_site.register(Group)
admin_site.register(TOTPDevice)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(HomePageContent, site=admin_site)
class HomePageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(HeroWord, site=admin_site)
class HeroWordAdmin(admin.ModelAdmin):
    list_display = ('text', 'css_class', 'order')
    list_editable = ('order',)


@admin.register(IndustryItem, site=admin_site)
class IndustryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(Testimonial, site=admin_site)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'position', 'order')
    list_editable = ('order',)


@admin.register(ServicesPageContent, site=admin_site)
class ServicesPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceItem, site=admin_site)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)


@admin.register(SiteSettings, site=admin_site)
class SiteSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(PortfolioPageContent, site=admin_site)
class PortfolioPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    inlines = [ProjectImageInline]


@admin.register(ContactPageContent, site=admin_site)
class ContactPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactMessage, site=admin_site)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('service', 'timeline', 'email', 'phone', 'created_at')
    readonly_fields = ('service', 'timeline', 'email', 'phone', 'created_at')


@admin.register(FeedbackMessage, site=admin_site)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ('position', 'email', 'created_at')
    readonly_fields = ('position', 'email', 'feedback', 'created_at')

@admin.register(Article, site=admin_site)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'is_published', 'order')
    list_editable = ('is_published', 'order')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Article Meta', {
            'fields': ('title', 'slug', 'author', 'published_at', 'is_published', 'order')
        }),
        ('Hero Image', {
            'fields': ('hero_image',)
        }),
        ('Content — Block 1', {
            'fields': ('intro_paragraph', 'paragraph_2', 'subheading_1', 'paragraph_3', 'paragraph_4'),
            'description': (
                'Fill only what the article needs. The intro paragraph gets the drop cap. '
                'Any field left blank is simply skipped in the layout.'
            )
        }),
        ('Mid Article Image', {
            'fields': ('mid_image', 'mid_image_caption')
        }),
        ('Content — Block 2', {
            'fields': ('subheading_2', 'paragraph_5', 'paragraph_6', 'paragraph_7')
        }),
    )
    
@admin.register(ArticlePageContent, site=admin_site)
class ArticlePageContentAdmin(admin.ModelAdmin):
    pass