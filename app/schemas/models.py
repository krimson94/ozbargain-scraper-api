from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Comment(BaseModel):
    author: str
    comment: str
    date_submitted: datetime
    children: List['Comment'] = Field(default_factory=list)

class DealResponse(BaseModel):
    node_id: int
    url: str
    title: str
    upvotes: int
    downvotes: int
    description: str
    date_submitted: datetime
    comments_count: int
    comments: List[Comment]

class NewDealResponse(BaseModel):
    title: str
    link: str
    description: str
    date_submitted: datetime
    image_url: str
