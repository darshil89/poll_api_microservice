from fastapi import APIRouter, Depends, HTTPException
from controllers.poll import create_poll, get_poll_by_id, get_poll_by_user_id, get_all_polls
from models.poll import Poll, Option, Vote, Like
from helpers.auth_middleware import get_current_user
from typing import Dict, Any

router = APIRouter()

url_prefix = "/api/poll"

@router.post(f"{url_prefix}/create-poll")
async def create_poll_route(poll: Poll, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return await create_poll(poll, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get(f"{url_prefix}/get-poll-by-id/{{poll_id}}") 
async def get_poll_by_id_route(poll_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return await get_poll_by_id(poll_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get(f"{url_prefix}/get-poll-by-user-id/{{user_id}}")
async def get_poll_by_user_id_route(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        # Verify user can only access their own polls
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: Cannot access other user's polls")
        return await get_poll_by_user_id(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get(f"{url_prefix}/get-all-polls")
async def get_all_polls_route(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return await get_all_polls()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")