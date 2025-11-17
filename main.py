import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import (
    Item,
    StaffMember,
    VoteLink,
    Event,
    BlogPost,
    Application,
    StatSummary,
    PlayerStat,
    Announcement,
    StaffMeeting,
    UserAccount,
)

app = FastAPI(title="EZBuilds API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers

def _collection_name(model_cls: Any) -> str:
    return model_cls.__name__.lower()


def _serialize(doc: Dict[str, Any]):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


@app.get("/")
def root():
    return {"name": "EZBuilds API", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:15]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Schema discovery for admin tools
class SchemaInfo(BaseModel):
    name: str
    fields: Dict[str, str]


@app.get("/schema", response_model=List[SchemaInfo])
def get_schema():
    models = [
        Item,
        StaffMember,
        VoteLink,
        Event,
        BlogPost,
        Application,
        StatSummary,
        PlayerStat,
        Announcement,
        StaffMeeting,
        UserAccount,
    ]
    out: List[SchemaInfo] = []
    for m in models:
        annotations = getattr(m, "model_fields", {})
        fields: Dict[str, str] = {}
        for name, field in annotations.items():
            fields[name] = str(field.annotation)
        out.append(SchemaInfo(name=m.__name__.lower(), fields=fields))
    return out


# Items
@app.get("/items")
def list_items(q: Optional[str] = Query(None), limit: int = 100):
    filt: Dict[str, Any] = {}
    if q:
        filt = {"name": {"$regex": q, "$options": "i"}}
    docs = get_documents(_collection_name(Item), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/items")
def create_item(item: Item):
    _id = create_document(_collection_name(Item), item)
    return {"id": _id}


# Staff
@app.get("/staff")
def list_staff(role: Optional[str] = None, team: Optional[str] = None, active: Optional[bool] = None, limit: int = 200):
    filt: Dict[str, Any] = {}
    if role:
        filt["role"] = role
    if team:
        filt["team"] = team
    if active is not None:
        filt["active"] = active
    docs = get_documents(_collection_name(StaffMember), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/staff")
def create_staff(member: StaffMember):
    _id = create_document(_collection_name(StaffMember), member)
    return {"id": _id}


# Vote links
@app.get("/votes")
def list_votes(limit: int = 20):
    docs = get_documents(_collection_name(VoteLink), {}, limit)
    return [_serialize(d) for d in docs]


@app.post("/votes")
def create_vote(v: VoteLink):
    _id = create_document(_collection_name(VoteLink), v)
    return {"id": _id}


# Events
@app.get("/events")
def list_events(active: Optional[bool] = None, limit: int = 50):
    filt: Dict[str, Any] = {}
    if active is not None:
        filt["active"] = active
    docs = get_documents(_collection_name(Event), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/events")
def create_event(e: Event):
    _id = create_document(_collection_name(Event), e)
    return {"id": _id}


# Blog
@app.get("/blogs")
def list_blogs(tag: Optional[str] = None, published: Optional[bool] = True, limit: int = 50):
    filt: Dict[str, Any] = {}
    if tag:
        filt["tags"] = {"$in": [tag]}
    if published is not None:
        filt["published"] = published
    docs = get_documents(_collection_name(BlogPost), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/blogs")
def create_blog(post: BlogPost):
    _id = create_document(_collection_name(BlogPost), post)
    return {"id": _id}


# Applications
@app.get("/applications")
def list_applications(status: Optional[str] = None, limit: int = 100):
    filt: Dict[str, Any] = {}
    if status:
        filt["status"] = status
    docs = get_documents(_collection_name(Application), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/applications")
def create_application(apply: Application):
    _id = create_document(_collection_name(Application), apply)
    return {"id": _id}


# Stats
@app.get("/stats/summary")
def get_stats_summary():
    docs = get_documents(_collection_name(StatSummary), {}, 1)
    if docs:
        return _serialize(docs[0])
    # default summary
    return StatSummary().model_dump()


@app.get("/stats/players")
def get_player_stats(username: Optional[str] = None, limit: int = 100):
    filt: Dict[str, Any] = {}
    if username:
        filt["username"] = {"$regex": f"^{username}$", "$options": "i"}
    docs = get_documents(_collection_name(PlayerStat), filt, limit)
    return [_serialize(d) for d in docs]


# Announcements
@app.get("/announcements")
def list_announcements(visibility: Optional[str] = "public", limit: int = 50):
    filt: Dict[str, Any] = {}
    if visibility:
        filt["visibility"] = visibility
    docs = get_documents(_collection_name(Announcement), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/announcements")
def create_announcement(a: Announcement):
    _id = create_document(_collection_name(Announcement), a)
    return {"id": _id}


# Staff meetings
@app.get("/meetings")
def list_meetings(limit: int = 50):
    docs = get_documents(_collection_name(StaffMeeting), {}, limit)
    return [_serialize(d) for d in docs]


@app.post("/meetings")
def create_meeting(m: StaffMeeting):
    _id = create_document(_collection_name(StaffMeeting), m)
    return {"id": _id}


# Users
@app.get("/users")
def list_users(role: Optional[str] = None, limit: int = 100):
    filt: Dict[str, Any] = {}
    if role:
        filt["roles"] = {"$in": [role]}
    docs = get_documents(_collection_name(UserAccount), filt, limit)
    return [_serialize(d) for d in docs]


@app.post("/users")
def create_user(u: UserAccount):
    _id = create_document(_collection_name(UserAccount), u)
    return {"id": _id}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
