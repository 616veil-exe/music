import os
from typing import Optional

import yt_dlp
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY", "").strip()  # optional — set in Vercel dashboard to lock this down


def check_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header")


def search_songs(query, limit=12):
    """Fast search using flat extraction (no per-video format resolution)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        entries = (info or {}).get("entries", [])

    results = []
    for e in entries:
        if not e:
            continue
        thumb = e.get("thumbnail")
        if not thumb and e.get("thumbnails"):
            thumb = e["thumbnails"][-1].get("url")
        results.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "duration": e.get("duration"),
            "uploader": e.get("uploader") or e.get("channel"),
            "thumbnail": thumb,
        })
    return results


def resolve_stream(video_id):
    """Resolve a video id to a direct, playable audio stream URL."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "format": "bestaudio/best",
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader") or info.get("channel"),
        "thumbnail": info.get("thumbnail"),
        "stream_url": info.get("url"),
        "ext": info.get("ext"),
        "format_note": info.get("format_note"),
        "expires_note": "stream_url is a signed link that expires after a few hours — resolve again before each play, do not cache long-term",
    }


@app.get("/api/search")
def search(q: str = "", limit: int = 12, x_api_key: Optional[str] = Header(default=None)):
    check_key(x_api_key)
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail='Missing query parameter "q"')
    limit = max(1, min(limit, 25))
    try:
        return search_songs(q, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resolve")
def resolve(id: str = "", x_api_key: Optional[str] = Header(default=None)):
    check_key(x_api_key)
    video_id = id.strip()
    if not video_id:
        raise HTTPException(status_code=400, detail='Missing query parameter "id"')
    try:
        return resolve_stream(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
