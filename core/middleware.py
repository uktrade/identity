from django.views.decorators.cache import never_cache


def no_cache(get_response):
    """Applies Django's built-in cache header method to all requests"""

    @never_cache
    def middleware(request):
        response = get_response(request)
        response["Pragma"] = "no-cache"  # not handled by the built-in decorator
        return response

    return middleware
