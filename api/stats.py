from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# הוספת הנתיב לשימוש ב-utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import CONFIG

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            stats = {
                "chunk_size": CONFIG["chunk_size"],
                "overlap_ratio": CONFIG["overlap_ratio"],
                "top_k": CONFIG["top_k"]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

