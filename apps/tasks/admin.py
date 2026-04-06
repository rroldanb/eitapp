from django.contrib import admin
from .models.tasks import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_completed', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

# Register your models here.
admin.site.register(Task, TaskAdmin)
