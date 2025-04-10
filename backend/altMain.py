# file: backend/main.py

import json
import sys
import time
import threading
import webbrowser
import http.server
import socketserver
import os

### CHANGED ###
# Instead of importing from parser directly, import process_nl_text
# from parser_manager (the new file).
from .parser_manager import process_nl_text

PORT = 8000
URL = f"http://localhost:{PORT}/betterGraphTester.html"

def run_http_server():
    """Starts a simple HTTP server serving files from the current directory."""
    os.chdir('backend')
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def open_browser(url):
    """Opens the default web browser to the specified URL."""
    webbrowser.open(url)

def main():
    # -------------------------
    # Step 1: Read Input from nl_texts.json
    # -------------------------
    try:
        with open("backend/nlp/nl_texts.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'nl_texts.json' was not found.")
        sys.exit(1)

    # We'll parse data["text3"] as before, but use our new function.
    natural_language = data["text3"]

    ### CHANGED ###
    # Step 2: Use process_nl_text instead of manual calls to nlp_runner + vis_parse_text
    nlp_output, graph_dict = process_nl_text(natural_language)
    print("🔹 NLP Output:\n", nlp_output)

    # If you still want a JSON file on disk, write it here:
    with open("backend/graphOutputs/gene_network.json", "w") as f:
        json.dump(graph_dict, f, indent=4)
    print("\n✅ Parsing complete! JSON file generated in 'backend/graphOutputs/gene_network.json'.")

    # -------------------------
    # Step 3: Start HTTP Server and Open Browser
    # -------------------------
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()

    # Wait briefly to ensure the server starts
    time.sleep(1)

    # Open the default browser to the specified URL.
    open_browser(URL)

    # Keep the script running so the server remains active.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
