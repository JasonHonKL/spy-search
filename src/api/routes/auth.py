from fastapi import APIRouter, HTTPException , Depends
from pydantic import BaseModel
from ..auth.auth import GoogleOAuth, JWTHandler, TokenData , get_current_user , verify_google_token

router = APIRouter()

class GoogleTokenRequest(BaseModel):
    token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: TokenData

@router.get("/auth/google/callback")
async def google_login_callback(code: str):
    # Use the authorization code to get access token from Google
    tokens = GoogleOAuth.exchange_code_for_token(code)
    user_info = GoogleOAuth.get_user_info(tokens["access_token"])
    
    jwt_token = JWTHandler.create_access_token(data=user_info)
    
    return LoginResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=TokenData(**user_info)
    )

@router.post("/google/exchange-code")
async def google_exchange_code(request: dict):
    """Exchange authorization code for tokens"""
    code = request.get("code")
    
    # Exchange code for token
    tokens = GoogleOAuth.exchange_code_for_token(code)
    user_info = GoogleOAuth.get_user_info(tokens["access_token"])
    # Create JWT token
    jwt_token = JWTHandler.create_access_token(data=user_info)
    
    return LoginResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=TokenData(**user_info)
    )


@router.get("/verify")
async def verify_jwt_token(current_user: dict = Depends(get_current_user)):
    """Verify if JWT token is still valid"""
    return {"valid": True, "user": current_user}

@router.get("/google/login")
async def google_login():
    """Get Google OAuth login URL"""
    auth_url = GoogleOAuth.get_google_auth_url()
    return {"auth_url": auth_url}