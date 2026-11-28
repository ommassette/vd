import logging
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from app.rag_engine import generate_chatbot_response
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    Article,
    ArticlePageContent,
    CaseStudy,
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
    ConsentLog,
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
    projects = list(
        Project.objects
        .select_related('case_study')
        .prefetch_related('images')
        .all()
    )

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
            email = (request.POST.get('email') or '').strip()
            phone = (request.POST.get('phone') or '').strip()

            if service and (email or phone):
                ContactMessage.objects.create(
                    service=service,
                    email=email or None,
                    phone=phone or None,
                )
                logger.info("Contact message saved successfully.")

                contact_lines = [f"Service: {service}"]
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

                if email:
                    try:
                        send_mail(
                            subject="We received your inquiry - Valgus Designs",
                            message=(
                                f"Hello,\n\n"
                                f"Thank you for reaching out to Valgus Designs.\n\n"
                                f"We've received your request regarding:\n"
                                f"  • Service: {service}\n\n"
                                f"Our team will review your inquiry and get back to you shortly.\n\n"
                                f"Best regards,\n"
                                f"Valgus Designs Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send client auto-reply: {e}")

                if email:
                    request.session['contact_success'] = "Message sent successfully. Check your inbox, we'll be in touch."
                else:
                    request.session['contact_success'] = "Thanks! We'll call you shortly."

                return redirect('contact')
            else:
                request.session['contact_error'] = "Please complete all steps and provide a phone number or email."
                return redirect('contact')

    contact_success = request.session.pop('contact_success', None)
    contact_error = request.session.pop('contact_error', None)

    context = {
        'content': ContactPageContent.objects.first(),
        'service_items': list(ServiceItem.objects.all()),
        'contact_success': contact_success,
        'contact_error': contact_error,
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
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /static/admin/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@cache_page(60 * 15)
@require_http_methods(["GET"])
def articles(request):
    context = {
        'content': ArticlePageContent.objects.first(),
        'articles': list(Article.objects.filter(is_published=True)),
    }
    return render(request, 'articles.html', context)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    context = {'article': article}
    return render(request, 'article.html', context)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def case_study_detail(request, project_id):
    case_study = get_object_or_404(
        CaseStudy.objects
        .select_related('project')
        .prefetch_related(
            'scope_tags',
            'color_swatches',
            'typefaces',
            'ui_components',
        ),
        project_id=project_id,
    )

    return render(request, 'case_study.html', {'case_study': case_study})


@csrf_exempt
@require_POST
def chatbot_query_view(request):
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
            question = data.get("message", "").strip()
        else:
            question = request.POST.get("message", "").strip()

        if not question:
            return JsonResponse({"error": "Empty message"}, status=400)

        answer_text = generate_chatbot_response(question)
        return JsonResponse({"response": answer_text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@cache_page(60 * 15)
@require_http_methods(["GET"])
def impressum(request):
    return render(request, 'impressum.html')


def _get_client_ip(request):
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return cf_ip.strip()
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


@require_POST
def log_consent(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Invalid JSON received on consent log endpoint.")
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    consent_id = str(data.get("consent_id", "")).strip()[:64]
    action = str(data.get("action", "")).strip()[:32]
    page_path = str(data.get("page_path", "/")).strip()[:255] or "/"
    fonts_and_media = bool(data.get("fonts_and_media", False))

    allowed_actions = {"accept_all", "reject_all", "custom", "update"}
    if not consent_id or action not in allowed_actions:
        logger.warning("Malformed consent log request: action=%s", action)
        return JsonResponse({"error": "Invalid consent payload"}, status=400)

    ip_address = _get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    try:
        ConsentLog.objects.create(
            consent_id=consent_id,
            essential=True,
            fonts_and_media=fonts_and_media,
            action=action,
            page_path=page_path,
            ip_hash=ConsentLog.hash_value(ip_address),
            user_agent_hash=ConsentLog.hash_value(user_agent),
        )
        logger.info("Consent logged: id=%s action=%s media=%s", consent_id[:8], action, fonts_and_media)
        return JsonResponse({"status": "logged", "fonts_and_media": fonts_and_media})
    except Exception as exc:
        logger.error("Failed to save consent log: %s", exc)
        return JsonResponse({"error": "Failed to record consent"}, status=500)