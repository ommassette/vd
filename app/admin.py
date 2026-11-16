# app/admin.py
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import (
    Article,
    ArticlePageContent,
    CaseStudy,
    ColorSwatch,
    ContactMessage,
    ContactPageContent,
    FeedbackMessage,
    HeroWord,
    HomePageContent,
    IndustryItem,
    PortfolioPageContent,
    Project,
    ProjectImage,
    ScopeTag,
    ServiceItem,
    ServicesPageContent,
    SiteSettings,
    Testimonial,
    Typeface,
    UIComponent,
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
        ('Pull Quote (Optional)', {
            'fields': ('quote_text', 'quote_author'),
            'description': (
                'Large centered quote that breaks up the article. '
                'Leave blank to skip — nothing renders if both fields are empty.'
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

# =============================================================================
# CASE STUDY ADMIN
# =============================================================================

class ScopeTagInline(admin.TabularInline):
    model = ScopeTag
    extra = 1
    fields = ('order', 'name')
    ordering = ('order',)


class ColorSwatchInline(admin.TabularInline):
    model = ColorSwatch
    extra = 1
    fields = ('order', 'name', 'hex_code')
    ordering = ('order',)


class TypefaceInline(admin.TabularInline):
    model = Typeface
    extra = 1
    fields = ('order', 'label', 'display_name', 'font_family', 'google_fonts_url')
    ordering = ('order',)


class UIComponentInline(admin.TabularInline):
    model = UIComponent
    extra = 1
    fields = ('order', 'component_type', 'label', 'content')
    ordering = ('order',)


@admin.register(CaseStudy, site=admin_site)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'client_name', 'year', 'show_transformation', 'show_design_system', 'show_video')
    list_filter = ('show_transformation', 'show_design_system', 'show_video')
    search_fields = ('project__title', 'client_name')
    readonly_fields = ('created_at',)
    inlines = [ScopeTagInline, ColorSwatchInline, TypefaceInline, UIComponentInline]

    fieldsets = (
        ('Linked Project', {
            'fields': ('project', 'created_at'),
            'description': (
                'Each project can have one case study. '
                'To show the "View Case Study" button on the portfolio page, '
                'a case study must exist for the project.'
            ),
        }),
        ('Hero & Meta', {
            'fields': (
                'kicker',
                'client_name',
                'client_location',
                'year',
                'scope_summary',
                'hero_image',
            ),
            'description': (
                'The two-column hero at the top of the page. '
                'Client, Year, and Scope render as the facts strip below the title. '
                'Scope tags are managed in the inline at the bottom of this form.'
            ),
        }),
        ('01 — The Brief & Vision', {
            'fields': ('brief_heading', 'brief_body'),
            'description': (
                'The starting point. What the client looked like before, '
                'and what the creative goal was. '
                'Use a blank line between paragraphs — each becomes a separate <p>.'
            ),
        }),
        ('02 — The Creative Direction', {
            'fields': ('direction_heading', 'direction_body'),
            'description': (
                'Your thinking. Visual language choices — typography, colour, layout. '
                'How you broke from generic templates in the industry.'
            ),
        }),
        ('03 — The Craft & Execution', {
            'fields': ('craft_heading', 'craft_body'),
            'description': (
                'What you actually built. UI/UX breakdown, technical polish, '
                'performance, architecture, micro-interactions.'
            ),
        }),
        ('04 — Transformation · Before & After (Optional)', {
            'fields': (
                'show_transformation',
                'transformation_heading',
                'transformation_before_label',
                'transformation_after_label',
                'transformation_before_image',
                'transformation_after_image',
            ),
            'description': (
                'Tick <b>Show this section</b> only if the project involved a rebrand, '
                'redesign, or clear before/after. Leave unticked for from-scratch builds.'
            ),
            'classes': ('wide',),
        }),
        ('05 — Design System (Optional)', {
            'fields': ('show_design_system', 'design_system_heading'),
            'description': (
                'Tick <b>Show this section</b> for projects built from scratch. '
                'The colour palette, typeface specimens, and UI components are managed '
                'in the inlines at the bottom of this form. '
                'Use <b>both 04 and 05</b> if the project had a rebrand <i>and</i> a full design system.'
            ),
            'classes': ('wide',),
        }),
        ('06 — Video Walkthrough (Optional)', {
            'fields': ('show_video', 'video_label', 'video_file', 'video_poster'),
            'description': (
                'Tick <b>Show this section</b> if you have a walkthrough video. '
                'Upload the <b>video file</b> directly (MP4 or WebM — Cloudinary handles transcoding and CDN delivery). '
                'Optionally add a <b>poster image</b> (16:9 recommended) that appears before playback starts. '
                'The player is custom, unstyled from any third party, and matches the site.'
            ),
        }),
        ('CTA (Optional Override)', {
            'fields': ('cta_heading', 'cta_text', 'cta_button_label'),
            'description': (
                'Every case study ends with a call-to-action before the footer. '
                'The defaults are sensible — only change these if you want '
                'a project-specific CTA copy.'
            ),
            'classes': ('collapse',),
        }),
    )