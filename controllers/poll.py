from prisma import Prisma
from fastapi import HTTPException, status
from dotenv import load_dotenv
from models.poll import Poll, Option, Vote, Like
from typing import Dict, Any
load_dotenv()


# create poll
async def create_poll(poll: Poll, current_user: Dict[str, Any]):
    prisma = Prisma()
    try:
        await prisma.connect()
        created_poll = await prisma.poll.create(
            data= {
                "question": poll.question,
                "userId": current_user["id"],
            }
        )

        # Create options if they exist
        if hasattr(poll, 'options') and poll.options:
            for option in poll.options:
                await prisma.option.create(
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
    finally:
        await prisma.disconnect()


# get poll by id
async def get_poll_by_id(poll_id: str):
    prisma = Prisma()
    try:
        await prisma.connect()
        poll = await prisma.poll.find_unique(
            where={"id": poll_id}
        )
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        return poll.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")
    finally:
        await prisma.disconnect()


# get poll by user id
async def get_poll_by_user_id(user_id: str):
    prisma = Prisma()
    try:
        await prisma.connect()
        polls = await prisma.poll.find_many(
            where={"userId": user_id}
        )
        return [poll.model_dump() for poll in polls]
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")
    finally:
        await prisma.disconnect()

# get all polls
async def get_all_polls():
    prisma = Prisma()
    try:
        await prisma.connect()
        polls = await prisma.poll.find_many()
        return [poll.model_dump() for poll in polls]
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")



# vote on a poll
async def vote_on_poll(poll_id: str, option_id: str, current_user: Dict[str, Any]):
    prisma = Prisma()
    try:
        await prisma.connect()
        created_vote = await prisma.vote.create(
            data={
                "userId": current_user["id"],
                "optionId": option_id,
                "pollId": poll_id,
            }
        )
        return created_vote.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")
    finally:
        await prisma.disconnect()

# like a poll
async def like_poll(poll_id: str, current_user: Dict[str, Any]):
    prisma = Prisma()
    try:
        await prisma.connect()
        created_like = await prisma.like.create(
            data={
                "userId": current_user["id"],
                "pollId": poll_id,
            }
        )
        return created_like.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")
    finally:
        await prisma.disconnect()