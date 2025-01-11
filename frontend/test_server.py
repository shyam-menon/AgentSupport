from http.server import HTTPServer, SimpleHTTPRequestHandler

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8501)
    httpd = server_class(server_address, handler_class)
    print("Server starting on port 8501...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
