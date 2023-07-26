# Third-Party
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import auth
from django import conf

class HomePage(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "sss/home.html"

    def get(self, request, *args, **kwargs):
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)