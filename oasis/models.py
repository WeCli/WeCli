"""
OASIS Forum - Data models
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class DiscussionStatus(str, Enum):
    PENDING = "pending"
    DISCUSSING = "discussing"
    CONCLUDED = "concluded"
    CANCELLED = "cancelled"
    ERROR = "error"


class CreateTopicRequest(BaseModel):
    """Request body for creating a new discussion topic.

    Expert pool is built from schedule_yaml or schedule_file (at least one required).
    schedule_file takes priority if both provided.
      "tag#temp#N" → ExpertAgent; "tag#oasis#id" → SessionExpert (oasis);
      "title#sid" → SessionExpert (regular).  Tag used to lookup name/persona.

    For simple all-parallel scenarios, use:
      version: 1
      repeat: true
      plan:
        - all_experts: true
    """
    question: str
    user_id: str = "anonymous"
    max_rounds: int = Field(default=5, ge=1, le=20)
    schedule_yaml: Optional[str] = None
    schedule_file: Optional[str] = None
    bot_enabled_tools: Optional[list[str]] = None
    bot_timeout: Optional[float] = None
    early_stop: bool = False
    discussion: Optional[bool] = None  # None=use YAML setting; True=forum discussion; False=execute mode
    # Callback: when discussion concludes, POST result to this URL via /system_trigger
    callback_url: Optional[str] = None
    callback_session_id: Optional[str] = None
    team: Optional[str] = None  # Team name for scoped agent storage


class ManualPostRequest(BaseModel):
    """Request body for injecting a live manual post into a running topic."""
    user_id: str = "anonymous"
    author: Optional[str] = None
    content: str = Field(min_length=1, max_length=8000)
    reply_to: Optional[int] = None


class AgentCallbackRequest(BaseModel):
    """Structured callback posted by an external agent during a running topic."""
    user_id: str = "anonymous"
    author: str = Field(min_length=1, max_length=200)
    round_num: int = Field(ge=0)
    result: dict[str, Any]


class HumanReplyRequest(BaseModel):
    """Plain-text reply that satisfies a waiting human workflow node."""
    user_id: str = "anonymous"
    node_id: str = Field(min_length=1)
    round_num: int = Field(ge=0)
    content: str = Field(min_length=1, max_length=8000)
    author: Optional[str] = None


class HumanWaitInfo(BaseModel):
    """Current waiting human node state, if any."""
    node_id: str
    prompt: str
    author: str
    round_num: int
    reply_to: Optional[int] = None


class PostInfo(BaseModel):
    """Single post in a discussion thread."""
    id: int
    author: str
    content: str
    reply_to: Optional[int] = None
    upvotes: int = 0
    downvotes: int = 0
    timestamp: float
    elapsed: float = 0.0


class TimelineEventInfo(BaseModel):
    """A single timeline event."""
    elapsed: float
    event: str
    agent: str = ""
    detail: str = ""


class TopicDetail(BaseModel):
    """Full detail of a discussion topic."""
    topic_id: str
    question: str
    user_id: str = "anonymous"
    status: DiscussionStatus
    current_round: int
    max_rounds: int
    posts: list[PostInfo]
    timeline: list[TimelineEventInfo] = []
    discussion: bool = True
    conclusion: Optional[str] = None
    pending_human: Optional[HumanWaitInfo] = None


class TopicSummary(BaseModel):
    """Brief summary of a discussion topic (for listing)."""
    topic_id: str
    question: str
    user_id: str = "anonymous"
    status: DiscussionStatus
    post_count: int
    current_round: int
    max_rounds: int
    created_at: float
