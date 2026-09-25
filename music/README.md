# ytmusic-api

A tiny, stateless JSON API for searching songs and resolving them to a direct, playable audio
URL — built with **Python + yt-dlp**, deployable to **Vercel** for free.

This is designed to be the "engine" for something bigger later (e.g. a Render-hosted room app) —
it just answers questions with JSON, it doesn't stream audio itself.

---

## Endpoints

### `GET /api/search?q=<query>&limit=<n>`
Searches for songs. `limit` is optional (default 12, max 25).

```
GET /api/search?q=arijit singh tum hi ho
```

```json
[
  {
    "id": "IJq0yyWug1k",
    "title": "Tum Hi Ho",
    "duration": 262,
    "uploader": "T-Series",
    "thumbnail": "https://i.ytimg.com/vi/IJq0yyWug1k/hqdefault.jpg"
  }
]
```

### `GET /api/resolve?id=<video_id>`
Resolves a video id (from a search result) to a direct playable audio URL + metadata.

```
GET /api/resolve?id=IJq0yyWug1k
```

```json
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
```

**Important:** `stream_url` expires after a few hours. Always call `/api/resolve` again right
before you actually need to play/proxy the song — don't store it and reuse it days later.

---

## Deploy to Vercel

1. Push this project to a GitHub repo (root of the repo should contain `api/`, `requirements.txt`,
   `vercel.json`).
2. Go to [vercel.com](https://vercel.com) → **Add New** → **Project** → import the repo.
3. Leave all build settings as default (Framework Preset: **Other**, no build/install command
   overrides). Vercel auto-detects `api/index.py` as the Python entrypoint from `requirements.txt`.
   Click **Deploy**.
4. You'll get a URL like `https://ytmusic-api-yourname.vercel.app`. Test it:
   ```
   https://ytmusic-api-yourname.vercel.app/api/search?q=alan walker faded
   ```

---

## Optional: lock it down with an API key

By default, anyone with your Vercel URL can use this API. If you don't want that (recommended
once it's public), set an environment variable:

1. Vercel dashboard → your project → **Settings → Environment Variables**
2. Add `API_KEY` = any secret string you choose → redeploy.
3. Every request now must include a header: `X-API-Key: <your secret>` — requests without it get
   a `401`.

Leave `API_KEY` unset if you want the API open (fine for early personal testing).

---

## Run it locally (optional, for testing before deploy)

```bash
npm i -g vercel      # Vercel CLI
pip install -r requirements.txt
vercel dev            # starts a local dev server mimicking Vercel's environment
```

---

## Using this later in your Render room app

When you build the room app on Render, instead of running yt-dlp directly on the Render server,
have it call this API:

```js
// inside your Render server.js
const searchRes = await fetch(`https://your-api.vercel.app/api/search?q=${encodeURIComponent(q)}`);
const results = await searchRes.json();

// when a song is about to actually play:
const resolveRes = await fetch(`https://your-api.vercel.app/api/resolve?id=${videoId}`);
const { stream_url } = await resolveRes.json();

// Render then fetches stream_url itself and pipes/proxies it to the connected clients
// (this part stays on Render — Vercel functions can't reliably proxy full audio streams)
```

This keeps the two projects cleanly separated: Vercel does search/resolve, Render does everything
stateful (rooms, sync, chat, voice) and the actual audio proxying.

---

## Limitations

- **Unofficial extraction** — relies on yt-dlp reading YouTube's internal APIs. Can break if
  YouTube changes something; redeploying usually pulls in the latest yt-dlp release automatically
  since `requirements.txt` doesn't pin a version.
- **Cold starts** — first request after inactivity may take a couple of extra seconds.
- **Free-tier execution limit** — 10 seconds per request. Search/resolve normally finish in 1-3s,
  but a slow/unusual query could occasionally hit the ceiling.
- **No audio proxying here by design** — this API only ever returns JSON, never streams bytes
  itself, to stay well within Vercel's response-size and duration limits.
