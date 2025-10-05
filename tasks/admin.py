from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'due_date', 'created_at', 'notify')
    list_filter = ('status', 'priority', 'notify')
    search_fields = ('title', 'description')