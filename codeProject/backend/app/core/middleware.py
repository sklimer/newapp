from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .telegram import is_running_in_telegram_web_app


class TelegramWebAppMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure certain routes only accept requests from Telegram Web App
    """
    def __init__(self, app, restricted_paths=None):
        super().__init__(app)
        self.restricted_paths = restricted_paths or [
            "/api/v1/users/",
            "/api/v1/orders/", 
            "/api/v1/cart/",
            "/api/v1/profile/",
            "/api/v1/payments/"
        ]

    async def dispatch(self, request: Request, call_next):
        # Check if the path is restricted and requires Telegram environment
        path = request.url.path
        is_restricted_path = any(path.startswith(restricted_path) for restricted_path in self.restricted_paths)
        
        if is_restricted_path:
            # Import here to avoid circular imports
            from .telegram import is_running_in_telegram_web_app
            if not is_running_in_telegram_web_app(request):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "This endpoint is only accessible from Telegram Web App"}
                )
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing request {request.url}: {e}")
            # Re-raise the exception to maintain normal error handling
            raise