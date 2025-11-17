"""
Database Schemas for EZBuilds

Each Pydantic model maps to a MongoDB collection using the lowercased
class name as the collection name.

Examples:
- Item -> "item"
- StaffMember -> "staffmember"
- BlogPost -> "blogpost"
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

# Core domain schemas

class Item(BaseModel):
    name: str = Field(..., description="Item name")
    price: float = Field(..., ge=0, description="Price in game currency")
    category: Optional[str] = Field(None, description="Category like blocks, tools, etc.")
    description: Optional[str] = Field(None, description="Optional short description")
    image_url: Optional[HttpUrl] = Field(None, description="Optional image for the item")

class StaffMember(BaseModel):
    username: str = Field(..., description="Minecraft username")
    role: str = Field(..., description="Team role: Content, Mod, Admin, Owner")
    team: str = Field(..., description="Team category e.g. Moderation, Content, Development")
    since: datetime = Field(default_factory=datetime.utcnow, description="Joined date/time")
    avatar_url: Optional[HttpUrl] = Field(None, description="Optional custom skin/face render URL")
    active: bool = Field(True, description="Active staff member")

class VoteLink(BaseModel):
    name: str = Field(..., description="Name of the vote site")
    url: HttpUrl = Field(..., description="Voting URL")
    description: Optional[str] = Field(None, description="Short helper text")

class Event(BaseModel):
    title: str
    description: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    reward: Optional[str] = Field(None, description="Role/Coupon or other reward")
    banner_url: Optional[HttpUrl] = None
    active: bool = True

class BlogPost(BaseModel):
    title: str
    content: str
    author: str
    tags: List[str] = []
    image_url: Optional[HttpUrl] = None
    published: bool = True

class Application(BaseModel):
    applicant_discord_id: str
    applicant_name: str
    role_applied: str
    motivation: str
    status: str = Field("pending", description="pending|accepted|rejected")

class StatSummary(BaseModel):
    online_players: int = 0
    total_players: int = 0
    total_money: float = 0
    tps: float = 20.0
    gamemode: str = "Citybuild"

class PlayerStat(BaseModel):
    username: str
    money: float = 0
    playtime_hours: float = 0
    last_seen: Optional[datetime] = None

class Announcement(BaseModel):
    title: str
    message: str
    visibility: str = Field("public", description="public|staff")

class StaffMeeting(BaseModel):
    title: str
    scheduled_for: datetime
    description: Optional[str] = None
    attendees: List[str] = []

class UserAccount(BaseModel):
    discord_id: str
    username: str
    avatar: Optional[str] = None
    roles: List[str] = Field(default_factory=lambda: ["player"], description="player, staff, mod, admin, owner")
    can_post_blog: bool = False
    can_manage_staff: bool = False
