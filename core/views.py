from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def index(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    return render(request, "core/base.html")


def trigger_error(request):
    division_by_zero = 1 / 0
