from django.contrib import admin
from .models import ScreenTimeLog


@admin.register(ScreenTimeLog)
class ScreenTimeLogAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'category', 'duration_minutes', 'date', 'get_productivity_impact']
    list_filter = ['category', 'date']
    search_fields = ['app_name']
    ordering = ['-date']