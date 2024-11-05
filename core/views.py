from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_api_key.permissions import HasAPIKey


def index(request):
    return render(request, "core/base.html")


def trigger_error(request):
    division_by_zero = 1 / 0



class HelloWorldView(APIView):
    permission_classes = [HasAPIKey]
    def get(self, request):
        return Response({"message": "Hello, from Identity Server"}, status=status.HTTP_200_OK)

