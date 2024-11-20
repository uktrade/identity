from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def index(request):
    return render(request, "core/base.html")


def trigger_error(request):
    division_by_zero = 1 / 0
