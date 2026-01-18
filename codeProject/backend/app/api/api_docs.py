"""
API Documentation and Information Module
Provides endpoints and information about API versions and usage
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/docs/info", summary="API Information")
async def api_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the API system
    """
    return {
        "title": "Restaurant Telegram Mini App API",
        "description": "Backend API for Telegram mini app with payment integration for restaurants",
        "versions": {
            "v1": {
                "status": "stable",
                "features": ["Basic CRUD operations", "User management", "Menu management", "Order processing"],
                "documentation": "/api/v1/docs"
            },
            "v2": {
                "status": "stable", 
                "features": ["Enhanced security", "Improved performance", "Additional analytics", "Better error handling"],
                "documentation": "/api/v2/docs"
            }
        },
        "base_url": "/api/{version}",
        "supported_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "authentication": "JWT tokens and Telegram authentication",
        "rate_limiting": "Available per client IP"
    }


@router.get("/versions", summary="Available API Versions")
async def available_versions() -> Dict[str, Any]:
    """
    List all available API versions with their status and endpoints
    """
    return {
        "versions": [
            {
                "version": "v1",
                "status": "active",
                "release_date": "2024-01-01",
                "end_of_life": "2026-12-31",
                "deprecated": False,
                "endpoints": "/api/v1/*"
            },
            {
                "version": "v2", 
                "status": "active",
                "release_date": "2024-06-01",
                "end_of_life": "2027-12-31",
                "deprecated": False,
                "endpoints": "/api/v2/*"
            }
        ],
        "latest_version": "v2",
        "default_version": "v1"
    }


@router.get("/usage-guide", summary="API Usage Guide")
async def usage_guide() -> Dict[str, Any]:
    """
    Provide guidance on how to use the API
    """
    return {
        "base_url_format": "https://your-domain.com/api/{version}/{endpoint}",
        "examples": {
            "v1_users": "/api/v1/users/",
            "v2_menu": "/api/v2/menu/",
            "v1_orders": "/api/v1/orders/"
        },
        "headers": {
            "authorization": "Bearer {jwt_token} or Telegram authentication",
            "content_type": "application/json"
        },
        "version_selection": {
            "method_1": "URL path: /api/v1/endpoint vs /api/v2/endpoint",
            "method_2": "Query parameter: ?api-version=v1 (not implemented yet)",
            "method_3": "Header: X-API-Version: v1 (not implemented yet)"
        }
    }