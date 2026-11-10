from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

local_storage = FileSystemStorage(location='/var/www/valgusdesigns/media', base_url='/media/')

class Project(models.Model):
    STATUS_CHOICES = [
        ('Kickoff', 'Kickoff'),
        ('In Progress', 'In Progress'),
        ('In Review', 'In Review'),
        ('Delivered', 'Delivered'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Kickoff', blank=True, null=True)
    progress_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or 'Untitled Project'} - {self.client.username if self.client else 'No Client'}"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Due', 'Due'),
        ('Paid', 'Paid'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices', blank=True, null=True)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Due', blank=True, null=True)
    receipt_file = models.FileField(upload_to='receipts/', storage=local_storage, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number or 'No Invoice #'} - {self.client.username if self.client else 'No Client'}"


class Message(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_messages', blank=True, null=True)
    sender_name = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender_name or 'Unknown'} to {self.client.username if self.client else 'No Client'}"