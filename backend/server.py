# server.py (inside backend/ folder)
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import the function in parser_manager.py
from backend.parser_manager import process_nl_text, process_snl_only
from backend.exporter import router as exporter_router

app = FastAPI()

# List the domains (origins) that are allowed to talk to this API.
# For local development with React/Next on port 3000, add that:
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],             # e.g. ["GET", "POST"] if you want to restrict
    allow_headers=["*"],
)

# Define a Pydantic model for the incoming JSON body
class TextInput(BaseModel):
    text: str

@app.post("/api/parse")
def parse_text(input_data: TextInput):
    """
    Receives a JSON body like: {"text": "some natural-language input"}.
    Calls process_nl_text(...) to do the NLP + parsing, 
    and returns the resulting SNL + graph data.
    """
    # 1) Call parser function
    nlp_output, graph_dict = process_nl_text(input_data.text)

    # 2) Return JSON to the client
    return {
        # "snl": nlp_output,
        "graph": graph_dict
    }

@app.post("/api/update_snl")
def update_snl(input_data: TextInput):
    return {"graph": process_snl_only(input_data.text)}

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Include the exporter router to handle the export_ginml endpoint
app.include_router(exporter_router)
