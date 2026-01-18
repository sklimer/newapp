"""
API Version Selector Module
Provides centralized management of API versions and version selection logic
"""
from enum import Enum
from fastapi import FastAPI
from typing import Dict, Callable, Optional


class APIVersion(str, Enum):
    """Available API versions"""
    V1 = "v1"
    V2 = "v2"


def register_api_versions(
    app: FastAPI,
    enabled_versions: Optional[list[APIVersion]] = None,
    default_version: APIVersion = APIVersion.V1
) -> None:
    """
    Register API versions with the FastAPI application
    
    Args:
        app: FastAPI application instance
        enabled_versions: List of versions to enable (all if None)
        default_version: Default version to use if no specific version is requested
    """
    if enabled_versions is None:
        enabled_versions = [APIVersion.V1, APIVersion.V2]
    
    # Import routers inside the function to avoid circular imports
    from app.api.v1.api import api_router as v1_router
    from app.api.v2.api import api_router as v2_router
    from app.api.endpoints.admin import router as admin_router
    
    # Map versions to their routers
    version_routers: Dict[APIVersion, Callable] = {
        APIVersion.V1: lambda: v1_router,
        APIVersion.V2: lambda: v2_router,
    }
    
    # Register enabled versions
    for version in enabled_versions:
        if version in version_routers:
            router = version_routers[version]()
            app.include_router(router, prefix=f"/api/{version.value}")
    
    # Also include admin routes
    app.include_router(admin_router)


def get_api_version_from_request(request) -> APIVersion:
    """
    Extract API version from request
    This can be extended to parse version from headers, query params, etc.
    """
    # For now, we'll implement basic path-based version detection
    path_parts = request.url.path.split('/')
    if len(path_parts) >= 3 and path_parts[2].startswith('v'):
        version_part = path_parts[2].replace('v', '').split('/')[0]
        try:
            return APIVersion(version_part)
        except ValueError:
            pass
    
    # Default to V1 if no version specified
    return APIVersion.V1


def get_available_versions() -> list[str]:
    """Return list of available API versions as strings"""
    return [version.value for version in APIVersion]