import logging
from datetime import datetime

logger = logging.getLogger("django.request")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 요청 URL을 로그에 포함하여 기록
        logger.info('[{}] {} {}'.format(datetime.now(), request.method, request.get_full_path()))

        response = self.get_response(request)
        return response