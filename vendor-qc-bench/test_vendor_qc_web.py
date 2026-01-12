#!/usr/bin/env python3
"""
Simple web server to test vendor_qc Portal/PWA functionality
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
from urllib.parse import urlparse, parse_qs
import threading
import time

class VendorQCHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="apps/vendor_qc/www", **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Handle API endpoints
        if parsed_path.path.startswith('/api/'):
            self.handle_api_request(parsed_path)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/'):
            self.handle_api_post_request(parsed_path)
        else:
            self.send_error(404, "Not Found")
    
    def handle_api_post_request(self, parsed_path):
        """Handle POST API requests for testing"""
        try:
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Mock POST responses
            if 'create_inspection' in parsed_path.path:
                response = {
                    "message": "檢驗創建成功",
                    "data": {
                        "name": f"INSP{int(time.time())}",
                        "status": "Created",
                        "creation": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            elif 'create_ncr' in parsed_path.path:
                response = {
                    "message": "NCR 創建成功", 
                    "data": {
                        "name": f"NCR{int(time.time())}",
                        "status": "Created",
                        "creation": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            else:
                response = {"message": "API endpoint not found"}
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_api_request(self, parsed_path):
        """Handle GET API requests for testing"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Mock API responses
        if 'contractor_sites' in parsed_path.path:
            response = {
                "data": [
                    {
                        "name": "SITE001",
                        "site_name": "測試工地 A",
                        "contractor": "承包商 A",
                        "location": "台北市信義區",
                        "status": "Active"
                    },
                    {
                        "name": "SITE002", 
                        "site_name": "測試工地 B",
                        "contractor": "承包商 B",
                        "location": "新北市板橋區",
                        "status": "Active"
                    }
                ]
            }
        elif 'ncr' in parsed_path.path:
            response = {
                "data": [
                    {
                        "name": "NCR001",
                        "title": "混凝土強度不足",
                        "site": "SITE001",
                        "severity": "High",
                        "status": "Open",
                        "creation": "2024-11-01 10:00:00"
                    },
                    {
                        "name": "NCR002",
                        "title": "鋼筋間距不符規範", 
                        "site": "SITE002",
                        "severity": "Medium",
                        "status": "In Progress",
                        "creation": "2024-11-01 11:00:00"
                    }
                ]
            }
        else:
            response = {"message": "API endpoint not found"}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def start_test_server(port=8090):
    """Start the test web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, VendorQCHandler)
    
    print(f"🌐 Starting vendor_qc test server on http://localhost:{port}")
    print(f"📱 Portal/PWA available at: http://localhost:{port}/app/")
    print("🔗 API endpoints:")
    print(f"   - http://localhost:{port}/api/contractor_sites")
    print(f"   - http://localhost:{port}/api/ncr")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    # Check if vendor_qc www directory exists
    www_dir = "apps/vendor_qc/www"
    if not os.path.exists(www_dir):
        print(f"❌ Directory not found: {www_dir}")
        print("Please make sure you're running this from the bench directory")
        exit(1)
    
    start_test_server()