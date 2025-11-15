import os
from typing import List, Literal, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Love Animations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnimationFrame(BaseModel):
    emoji: str
    color: str
    motion: Literal["float", "bounce", "pulse", "spin", "slide"]
    duration: float
    text: Optional[str] = None


class AnimateRequest(BaseModel):
    message: str


class AnimateResponse(BaseModel):
    theme: Literal["romance", "gratitude", "missyou", "apology", "celebration", "default"]
    frames: List[AnimationFrame]
    tags: List[str]
    caption: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/animate", response_model=AnimateResponse)
def animate_text(req: AnimateRequest):
    text = req.message.strip()
    lower = text.lower()

    romance_words = ["love", "heart", "babe", "baby", "sweet", "kiss", "romance", "romantic", "dear", "darling"]
    gratitude_words = ["thank", "grateful", "appreciate", "gratitude", "thanks"]
    missyou_words = ["miss you", "miss u", "missing", "apart", "distance"]
    apology_words = ["sorry", "apolog", "forgive", "regret"]
    celebration_words = ["congrats", "congratulations", "celebrate", "birthday", "anniversary", "party", "yay", "proud"]

    def contains_any(words):
        return any(w in lower for w in words)

    if contains_any(romance_words):
        theme = "romance"
        palette = ["#FF6B6B", "#FF8FAB", "#FFC6FF", "#BDB2FF"]
        emojis = ["💖", "💞", "😘", "💐", "✨"]
        motions = ["float", "pulse", "bounce"]
        caption = "A love note, animated with hearts"
    elif contains_any(gratitude_words):
        theme = "gratitude"
        palette = ["#FFD166", "#F4978E", "#C6F7E2", "#BEE3F8"]
        emojis = ["🙏", "🌟", "😊", "💛", "✨"]
        motions = ["pulse", "float", "slide"]
        caption = "A warm thank-you, wrapped in sparkles"
    elif contains_any(missyou_words):
        theme = "missyou"
        palette = ["#A0AEC0", "#90CDF4", "#B794F4", "#81E6D9"]
        emojis = ["🌙", "💫", "💌", "🕊️", "✨"]
        motions = ["float", "slide", "pulse"]
        caption = "Across the distance, a little animated hug"
    elif contains_any(apology_words):
        theme = "apology"
        palette = ["#FBD38D", "#F6AD55", "#FEEBC8", "#CBD5E0"]
        emojis = ["🥺", "💛", "🌧️", "🤍", "✨"]
        motions = ["pulse", "slide", "float"]
        caption = "Soft apologies, hoping for a smile"
    elif contains_any(celebration_words):
        theme = "celebration"
        palette = ["#FDE68A", "#FCA5A5", "#93C5FD", "#6EE7B7"]
        emojis = ["🎉", "🎊", "🌈", "🌟", "💃"]
        motions = ["bounce", "spin", "pulse"]
        caption = "Good news deserves confetti"
    else:
        theme = "default"
        palette = ["#FBB6CE", "#BEE3F8", "#C6F6D5", "#FAF089"]
        emojis = ["✨", "⭐", "💌", "🌸", "🌙"]
        motions = ["float", "pulse", "slide"]
        caption = "Feelings, made a little magical"

    # Split text into gentle chunks
    import re
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    if not sentences:
        sentences = [text] if text else ["(empty message)"]

    # Build frames by pairing sentences with cute emoji/motions/colors
    frames: List[AnimationFrame] = []
    for i, s in enumerate(sentences):
        frames.append(
            AnimationFrame(
                emoji=emojis[i % len(emojis)],
                color=palette[i % len(palette)],
                motion=motions[i % len(motions)],
                duration=max(2.0, min(5.0, 2.5 + (len(s) / 80.0))),
                text=s,
            )
        )

    # Add a closing sparkle frame
    frames.append(
        AnimationFrame(
            emoji="✨",
            color=palette[len(frames) % len(palette)],
            motion="float",
            duration=2.5,
            text="",
        )
    )

    # Lightweight "love language" style tags
    tags = []
    if contains_any(["proud", "amazing", "best", "incredible", "beautiful", "handsome"]):
        tags.append("words-of-affirmation")
    if contains_any(["hug", "hold", "touch", "cuddle", "kiss"]):
        tags.append("physical-touch")
    if contains_any(["gift", "present", "surprise", "treat"]):
        tags.append("gift-giving")
    if contains_any(["time", "together", "walk", "date", "movie"]):
        tags.append("quality-time")
    if contains_any(["help", "support", "do", "bring", "cook", "clean"]):
        tags.append("acts-of-service")

    return AnimateResponse(theme=theme, frames=frames, tags=tags, caption=caption)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
