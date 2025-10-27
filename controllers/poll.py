from prisma import Prisma
from fastapi import HTTPException, status
from dotenv import load_dotenv
from models.poll import Poll
from typing import Dict, Any, List
from models.poll import PollResponse, VoteResponse, LikeResponse
from helpers.db import prisma_client
load_dotenv()


# create poll
async def create_poll(poll: Poll, current_user: Dict[str, Any]):
    try:
        created_poll = await prisma_client.poll.create(
            data= {
                "question": poll.question,
                "userId": current_user["id"],
            }
        )

        # Create options if they exist
        if hasattr(poll, 'options') and poll.options:
            for option in poll.options:
                await prisma_client.option.create(
                    data={
                        "text": option.text,
                        "pollId": created_poll.id,
                    }
                )

        return created_poll.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {error_message}"
        )


# get poll by id
async def get_poll_by_id(poll_id: str) -> PollResponse:
    try:
        # include options, votes, and likes
        poll = await prisma_client.poll.find_unique(
            where={"id": poll_id},
            include={
                "options": {
                    "include": {
                        "votes": True,
                    }
                },
                "likes": True,
            }
        )
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        return PollResponse.model_dump(poll)
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")


# get poll by user id
async def get_poll_by_user_id(user_id: str) -> List[PollResponse]:
    try:
        polls = await prisma_client.poll.find_many(
            where={"userId": user_id},
            include={
                "options": {
                    "include": {
                        "votes": True,
                    }
                },
                "likes": True,
            }
        )
        return [PollResponse.model_dump(poll) for poll in polls]
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")


# get all polls
async def get_all_polls() -> List[PollResponse]:
    try:
        polls = await prisma_client.poll.find_many(
            include={
                "options": {
                    "include": {
                        "votes": True,
                    }
                },
                "likes": True,
            }
        )
        return [PollResponse.model_dump(poll) for poll in polls]
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")



# vote on a poll
async def vote_on_poll(poll_id: str, option_id: str, current_user: Dict[str, Any]) -> VoteResponse:
    try:
        # check if user has already voted on the poll
        existing_vote = await prisma_client.vote.find_first(
            where={"userId": current_user["id"], "optionId": option_id, "pollId": poll_id}
        )
        if existing_vote:
            raise HTTPException(status_code=400, detail="User has already voted on this poll")
        created_vote = await prisma_client.vote.create(
            data={
                "userId": current_user["id"],
                "optionId": option_id,
                "pollId": poll_id,
            }
        )
        return VoteResponse.model_dump(created_vote)
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")

# like a poll
async def like_poll(poll_id: str, current_user: Dict[str, Any]) -> LikeResponse:
    try:
        # check if user has already liked the poll
        existing_like = await prisma_client.like.find_first(
            where={"userId": current_user["id"], "pollId": poll_id}
        )
        if existing_like:
            raise HTTPException(status_code=400, detail="User has already liked this poll")
        created_like = await prisma_client.like.create(
            data={
                "userId": current_user["id"],
                "pollId": poll_id,
            }
        )
        return LikeResponse.model_dump(created_like)
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")