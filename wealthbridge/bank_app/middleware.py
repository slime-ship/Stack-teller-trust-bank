import logging
import traceback

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(
            "Unhandled exception\n"
            f"URL: {request.build_absolute_uri()}\n"
            f"Method: {request.method}\n"
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'}\n"
            f"Exception: {exception}\n\n"
            f"{traceback.format_exc()}"
        )

        # Returning None lets Django continue handling the exception
        return None
