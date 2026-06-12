from django.urls import path
from .views.views import *

urlpatterns = [
    path('', task_list, name='task_list'),
    path('create/', create_task, name='create_task'),
    path('bulk-create/', bulk_create_tasks, name='bulk_create_tasks'),
    path('<uuid:task_id>/', task_detail, name='task_detail'),
    path('<uuid:task_id>/complete/', complete_task, name='complete_task'),
    path('<uuid:task_id>/delete/', delete_task, name='delete_task'),
]
