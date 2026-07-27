from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly
from apps.tasks.models.tasks import Task
from apps.tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAdminOrReadOnly]
