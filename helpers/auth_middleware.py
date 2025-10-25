from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from helpers.jwt_auth import verify_token
from typing import Dict, Any

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = verify_token(token)
    
    # Extract user information from token
    user_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": user_id,
        "email": email,
        "name": name
    }
