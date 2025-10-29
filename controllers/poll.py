from prisma import Prisma
from fastapi import HTTPException, status
from dotenv import load_dotenv
from models.poll import PollCreate, PollResponse
import json
from typing import Dict, Any, List
from helpers.db import prisma_client, redis_client
import asyncio
load_dotenv()

# create poll
async def create_poll(poll: PollCreate, current_user: Dict[str, Any]):
    try:
        created_poll = await prisma_client.poll.create(
            data= {
                "question": poll.question,
                "userId": current_user["id"],
                "email": current_user["email"],
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
async def get_poll_by_id(poll_id: str, user_id: str) -> PollResponse:
    try:
        # include options, votes, and likes
        poll = await prisma_client.poll.find_unique(
            where={"id": poll_id},
            include={
                "options": True,
            }
        )
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        # get like count for the poll
        redis_key = [f"poll:{poll_id}:likes"]
        option_ids = [option.id for option in poll.options]
        redis_key.extend([f"poll:{poll_id}:option:{option_id}" for option_id in option_ids])

        # all count in one go
        counts, user_vote, user_like = await asyncio.gather(
            redis_client.mget(redis_key),
            prisma_client.vote.find_first(
                where={"userId": user_id, "pollId": poll_id}
            ),
            prisma_client.like.find_first(
                where={"userId": user_id, "pollId": poll_id}
            )
        )

        final_counts = {
            "likes": int(counts[0] or 0),
        }

        for i, option_id in enumerate(option_ids):
            final_counts[option_id] = int(counts[i+1] or 0)

        poll_dict = poll.model_dump()
        poll_dict["counts"] = final_counts

        poll_dict["userHasVoted"] = user_vote.optionId if user_vote else None
        poll_dict["userHasLiked"] = user_like if user_like else None

        return PollResponse(**poll_dict)
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
                "options": True
            }
        )

        all_redis_keys = []
        poll_key_map = {} 
        
        for poll in polls:
            poll_keys = [f"poll:{poll.id}:likes"]
            poll_key_map[poll.id] = {"like_key": poll_keys[0], "option_keys": []}
            
            for option in poll.options:
                opt_key = f"poll:{poll.id}:option:{option.id}"
                poll_keys.append(opt_key)
                poll_key_map[poll.id]["option_keys"].append((option.id, opt_key))
                
            all_redis_keys.extend(poll_keys)

        all_counts = await redis_client.mget(all_redis_keys)
        counts_dict = dict(zip(all_redis_keys, all_counts))

        response_list = []
        for poll in polls:
            final_counts = {}
            key_map = poll_key_map[poll.id]
            
            # Get like count
            final_counts["likes"] = int(counts_dict.get(key_map["like_key"]) or 0)
            
            # Get option counts
            for option_id, opt_key in key_map["option_keys"]:
                final_counts[option_id] = int(counts_dict.get(opt_key) or 0)

            # user specific counts
            user_votes = await prisma_client.vote.find_many(where={"userId": user_id})
            user_likes = await prisma_client.like.find_many(where={"userId": user_id})

            user_voted_poll_ids = {v.pollId: v.optionId for v in user_votes}
            user_liked_poll_ids = {l.pollId for l in user_likes}

            
            poll_dict = poll.model_dump()
            poll_dict["counts"] = final_counts

            poll_dict["userHasVoted"] = user_voted_poll_ids.get(poll.id, None)
            poll_dict["userHasLiked"] = poll.id in user_liked_poll_ids

            response_list.append(PollResponse(**poll_dict))
            
        return response_list

    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")


# get all polls
async def get_all_polls(user_id: str) -> List[PollResponse]:
    try:
        polls = await prisma_client.poll.find_many(
            include={
                "options": True,
            }
        )

        # get likes and votes counts each option
        all_redis_keys = []
        poll_key_map = {} 
        
        for poll in polls:
            poll_keys = [f"poll:{poll.id}:likes"]
            poll_key_map[poll.id] = {"like_key": poll_keys[0], "option_keys": []}
            
            for option in poll.options:
                opt_key = f"poll:{poll.id}:option:{option.id}"
                poll_keys.append(opt_key)
                poll_key_map[poll.id]["option_keys"].append((option.id, opt_key))
                
            all_redis_keys.extend(poll_keys)

        all_counts = await redis_client.mget(all_redis_keys)
        counts_dict = dict(zip(all_redis_keys, all_counts))

        response_list = []
        for poll in polls:
            final_counts = {}
            key_map = poll_key_map[poll.id]
            
            # Get like count
            final_counts["likes"] = int(counts_dict.get(key_map["like_key"]) or 0)
            
            # Get option counts
            for option_id, opt_key in key_map["option_keys"]:
                final_counts[option_id] = int(counts_dict.get(opt_key) or 0)

            # user specific counts
            user_votes = await prisma_client.vote.find_many(where={"userId": user_id})
            user_likes = await prisma_client.like.find_many(where={"userId": user_id})

            user_voted_poll_ids = {v.pollId: v.optionId for v in user_votes}
            user_liked_poll_ids = {l.pollId for l in user_likes}

            
            poll_dict = poll.model_dump()
            poll_dict["counts"] = final_counts

            poll_dict["userHasVoted"] = user_voted_poll_ids.get(poll.id, None)
            poll_dict["userHasLiked"] = poll.id in user_liked_poll_ids

            poll_dict["email"] = poll.email
            response_list.append(PollResponse(**poll_dict))
            
        return response_list

    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")



# vote on a poll
async def vote_on_poll(poll_id: str, option_id: str, current_user: Dict[str, Any]):
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

        # Redis increment vote count
        redis_key = f"poll:{poll_id}:option:{option_id}"
        new_vote_count = await redis_client.incr(redis_key)
        if new_vote_count is None:
            raise HTTPException(status_code=500, detail="Failed to increment vote count")

        message = {
            "poll_id": poll_id,
            "option_id": option_id,
            "vote_count": new_vote_count,
            "user_id": current_user["id"],
        }

        # sending the message to the message queue
        await redis_client.publish("poll-updates", json.dumps(message))

        return created_vote.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")

# like a poll
async def like_poll(poll_id: str, current_user: Dict[str, Any]):
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

        # Redis increment like count
        redis_key = f"poll:{poll_id}:likes"
        new_like_count = await redis_client.incr(redis_key)
        if new_like_count is None:
            raise HTTPException(status_code=500, detail="Failed to increment like count")

        message = {
            "poll_id": poll_id,
            "type": "like",
            "like_count": new_like_count,
            "user_id": current_user["id"],
        }

        # sending the message to the message queue
        await redis_client.publish("poll-updates", json.dumps(message))

        return created_like.model_dump()
    except Exception as e:
        error_message = str(e)
        print(f"Database error: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {error_message}")