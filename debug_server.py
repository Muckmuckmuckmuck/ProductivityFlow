#!/usr/bin/env python3
"""
ProductivityFlow Debug Server
Serves the debug page and handles CORS properly
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import sys
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/'):
            # Proxy API requests to the backend
            self.proxy_api_request()
        else:
            super().do_POST()

    def do_GET(self):
        if self.path.startswith('/api/'):
            # Proxy API requests to the backend
            self.proxy_api_request()
        else:
            super().do_GET()

    def proxy_api_request(self):
        try:
            # Get the full URL path
            backend_url = f"http://localhost:3002{self.path}"
            
            # Get request headers
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'content-length']:
                    headers[key] = value

            # Get request body for POST requests
            content_length = int(self.headers.get('Content-Length', 0))
            body = None
            if content_length > 0:
                body = self.rfile.read(content_length)

            # Create request
            req = urllib.request.Request(backend_url, data=body, headers=headers)
            req.get_method = lambda: self.command

            # Make request to backend
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                response_headers = response.headers

            # Send response back to client
            self.send_response(response.getcode())
            
            # Copy relevant headers
            for key, value in response_headers.items():
                if key.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(key, value)
            
            self.end_headers()
            self.wfile.write(response_data)

        except Exception as e:
            print(f"Error proxying request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                "error": "Proxy error",
                "details": str(e)
            }).encode('utf-8')
            self.wfile.write(error_response)

def main():
    port = 8080
    print(f"🚀 Starting ProductivityFlow Debug Server on port {port}")
    print(f"📱 Open your browser to: http://localhost:{port}/debug_login.html")
    print(f"🌐 Backend URL: http://localhost:3002")
    print(f"🔧 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        server = HTTPServer(('localhost', port), CORSRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Debug server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main() 