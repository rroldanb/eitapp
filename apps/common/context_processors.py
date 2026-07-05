from django.utils import timezone

from apps.tasks.models.tasks import Task, TaskStatus
from apps.usuarios.models import Role
from apps.usuarios.utils import get_user_role


def pending_tasks(request):
    if not request.user.is_authenticated:
        return {
            "pending_tasks_count": 0,
            "overdue_tasks_count": 0,
            "pending_tasks": [],
        }

    role = get_user_role(request.user)
    if role >= Role.ADMIN:
        tasks = Task.objects.all()
    elif role >= Role.MODELADOR:
        tasks = Task.objects.filter(created_by=request.user)
    else:
        tasks = Task.objects.filter(assignee=request.user)

    pending = tasks.filter(status=TaskStatus.PENDIENTE)
    now = timezone.now()
    overdue = pending.filter(due_date__lt=now)

    show_modal = (
        request.session.pop("show_pending_modal", False)
        if not request.headers.get("HX-Request")
        else False
    )

    return {
        "pending_tasks_count": pending.count(),
        "overdue_tasks_count": overdue.count(),
        "pending_tasks": pending.select_related("assignee", "created_by")[:5],
        "now": now,
        "show_pending_modal": show_modal,
    }
