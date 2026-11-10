import logging
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from .models import (
    ContactMessage,
    ContactPageContent,
    FeedbackMessage,
    HeroWord,
    HomePageContent,
    IndustryItem,
    PortfolioPageContent,
    Project,
    ServiceItem,
    ServicesPageContent,
    Testimonial,
)

logger = logging.getLogger(__name__)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def index(request):
    context = {
        'content': HomePageContent.objects.first(),
        'hero_words': list(HeroWord.objects.all()),
        'industry_items': list(IndustryItem.objects.all()),
        'testimonials': list(Testimonial.objects.all()),
    }
    return render(request, 'index.html', context)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def services(request):
    context = {
        'content': ServicesPageContent.objects.first(),
        'service_items': list(ServiceItem.objects.all()),
    }
    return render(request, 'services.html', context)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def portfolio(request):
    projects = list(Project.objects.prefetch_related('images').all())
    
    for project in projects:
        for img in project.images.all():
            if hasattr(img, 'image') and img.image:
                img.optimized_url = img.image.build_url(fetch_format="auto", quality="auto")

    context = {
        'content': PortfolioPageContent.objects.first(),
        'projects': projects,
    }
    return render(request, 'portfolio.html', context)


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == 'POST':
        if 'subject' in request.POST:
            subject = request.POST.get('subject')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            message_text = request.POST.get('message')

            if subject and email and phone and message_text:
                ContactMessage.objects.create(
                    subject=subject,
                    email=email,
                    phone=phone,
                    message=message_text
                )
                logger.info("Contact message saved successfully.")

                try:
                    send_mail(
                        subject=f"New Contact Inquiry: {subject}",
                        message=f"Email: {email}\nPhone: {phone}\nMessage: {message_text}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send admin contact notification: {e}")

                if email:
                    try:
                        send_mail(
                            subject="We received your inquiry - Valgus Designs",
                            message=(
                                f"Hello,\n\n"
                                f"Thank you for contacting Valgus Designs.\n\n"
                                f"We have received your message regarding '{subject}'. "
                                f"Our team will review your inquiry and get back to you shortly.\n\n"
                                f"Best regards,\n"
                                f"Valgus Designs Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send user contact confirmation: {e}")

                messages.success(request, "Message sent successfully.")
                return redirect('contact')
            else:
                messages.error(request, "Please fill out all required fields.")

        elif 'position' in request.POST:
            position = request.POST.get('position')
            email = request.POST.get('email')
            feedback = request.POST.get('feedback')

            if position and feedback:
                FeedbackMessage.objects.create(
                    position=position,
                    email=email,
                    feedback=feedback
                )
                logger.info("Feedback saved successfully.")

                try:
                    send_mail(
                        subject="New Feedback Submission - Valgus Designs",
                        message=f"Position/Author: {position}\nEmail: {email or 'N/A'}\nFeedback: {feedback}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send admin feedback notification: {e}")

                if email:
                    try:
                        send_mail(
                            subject="Thank you for your feedback - Valgus Designs",
                            message=(
                                f"Hello,\n\n"
                                f"Thank you for sharing your feedback with Valgus Designs.\n\n"
                                f"We truly appreciate your insights and input.\n\n"
                                f"Best regards,\n"
                                f"Valgus Designs Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send feedback user confirmation: {e}")

                messages.success(request, "Feedback submitted successfully.")
                return redirect('contact')
            else:
                messages.error(request, "Please fill out all feedback fields.")

    context = {'content': ContactPageContent.objects.first()}
    return render(request, 'contact.html', context)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def privacy_policy(request):
    return render(request, 'policy.html')


@cache_page(60 * 15)
@require_http_methods(["GET"])
def terms(request):
    return render(request, 'terms.html')


@cache_page(60 * 15)
@require_http_methods(["GET"])
def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /siri/
Disallow: /static/admin/

Host: https://valgusdesigns.com
Sitemap: https://valgusdesigns.com/sitemap.xml
"""
    return HttpResponse(content.strip(), content_type="text/plain")