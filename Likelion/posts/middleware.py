import logging
from datetime import datetime

logger = logging.getLogger("django.request")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"[{datetime.now()}] {request.method} {request.get_full_path()}")
        response = self.get_response(request)
        return response