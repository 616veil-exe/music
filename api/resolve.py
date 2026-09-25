from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import sys

sys.path.append(os.path.dirname(__file__))
from _utils import resolve_stream

API_KEY = os.environ.get('API_KEY', '').strip()  # optional — set in Vercel dashboard to lock this down


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if API_KEY and self.headers.get('X-API-Key', '') != API_KEY:
            self._json(401, {'error': 'Invalid or missing X-API-Key header'})
            return

        query = parse_qs(urlparse(self.path).query)
        video_id = (query.get('id', [''])[0] or '').strip()

        if not video_id:
            self._json(400, {'error': 'Missing query parameter "id"'})
            return

        try:
            data = resolve_stream(video_id)
            self._json(200, data)
        except Exception as e:
            self._json(500, {'error': str(e)})

    def _json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
