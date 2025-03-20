import json
import sys
import time
import threading
import webbrowser
import http.server
import socketserver
import os

from parser.visParser import vis_parse_text  # Import the parsing function from the visual parser
from nlp.spacy_test import nlp_runner      # Import the NLP pipeline

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
    # Step 1: Run the parser
    # -------------------------
    try:
        with open("backend/nlp/nl_texts.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'nl_texts.json' was not found.")
        sys.exit(1)

    # Run NLP pipeline and get structured text
    nlp_output = nlp_runner(data["text3"])
    print("🔹 NLP Output:\n", nlp_output)

    # Run the parser (vis parser) and generate the JSON graph
    transformer = vis_parse_text(nlp_output)
    transformer.to_json("backend/graphOutputs/gene_network.json")
    print("\n✅ Parsing complete! JSON file generated.")

    # -------------------------
    # Step 2: Start HTTP Server and Open Browser
    # -------------------------
    # Start the HTTP server in a separate thread.
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
