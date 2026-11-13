# app/models.py
import logging
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone

logger = logging.getLogger(__name__)


class HomePageContent(models.Model):
    hero_prefix = models.CharField(
        max_length=255, blank=True, null=True, default="We help businesses with"
    )
    intro_text = models.TextField(
        blank=True, null=True, default="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua"
    )
    intro_image = CloudinaryField(
        'image', 
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )

    brand_name = models.CharField(max_length=255, blank=True, null=True, default="Valgus Designs")

    about_lead = models.TextField(
        blank=True, null=True, default="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    )
    about_body = models.TextField(
        blank=True, null=True, default="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    about_image = CloudinaryField(
        'image', 
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )

    industries_lead = models.TextField(
        blank=True, null=True, default="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt."
    )

    dark_section_text = models.TextField(
        blank=True, null=True, default="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore."
    )
    dark_section_title = models.CharField(
        max_length=255, blank=True, null=True, default="Bold ideas built to last"
    )
    dark_section_image = CloudinaryField(
        'image', 
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"

    def __str__(self):
        return "Home Page Content Configuration"


class HeroWord(models.Model):
    text = models.CharField(max_length=100, blank=True, null=True)
    css_class = models.CharField(
        max_length=100, blank=True, null=True, help_text="e.g. word--content, word--web, word--design"
    )
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text or "Hero Word"


class IndustryItem(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name or "Industry Item"


class Testimonial(models.Model):
    quote = models.TextField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.author or 'Unknown'} - {self.position or 'Unknown'}"


class ServicesPageContent(models.Model):
    intro_subtitle = models.CharField(
        max_length=255, blank=True, null=True, default="Lorem ipsum dolor sit ut labore"
    )
    header_text = models.TextField(
        blank=True, null=True, default="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    )
    header_image = CloudinaryField(
        'image', 
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )

    class Meta:
        verbose_name = "Services Page Content"
        verbose_name_plural = "Services Page Content"

    def __str__(self):
        return "Services Page Configuration"


class ServiceItem(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    basic_name = models.CharField(max_length=100, blank=True, null=True, default="Basic")
    basic_price = models.CharField(max_length=50, blank=True, null=True, default="$500")
    basic_features = models.TextField(blank=True, null=True, help_text="Put each feature on a new line")

    standard_name = models.CharField(max_length=100, blank=True, null=True, default="Standard")
    standard_price = models.CharField(max_length=50, blank=True, null=True, default="$1,200")
    standard_features = models.TextField(blank=True, null=True, help_text="Put each feature on a new line")

    premium_name = models.CharField(max_length=100, blank=True, null=True, default="Premium")
    premium_price = models.CharField(max_length=50, blank=True, null=True, default="$2,500")
    premium_features = models.TextField(blank=True, null=True, help_text="Put each feature on a new line")

    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Service Item"

    def get_basic_features_list(self):
        if not self.basic_features:
            return []
        return [f.strip() for f in self.basic_features.split('\n') if f.strip()]

    def get_standard_features_list(self):
        if not self.standard_features:
            return []
        return [f.strip() for f in self.standard_features.split('\n') if f.strip()]

    def get_premium_features_list(self):
        if not self.premium_features:
            return []
        return [f.strip() for f in self.premium_features.split('\n') if f.strip()]


class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=255, blank=True, null=True, default="Valgus Designs")
    copyright_text = models.CharField(max_length=255, blank=True, null=True, default="© 2026 Valgus Designs. All rights reserved.")
    address = models.CharField(max_length=255, blank=True, null=True, default="123 Lorem Street, Dolor City")
    email = models.EmailField(blank=True, null=True, default="hello@valgusdesigns.com")
    phone = models.CharField(max_length=50, blank=True, null=True, default="+1 234 567 890")
    whatsapp_url = models.URLField(max_length=500, blank=True, null=True, default="#")
    privacy_policy_url = models.URLField(max_length=500, blank=True, null=True, default="#")
    terms_url = models.URLField(max_length=500, blank=True, null=True, default="#")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Global Site Footer Settings"


class PortfolioPageContent(models.Model):
    intro_subtitle = models.CharField(
        max_length=255, blank=True, null=True, default="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore"
    )

    class Meta:
        verbose_name = "Portfolio Page Content"
        verbose_name_plural = "Portfolio Page Content"

    def __str__(self):
        return "Portfolio Page Configuration"


class Project(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    project_url = models.URLField(max_length=500, blank=True, null=True, default="#")
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Project"


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE, blank=True, null=True)
    image = CloudinaryField(
        'image',
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        proj_title = self.project.title if self.project else "Unassigned"
        return f"Image for {proj_title}"


class ContactPageContent(models.Model):
    contact_text = models.TextField(blank=True, null=True, default="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua")
    feedback_title = models.CharField(max_length=255, blank=True, null=True, default="Feedback")
    feedback_text = models.TextField(blank=True, null=True, default="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore")

    class Meta:
        verbose_name = "Contact Page Content"
        verbose_name_plural = "Contact Page Content"

    def __str__(self):
        return "Contact Page Configuration"


class ContactMessage(models.Model):
    service = models.CharField(max_length=255, blank=True, null=True)
    timeline = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        contact = self.email or self.phone or "No Contact"
        return f"{self.service or 'General'} — {contact}"


class FeedbackMessage(models.Model):
    position = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Feedback ({self.position or 'General'}) - {self.email or 'No Email'}"

class Article(models.Model):
    # Meta
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Auto-fills from title — edit if needed for SEO")
    author = models.CharField(max_length=100, blank=True, null=True, default="Valgus Creative")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(blank=True, null=True, default=0)

    # Hero
    hero_image = CloudinaryField(
        'image',
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )

    # Content block 1
    intro_paragraph = models.TextField(
        blank=True, null=True,
        help_text="Opening paragraph — gets the big magazine-style drop cap."
    )
    paragraph_2 = models.TextField(blank=True, null=True)
    subheading_1 = models.CharField(max_length=255, blank=True, null=True)
    paragraph_3 = models.TextField(blank=True, null=True)
    paragraph_4 = models.TextField(blank=True, null=True)

        # Pull quote (optional)
    quote_text = models.TextField(
        blank=True, null=True,
        help_text="Optional pull quote shown between the two content blocks."
    )
    quote_author = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Optional attribution for the quote."
    )

    # Mid image
    mid_image = CloudinaryField(
        'image',
        blank=True, null=True,
        transformation={'fetch_format': 'auto', 'quality': 'auto'}
    )
    mid_image_caption = models.CharField(max_length=255, blank=True, null=True)

    # Content block 2
    subheading_2 = models.CharField(max_length=255, blank=True, null=True)
    paragraph_5 = models.TextField(blank=True, null=True)
    paragraph_6 = models.TextField(blank=True, null=True)
    paragraph_7 = models.TextField(
        blank=True, null=True,
        help_text="Closing paragraph. Leave blank if the article ends earlier."
    )

    class Meta:
        ordering = ['order', '-published_at']

    def __str__(self):
        return self.title or "Untitled Article"

class ArticlePageContent(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, default="Articles")
    intro_text = models.TextField(
        blank=True, null=True,
        default="Notes on branding, design, and building businesses that look the part."
    )

    class Meta:
        verbose_name = "Article Page Content"
        verbose_name_plural = "Article Page Content"

    def __str__(self):
        return "Article Page Configuration"