from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class Option(BaseModel):
    id: str
    text: str
    pollId: str

    class Config:
        from_attributes = True

class Vote(BaseModel):
    id: Optional[str] = None
    userId: str
    optionId: str
    pollId: str
    
    class Config:
        from_attributes = True

class Like(BaseModel):
    id: Optional[str] = None
    userId: str
    pollId: str
    
    class Config:
        from_attributes = True


class OptionCreate(BaseModel):
    text: str

class PollCreate(BaseModel):
    question: str
    options: List[OptionCreate]
    email: str


class PollResponse(BaseModel):
    id: str
    question: str
    userId: str
    email: Optional[str] = None
    createdAt: datetime
    options: List[Option]

    counts: Dict[str, int]
    userHasVoted: Optional[str]
    userHasLiked: bool

    class Config:
        from_attributes = True