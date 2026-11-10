from django.contrib import admin

# Register your models here.
# portal/admin.py
from django.contrib import admin
from app.admin import admin_site
from .models import Project, Invoice, Message

@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'progress_percentage', 'due_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'client__username', 'client__email')

@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'description', 'client__username', 'client__email')

@admin.register(Message, site=admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'client', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender_name', 'content', 'client__username', 'client__email')