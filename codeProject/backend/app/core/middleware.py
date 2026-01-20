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
            "/api/v1/profile/",
            "/api/v1/payments/"
        ]
        # Paths that require Telegram Web App but should have more flexible checking
        self.flexible_cart_paths = [
            "/api/v1/cart/"
        ]
        # Paths that should be accessible without Telegram Web App requirements
        self.public_paths = [
            "/api/v1/menu/"
        ]

    async def dispatch(self, request: Request, call_next):
        # Check if the path is restricted and requires Telegram environment
        path = request.url.path

        # Check for public paths that should always be accessible
        is_public_path = any(path.startswith(public_path) for public_path in self.public_paths)

        # If it's a public path, allow access without Telegram restrictions
        if is_public_path:
            pass
        else:
            # Check for regular restricted paths
            is_restricted_path = any(path.startswith(restricted_path) for restricted_path in self.restricted_paths)

            # Check for cart paths specifically (these may have alternative auth methods)
            is_cart_path = any(path.startswith(cart_path) for cart_path in self.flexible_cart_paths)

            if is_restricted_path:
                # Import here to avoid circular imports
                from .telegram import is_running_in_telegram_web_app
                if not is_running_in_telegram_web_app(request):
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "This endpoint is only accessible from Telegram Web App"}
                    )
            elif is_cart_path:
                # For cart paths, we'll allow external access but may apply other checks later
                # This allows frontend to access cart functionality
                pass

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