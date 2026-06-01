"""DRF APIView with async handler support for Daphne/ASGI."""
from __future__ import annotations

import asyncio

from rest_framework.views import APIView as DRFAPIView


class APIView(DRFAPIView):
    """
    DRF APIView that correctly awaits async get/post/patch/... handlers.

    Stock DRF (including 3.15) calls handlers synchronously in dispatch, so
    `async def get` returns a coroutine object and ASGI responds with 500.
    """

    async def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            if asyncio.iscoroutinefunction(handler):
                response = await handler(request, *args, **kwargs)
            else:
                response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response
