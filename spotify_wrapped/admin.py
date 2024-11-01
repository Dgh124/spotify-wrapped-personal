from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for managing feedback submissions.

    Provides list display, filters, and search functionality to easily access and manage feedback data.
    """
    list_display = ('name', 'email', 'submitted')
    list_filter = ('submitted',)
    search_fields = ('name', 'email', 'message')