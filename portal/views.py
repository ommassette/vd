import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from .models import Project, Invoice, Message

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def portal_login(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    error_message = None

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"Client {user.username} logged into portal.")
            return redirect('portal:dashboard')
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            error_message = "Invalid username or password."

    return render(request, 'portal/login.html', {'error': error_message})


@require_http_methods(["POST", "GET"])
def portal_logout(request):
    if request.user.is_authenticated:
        logger.info(f"Client {request.user.username} logged out.")
        logout(request)
    return redirect('portal:login')


@login_required
@require_GET
def portal_dashboard(request):
    user = request.user
    
    projects = Project.objects.filter(client=user).select_related('client')
    invoices = Invoice.objects.filter(client=user).select_related('client')
    messages = Message.objects.filter(client=user).select_related('client')

    active_projects_count = projects.exclude(status='Delivered').count()
    pending_invoices_count = invoices.filter(status='Due').count()
    unread_messages_count = messages.filter(is_read=False).count()
    delivered_projects_count = projects.filter(status='Delivered').count()

    context = {
        'projects': projects,
        'invoices': invoices,
        'messages': messages,
        'stats': {
            'active_projects': f"{active_projects_count:02d}",
            'pending_invoices': f"{pending_invoices_count:02d}",
            'unread_messages': f"{unread_messages_count:02d}",
            'delivered': f"{delivered_projects_count:02d}",
        }
    }
    
    return render(request, 'portal/index.html', context)