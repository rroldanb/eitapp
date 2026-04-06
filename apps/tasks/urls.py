from django.urls import path
from .views.views import *

urlpatterns = [

    path('', tasks, name='tasks'),
    path('completed/', tasks_completed, name='tasks_completed'),
    path('create/', create_task, name='create_task'),
    path('<uuid:task_id>/', task_detail, name='task_detail'),
    path('<uuid:task_id>/complete/', complete_task, name='complete_task'),
    path('<uuid:task_id>/delete/', delete_task, name='delete_task'),
]