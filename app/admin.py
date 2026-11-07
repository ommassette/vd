# app/admin.py
from django.contrib import admin
from django_otp.admin import OTPAdminSite
from .models import (
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


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(HeroWord)
class HeroWordAdmin(admin.ModelAdmin):
    list_display = ('text', 'css_class', 'order')
    list_editable = ('order',)


@admin.register(IndustryItem)
class IndustryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'position', 'order')
    list_editable = ('order',)


@admin.register(ServicesPageContent)
class ServicesPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(PortfolioPageContent)
class PortfolioPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    inlines = [ProjectImageInline]


@admin.register(ContactPageContent)
class ContactPageContentAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'phone', 'created_at')
    readonly_fields = ('subject', 'email', 'phone', 'message', 'created_at')


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ('position', 'email', 'created_at')
    readonly_fields = ('position', 'email', 'feedback', 'created_at')