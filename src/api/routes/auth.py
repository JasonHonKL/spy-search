from fastapi import APIRouter, HTTPException , Depends
from pydantic import BaseModel
from ..auth.auth import GoogleOAuth, JWTHandler, TokenData , get_current_user , verify_google_token

router = APIRouter(prefix="/auth", tags=["authentication"])

class GoogleTokenRequest(BaseModel):
    token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: TokenData

@router.post("/google/callback", response_model=LoginResponse)
async def google_login_callback(request: GoogleTokenRequest):
    """Handle Google OAuth callback and return JWT token"""
    
    # Verify Google token
    user_info = GoogleOAuth.verify_google_token(request.token)
    
    # Create JWT token
    jwt_token = JWTHandler.create_access_token(data=user_info)
    
    return LoginResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=TokenData(**user_info)
    )

@router.get("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback with authorization code"""
    
    # Exchange code for token
    token_response = GoogleOAuth.exchange_code_for_token(code)
    
    # Get user info using access token
    user_info = GoogleOAuth.get_user_info(token_response["access_token"])
    
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