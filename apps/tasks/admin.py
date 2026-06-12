from django.contrib import admin
from .models.tasks import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignee', 'created_by', 'status', 'proyecto', 'due_date', 'created_at')
    list_filter = ('status', 'is_important')
    search_fields = ('title', 'assignee__username', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Task, TaskAdmin)
