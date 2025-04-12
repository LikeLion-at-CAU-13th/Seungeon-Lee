import logging
from datetime import datetime

logger = logging.getLogger("django.request")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 요청 URL을 한 줄에 포함시켜서 기록
        logger.info(
            '[{}] {} {}'.format(datetime.now(), request.method, request.get_full_path()),
            extra={'request_url': request.get_full_path()}
        )

        response = self.get_response(request)
        return response