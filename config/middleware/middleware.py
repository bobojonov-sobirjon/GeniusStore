from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
import logging

from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


# Middleware for handling JSON error responses
class JsonErrorResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the view function
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if not request.path.startswith('/api/'):
            return None

        # Convert common exceptions to correct HTTP codes instead of always 500.
        if isinstance(exception, Http404):
            return JsonResponse({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exception, ObjectDoesNotExist):
            return JsonResponse({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exception, ValidationError) and request.path.startswith('/api/'):
            text = ' '.join(str(m) for m in getattr(exception, 'messages', [exception]))
            if 'uuid' in text.lower():
                return JsonResponse({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exception, APIException):
            detail = getattr(exception, "detail", None)
            return JsonResponse({"detail": detail if detail is not None else "Ошибка запроса."}, status=exception.status_code)

        logger.exception('Unhandled API error on %s', request.path)

        # Fallback
        return JsonResponse({"detail": "Внутренняя ошибка сервера."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Middleware for handling custom 404 responses
class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the view function
        response = self.get_response(request)

        if self._should_skip_json_404(request):
            return response

        if response is None:
            return self.handle_404(request)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return self.handle_404(request)

        return response

    @staticmethod
    def _should_skip_json_404(request) -> bool:
        path = request.path
        if path.startswith('/api/'):
            return True
        html_prefixes = ('/admin/', '/docs/', '/redoc/', '/schema/', '/static/', '/media/')
        return path.startswith(html_prefixes)

    def handle_404(self, request):
        # Handle 404 error and return JSON response
        data = {"detail": "Страница не найдена."}
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

