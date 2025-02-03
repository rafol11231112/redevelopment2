from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import base64
import sys
from urllib.parse import urlparse
from datetime import datetime
import mimetypes

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Cache common file types
        self.cache = {}
        super().__init__(*args, **kwargs)

    def log_ip(self):
        # Only log essential information
        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {client_ip} - {self.path}\n"
        
        with open("ips.log", "a") as log_file:
            log_file.write(log_entry)

    def do_GET(self):
        # Log IP for every request
        self.log_ip()
        
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        
        # Try to serve from cache first
        if self.path in self.cache:
            content, content_type = self.cache[self.path]
            self.send_response(200)
            if content_type:
                self.send_header('Content-type', content_type)
            self.send_header('Cache-Control', 'max-age=3600')  # Cache for 1 hour
            self.end_headers()
            self.wfile.write(content)
            return

        # Get file extension and set correct content type
        _, ext = os.path.splitext(self.path)
        content_type = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif'
        }.get(ext, 'text/plain')

        # Handle API requests
        if self.path.startswith('/api/'):
            if self.path == '/api/projects':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                projects = self.get_projects()
                self.wfile.write(json.dumps(projects).encode())
                return

        # Serve static files
        try:
            with open(self.path[1:], 'rb') as f:
                content = f.read()
                
            # Cache the file if it's a common type
            if ext in ['.css', '.js', '.html']:
                self.cache[self.path] = (content, content_type)
                
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Cache-Control', 'max-age=3600')
            self.end_headers()
            self.wfile.write(content)
            return
        except Exception as e:
            print(f"Error serving file {self.path}: {e}")
            self.send_error(404, f"File not found: {self.path}")

    def do_POST(self):
        # Send response before headers
        self.send_response(200)
        
        # Add CORS and ngrok-specific headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.send_header('ngrok-skip-browser-warning', 'true')
        
        # Log IP after sending headers
        self.log_ip()
        
        content_length = int(self.headers.get('Content-Length', 0))
        
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            print(f"Received POST request to {self.path} with data: {data}")
            
            if self.path == '/api/projects':
                self.save_project(data)
                self.send_json_response({'success': True, 'message': 'Project saved successfully'})
            elif self.path == '/api/projects/delete':
                self.delete_project(data['id'])
                self.send_json_response({'success': True, 'message': 'Project deleted successfully'})
            else:
                self.send_error(404, "API endpoint not found")

        except Exception as e:
            print(f"Error processing request: {str(e)}", file=sys.stderr)
            self.send_error(500, str(e))

    def send_json_response(self, data):
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps(data).encode()
        self.wfile.write(response)

    def get_projects(self):
        try:
            os.makedirs('data', exist_ok=True)
            projects_file = Path('data/projects.json')
            
            if not projects_file.exists():
                with open(projects_file, 'w') as f:
                    json.dump([], f)
                return []
                
            with open(projects_file, 'r') as f:
                projects = json.load(f)
                return projects
        except Exception as e:
            print(f"Error loading projects: {str(e)}", file=sys.stderr)
            return []

    def save_project(self, project_data):
        try:
            os.makedirs('data', exist_ok=True)
            projects = self.get_projects()
            existing_idx = next((i for i, p in enumerate(projects) if str(p['id']) == str(project_data['id'])), None)
            
            if existing_idx is not None:
                projects[existing_idx] = project_data
            else:
                projects.append(project_data)
            
            with open('data/projects.json', 'w') as f:
                json.dump(projects, f, indent=2)
        except Exception as e:
            print(f"Error saving project: {str(e)}", file=sys.stderr)
            raise

    def delete_project(self, project_id):
        try:
            projects = self.get_projects()
            projects = [p for p in projects if str(p['id']) != str(project_id)]
            
            with open('data/projects.json', 'w') as f:
                json.dump(projects, f)
        except Exception as e:
            print(f"Error deleting project: {str(e)}", file=sys.stderr)
            raise

# Server setup

def run(server_class=HTTPServer, handler_class=CORSRequestHandler, port=8000):
    server_address = ('', port)
    
    while True:
        try:
            httpd = server_class(server_address, handler_class)
            break
        except OSError:
            print(f"Port {port} is in use, trying port {port + 1}")
            port += 1
            server_address = ('', port)

    print(f"Server running on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run()
