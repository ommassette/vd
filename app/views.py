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
        if 'service' in request.POST:
            service = request.POST.get('service')
            timeline = request.POST.get('timeline')
            email = (request.POST.get('email') or '').strip()
            phone = (request.POST.get('phone') or '').strip()

            if service and timeline and (email or phone):
                ContactMessage.objects.create(
                    service=service,
                    timeline=timeline,
                    email=email or None,
                    phone=phone or None,
                )
                logger.info("Contact message saved successfully.")

                # ---- Admin notification ----
                contact_lines = [f"Service: {service}", f"Timeline: {timeline}"]
                if email:
                    contact_lines.append(f"Email: {email}")
                if phone:
                    contact_lines.append(f"Phone: {phone}")

                try:
                    send_mail(
                        subject=f"New Contact Inquiry: {service}",
                        message="\n".join(contact_lines),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send admin contact notification: {e}")

                # ---- Client auto-reply (only if they gave an email) ----
                if email:
                    try:
                        send_mail(
                            subject="We received your inquiry - Valgus Designs",
                            message=(
                                f"Hello,\n\n"
                                f"Thank you for reaching out to Valgus Designs.\n\n"
                                f"We've received your request regarding:\n"
                                f"  • Service: {service}\n"
                                f"  • Timeline: {timeline}\n\n"
                                f"Our team will review your inquiry and get back to you shortly.\n\n"
                                f"Best regards,\n"
                                f"Valgus Designs Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=True,
                        )
                        logger.info(f"Auto-reply sent to {email}.")
                    except Exception as e:
                        logger.error(f"Failed to send client auto-reply: {e}")

                # ---- Tailored success message ----
                if email:
                    messages.success(
                        request,
                        "Message sent successfully. Check your inbox — we'll be in touch."
                    )
                else:
                    messages.success(
                        request,
                        "Thanks! We'll call you shortly."
                    )
                return redirect('contact')
            else:
                messages.error(
                    request,
                    "Please complete all steps and provide a phone number or email."
                )

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

    context = {
        'content': ContactPageContent.objects.first(),
        'service_items': list(ServiceItem.objects.all()),
    }
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