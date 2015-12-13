"""
Adapted with permission from ReportLab's DocEngine framework
"""



import logging
import traceback
from django.views.debug import ExceptionReporter, get_exception_reporter_filter

class DbLogHandler(logging.Handler):
    def emit(self, record):
        from models import Log
        try:
            request = record.request
            filter = get_exception_reporter_filter(request)
            request_repr = filter.get_request_repr(request)
        except Exception:
            request = None
            request_repr = "Request repr() unavailable."

        if record.exc_info:
            exc_info = record.exc_info
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            exc_info = (None, record.getMessage(), None)
            stack_trace = "No stack trace available"

        rec = Log(level = record.levelname,
                  message = record.getMessage(),
                  request = request_repr,
                  traceback = stack_trace
              )
        rec.save()
