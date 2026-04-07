# server.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.exporter import router as exporter_router
from backend.parser_manager import process_nl_text, process_snl_only

app = FastAPI()

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://www.gidgraph.com",
    "https://api.gidgraph.com",
    "https://gidgraph.com",
]


def get_allowed_origins() -> list[str]:
    """
    Allow local frontend development and deployed frontend usage by default.
    Extra origins can be added with BACKEND_CORS_ORIGINS as a comma-separated list.
    """
    extra_origins = os.getenv("BACKEND_CORS_ORIGINS", "")
    parsed_extra_origins = [
        origin.strip() for origin in extra_origins.split(",") if origin.strip()
    ]

    deduped_origins: list[str] = []
    for origin in [*DEFAULT_CORS_ORIGINS, *parsed_extra_origins]:
        if origin not in deduped_origins:
            deduped_origins.append(origin)

    return deduped_origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextInput(BaseModel):
    text: str


@app.post("/api/parse")
def parse_text(input_data: TextInput):
    """
    Receives a JSON body like: {"text": "some natural-language input"}.
    Calls process_nl_text(...) to do the NLP + parsing,
    and returns the resulting SNL + graph data.
    """
    nlp_output, graph_dict = process_nl_text(input_data.text)

    return {
        # "snl": nlp_output,
        "graph": graph_dict,
    }


@app.post("/api/update_snl")
def update_snl(input_data: TextInput):
    return {"graph": process_snl_only(input_data.text)}


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(exporter_router)
