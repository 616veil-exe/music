import yt_dlp


def search_songs(query, limit=12):
    """Fast search using flat extraction (no per-video format resolution)."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        entries = (info or {}).get('entries', [])

    results = []
    for e in entries:
        if not e:
            continue
        thumb = e.get('thumbnail')
        if not thumb and e.get('thumbnails'):
            thumb = e['thumbnails'][-1].get('url')
        results.append({
            'id': e.get('id'),
            'title': e.get('title'),
            'duration': e.get('duration'),
            'uploader': e.get('uploader') or e.get('channel'),
            'thumbnail': thumb,
        })
    return results


def resolve_stream(video_id):
    """Resolve a video id to a direct, playable audio stream URL."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'bestaudio/best',
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        'id': info.get('id'),
        'title': info.get('title'),
        'duration': info.get('duration'),
        'uploader': info.get('uploader') or info.get('channel'),
        'thumbnail': info.get('thumbnail'),
        'stream_url': info.get('url'),
        'ext': info.get('ext'),
        'format_note': info.get('format_note'),
        'expires_note': 'stream_url is a signed link that expires after a few hours — resolve again before each play, do not cache long-term'
    }
