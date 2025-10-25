from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class Option(BaseModel):
    id: Optional[str] = None
    text: str
    pollId: Optional[str] = None

class Vote(BaseModel):
    id: Optional[str] = None
    userId: str
    optionId: str
    pollId: str

class Like(BaseModel):
    id: Optional[str] = None
    userId: str
    pollId: str


class PollCreate(BaseModel):
    question: str
    userId: str
    options: Optional[List[Option]] = None
    votes: Optional[List[Vote]] = None
    likes: Optional[List[Like]] = None


class Poll(BaseModel):
    id: Optional[str] = None
    question: str
    userId: str
    options: Optional[List[Option]] = None
    votes: Optional[List[Vote]] = None
    likes: Optional[List[Like]] = None
    createdAt: Optional[datetime] = None