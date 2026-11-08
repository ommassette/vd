# app/views.py
import logging
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
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


@require_http_methods(["GET"])
def index(request):
    context = cache.get("index_view_data")
    if not context:
        logger.info("Memcached cache miss for index view. Querying database.")
        context = {
            'content': HomePageContent.objects.first(),
            'hero_words': list(HeroWord.objects.all()),
            'industry_items': list(IndustryItem.objects.all()),
            'testimonials': list(Testimonial.objects.all()),
        }
        cache.set("index_view_data", context, 3600)
    return render(request, 'index.html', context)


@require_http_methods(["GET"])
def services(request):
    context = cache.get("services_view_data")
    if not context:
        logger.info("Memcached cache miss for services view. Querying database.")
        context = {
            'content': ServicesPageContent.objects.first(),
            'service_items': list(ServiceItem.objects.all()),
        }
        cache.set("services_view_data", context, 3600)
    return render(request, 'services.html', context)


@require_http_methods(["GET"])
def portfolio(request):
    context = cache.get("portfolio_view_data")
    if not context:
        logger.info("Memcached cache miss for portfolio view. Querying database.")
        context = {
            'content': PortfolioPageContent.objects.first(),
            'projects': list(Project.objects.prefetch_related('images').all()),
        }
        cache.set("portfolio_view_data", context, 3600)
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

                # Admin notification
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

                # Automatic user reply
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

                # Admin notification
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

                # Automatic user reply
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

    context = cache.get("contact_view_data")
    if not context:
        logger.info("Memcached cache miss for contact view. Querying database.")
        context = {'content': ContactPageContent.objects.first()}
        cache.set("contact_view_data", context, 3600)
    return render(request, 'contact.html', context)


@require_http_methods(["GET"])
def privacy_policy(request):
    return render(request, 'policy.html')


@require_http_methods(["GET"])
def terms(request):
    return render(request, 'terms.html')

from django.http import HttpResponse

def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /siri/
Disallow: /static/admin/

Host: https://valgusdesigns.com
Sitemap: https://valgusdesigns.com/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")