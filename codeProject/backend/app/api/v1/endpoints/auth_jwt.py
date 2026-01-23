import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.api.deps import get_db, get_async_db
from app.core.security import get_or_create_user_from_telegram
from app.schemas.users import UserResponse
from app.core.config import settings
from app.core.telegram import validate_telegram_init_data, get_telegram_user_data
from app.models.users import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# JWT token helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT refresh token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh token lives longer than access token
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access"):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        
        # Check token type
        token_type_claim = payload.get("type")
        if token_type_claim != token_type:
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid token type: expected {token_type}, got {token_type_claim}"
            )
        
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set auth tokens in HTTP-only cookies"""
    # Set access token cookie (short-lived)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Use HTTPS in production
        samesite="strict",
        max_age=1800  # 30 minutes (same as ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Set refresh token cookie (longer-lived)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Use HTTPS in production
        samesite="strict",
        max_age=604800  # 7 days
    )


def clear_auth_cookies(response: Response):
    """Clear auth cookies"""
    response.set_cookie(key="access_token", value="", httponly=True, max_age=0)
    response.set_cookie(key="refresh_token", value="", httponly=True, max_age=0)


@router.post("/telegram-auth")
async def telegram_auth(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Authenticate user via Telegram Web App init data and return JWT tokens
    """
    logger.info("📱 Starting Telegram authentication flow")
    
    try:
        # Get init data from request body
        body = await request.json()
        init_data = body.get("initData") or body.get("init_data")
        
        if not init_data:
            logger.error("❌ No initData provided in request")
            raise HTTPException(status_code=400, detail="No initData provided")
        
        logger.info(f"📥 Received initData. Length: {len(init_data)} characters")
        
        # Validate init data signature using improved validation
        try:
            validate_telegram_init_data(init_data)
            logger.info("✅ Telegram init data signature validated")
        except Exception as e:
            logger.error(f"❌ Telegram init data validation failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid Telegram init data")
        
        # Extract user data from init data
        user_data = get_telegram_user_data(init_data)
        if not user_data or 'id' not in user_data:
            logger.error("❌ Could not extract user data from init data")
            raise HTTPException(status_code=400, detail="Invalid user data in init data")
        
        logger.info(f"👤 Extracted user data. Telegram ID: {user_data['id']}")
        
        # Get or create user in database
        db_user = await get_or_create_user_from_telegram(user_data, db)
        if not db_user:
            logger.error("❌ Failed to create/get user from database")
            raise HTTPException(status_code=500, detail="Failed to process user")
        
        logger.info(f"✅ User processed successfully. DB ID: {db_user.id}, Telegram ID: {db_user.telegram_id}")
        
        # Create JWT tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=7)  # 7 days
        
        access_token = create_access_token(
            data={"sub": str(db_user.id), "telegram_id": str(user_data['id'])},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(db_user.id), "telegram_id": str(user_data['id'])},
            expires_delta=refresh_token_expires
        )
        
        logger.info(f"🔐 JWT tokens created. Access token expires in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        # Prepare response
        response_data = {
            "success": True,
            "user": UserResponse.from_orm(db_user),
            "telegram": {
                "user_id": user_data.get('id'),
                "username": user_data.get('username'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "language_code": user_data.get('language_code'),
                "is_premium": user_data.get('is_premium', False)
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
            }
        }
        
        # Create response with tokens in cookies
        response = JSONResponse(content=response_data)
        set_auth_cookies(response, access_token, refresh_token)
        
        logger.info(f"✅ Telegram authentication completed successfully for user ID: {db_user.id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during Telegram authentication: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh-token")
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refresh access token using refresh token
    """
    logger.info("🔄 Starting token refresh flow")
    
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            logger.error("❌ No refresh token in cookies")
            raise HTTPException(status_code=401, detail="No refresh token provided")
        
        logger.info("🔍 Validating refresh token")
        
        # Verify refresh token
        try:
            payload = verify_token(refresh_token, token_type="refresh")
            user_id = payload.get("sub")
            telegram_id = payload.get("telegram_id")
            
            if not user_id:
                logger.error("❌ No user ID in refresh token payload")
                raise HTTPException(status_code=401, detail="Invalid refresh token")
                
        except HTTPException:
            # If token verification fails, clear cookies and return error
            response = JSONResponse(content={"detail": "Invalid refresh token"}, status_code=401)
            clear_auth_cookies(response)
            return response
        
        logger.info(f"✅ Refresh token validated. User ID: {user_id}, Telegram ID: {telegram_id}")
        
        # Verify user still exists in database
        user = await db.get(User, int(user_id))
        if not user or not user.is_active:
            logger.error(f"❌ User {user_id} not found or inactive")
            response = JSONResponse(content={"detail": "User no longer exists"}, status_code=401)
            clear_auth_cookies(response)
            return response
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "telegram_id": telegram_id},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token (optional: rotate refresh tokens)
        refresh_token_expires = timedelta(days=7)
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id), "telegram_id": telegram_id},
            expires_delta=refresh_token_expires
        )
        
        logger.info("✅ New tokens generated")
        
        # Update response with new tokens
        response_data = {
            "success": True,
            "tokens": {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
        response = JSONResponse(content=response_data)
        set_auth_cookies(response, access_token, new_refresh_token)
        
        logger.info(f"✅ Token refresh completed successfully for user ID: {user.id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during token refresh: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(request: Request):
    """
    Logout user and clear auth cookies
    """
    logger.info("🚪 Starting logout process")
    
    try:
        # Clear auth cookies
        response = JSONResponse(content={"success": True, "message": "Logged out successfully"})
        clear_auth_cookies(response)
        
        logger.info("✅ Logout completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error during logout: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current authenticated user info
    """
    logger.info("👤 Request for current user info")
    
    try:
        # Get access token from cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.error("❌ No access token in cookies")
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        logger.info("🔍 Validating access token")
        
        # Verify access token
        try:
            payload = verify_token(access_token, token_type="access")
            user_id = payload.get("sub")
            
            if not user_id:
                logger.error("❌ No user ID in access token payload")
                raise HTTPException(status_code=401, detail="Invalid access token")
                
        except HTTPException:
            raise
        except Exception:
            logger.error("❌ Access token validation failed")
            raise HTTPException(status_code=401, detail="Invalid access token")
        
        logger.info(f"✅ Access token validated. User ID: {user_id}")
        
        # Get user from database
        user = await db.get(User, int(user_id))
        if not user or not user.is_active:
            logger.error(f"❌ User {user_id} not found or inactive")
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.info(f"✅ Current user info retrieved. User ID: {user.id}")
        
        return {
            "success": True,
            "user": UserResponse.from_orm(user),
            "telegram_id": payload.get("telegram_id")
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/validate-session")
async def validate_session(request: Request):
    """
    Validate current session without returning user data
    """
    logger.info("🔍 Validating current session")
    
    try:
        # Get access token from cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.info("❌ No access token in cookies")
            return {"valid": False, "reason": "no_token"}
        
        # Verify access token
        try:
            payload = verify_token(access_token, token_type="access")
            user_id = payload.get("sub")
            
            if not user_id:
                logger.info("❌ Invalid token - no user ID")
                return {"valid": False, "reason": "invalid_token"}
                
        except Exception:
            logger.info("❌ Access token validation failed")
            return {"valid": False, "reason": "invalid_token"}
        
        logger.info(f"✅ Session validated. User ID: {user_id}")
        return {"valid": True, "user_id": user_id}
        
    except Exception as e:
        logger.error(f"❌ Unexpected error validating session: {str(e)}", exc_info=True)
        return {"valid": False, "reason": "server_error"}