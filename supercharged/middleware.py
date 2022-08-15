from django.conf import settings


class BootstrapThemeMiddleware:
    """
    A simple middleware to enable a bootstrap theme.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        theme = hasattr(settings, "BOOTSTRAP_THEME") and getattr(
            settings, "BOOTSTRAP_THEME"
        )
        if theme:
            response.context_data["BOOTSTRAP_THEME"] = theme
        return response
