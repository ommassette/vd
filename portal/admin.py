# portal/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from app.admin import admin_site
from .models import Project, Invoice, Message

class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        password = form.cleaned_data.get('password')
        if password and not password.startswith('pbkdf2_'):
            obj.set_password(password)
        super().save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(User, UserAdmin, site=admin_site)

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
    