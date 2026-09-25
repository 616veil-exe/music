🎵 ytmusic-api

«A tiny, stateless JSON API for searching songs and resolving them to direct, playable audio URLs.

Built with Python + yt-dlp and deployable to Vercel for free.»

Designed to act as the engine behind something bigger later — for example, a Render-hosted room app.

It answers questions with JSON.
It does not stream audio itself.

---

✦ Endpoints

"GET /api/search"

Search for songs.

Parameter| Required| Default| Maximum
"q"| ✓| —| —
"limit"| —| "12"| "25"

Example

GET /api/search?q=arijit%20singh%20tum%20hi%20ho

Response

[
  {
    "id": "IJq0yyWug1k",
    "title": "Tum Hi Ho",
    "duration": 262,
    "uploader": "T-Series",
    "thumbnail": "https://i.ytimg.com/vi/IJq0yyWug1k/hqdefault.jpg"
  }
]

---

"GET /api/resolve"

Resolve a video ID from a search result into a direct playable audio URL + metadata.

GET /api/resolve?id=IJq0yyWug1k

Response

{
  "id": "IJq0yyWug1k",
  "title": "Tum Hi Ho",
  "duration": 262,
  "uploader": "T-Series",
  "thumbnail": "https://i.ytimg.com/vi/IJq0yyWug1k/hqdefault.jpg",
  "stream_url": "https://rr---sn-xxxx.googlevideo.com/videoplayback?...",
  "ext": "webm",
  "format_note": "medium",
  "expires_note": "stream_url is a signed link that expires after a few hours — resolve again before each play, do not cache long-term"
}

«[!IMPORTANT]

"stream_url" is temporary

The returned "stream_url" expires after a few hours.

Always call "/api/resolve" right before you actually need to play or proxy the song.

Do not store the URL and reuse it days later.»

---

🚀 Deploy to Vercel

Deploying is intentionally simple.

01 — Push the project

Push the project to a GitHub repository.

The repository root should contain:

api/
requirements.txt
vercel.json

02 — Import into Vercel

Go to "vercel.com" (https://vercel.com) →

Add New → Project → Import the repository.

03 — Deploy

Vercel automatically detects the Python functions in "api/" from "requirements.txt".

No other configuration is needed.

Click Deploy.

04 — Test the API

You'll receive a URL similar to:

https://ytmusic-api-yourname.vercel.app

Then test:

https://ytmusic-api-yourname.vercel.app/api/search?q=alan%20walker%20faded

---

🔐 Optional API Key

By default, anyone who knows your Vercel URL can use the API.

If you don't want that, you can lock it down with an API key.

«Recommended once the API becomes public.»

Setup

1. Open your Vercel project.

Settings
   └── Environment Variables

2. Add:

API_KEY = your-secret-string

3. Redeploy.

After that, every request must include:

X-API-Key: <your secret>

Requests without the correct key receive:

401

Open API mode

Leave "API_KEY" unset if you want the API to remain open.

This is fine for early personal testing.

---

🧪 Run Locally

Optional — useful for testing before deployment.

Install Vercel CLI

npm i -g vercel

Install Python dependencies

pip install -r requirements.txt

Start local development

vercel dev

This starts a local development server that mimics the Vercel environment.

---

🏗️ Using This With a Render Room App

When you build the room app on Render, instead of running "yt-dlp" directly on the Render server, have it call this API.

Search

// inside your Render server.js
const searchRes = await fetch(
  `https://your-api.vercel.app/api/search?q=${encodeURIComponent(q)}`
);

const results = await searchRes.json();

Resolve when playback begins

// when a song is about to actually play:
const resolveRes = await fetch(
  `https://your-api.vercel.app/api/resolve?id=${videoId}`
);

const { stream_url } = await resolveRes.json();

Audio proxy

// Render then fetches stream_url itself and pipes/proxies it
// to the connected clients.
//
// This part stays on Render — Vercel functions can't reliably
// proxy full audio streams.

Architecture

                         ┌─────────────────────┐
                         │     Client / UI     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Render Room App  │
                         │                     │
                         │  rooms              │
                         │  sync               │
                         │  chat               │
                         │  voice              │
                         │  audio proxy        │
                         └──────────┬──────────┘
                                    │
                          search / resolve
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Vercel API      │
                         │                     │
                         │      yt-dlp         │
                         │                     │
                         │  /api/search        │
                         │  /api/resolve       │
                         └─────────────────────┘
                                    │
                                    ▼
                              YouTube data

This keeps the two projects cleanly separated:

Vercel API| Render Room App
Song search| Rooms
Video resolution| Synchronization
Metadata| Chat
Direct audio URLs| Voice
Stateless| Stateful
JSON responses| Audio proxying

Vercel does search/resolve.
Render handles everything stateful and proxies the actual audio.

---

⚠️ Limitations

01 · Unofficial extraction

This relies on "yt-dlp" reading YouTube's internal APIs.

YouTube can change those APIs, which may break extraction.

Redeploying usually pulls in the latest "yt-dlp" release automatically since "requirements.txt" doesn't pin a version.

---

02 · Cold starts

The first request after inactivity may take a couple of extra seconds.

---

03 · Free-tier execution limit

Vercel's free-tier execution limit is 10 seconds per request.

Search/resolve normally finish in 1–3 seconds, but a slow or unusual query could occasionally hit the ceiling.

---

04 · No audio proxying

This API intentionally never streams audio bytes itself.

It only returns JSON.

That keeps it well within Vercel's response-size and duration limits.

---

📌 Project Philosophy

                 ┌─────────────────────┐
                 │      ytmusic-api    │
                 └──────────┬──────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
            SEARCH                    RESOLVE
               │                         │
               ▼                         ▼
          Song metadata          Direct audio URL
               │                         │
               └────────────┬────────────┘
                            │
                            ▼
                     JSON → Client

Small. Stateless. Focused.

The API handles discovery and resolution so the application built around it doesn't have to.

---

<div align="center">Built with

Python · yt-dlp · Vercel

</div>