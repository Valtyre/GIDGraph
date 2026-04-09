# server.py
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.exporter import router as exporter_router
from backend.nlp.local_text_optimizer import optimize_text
from backend.parser_manager import process_nl_text, process_snl_only
from backend.parser.visParser import ParserError

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


def _raise_http_parse_error(exc: ParserError) -> None:
    raise HTTPException(
        status_code=422,
        detail={
            "error": exc.error,
            "message": exc.message,
            "details": {
                "original_input": exc.original_input,
                "parser_input": exc.parser_input,
                "position": exc.position,
                "context": exc.context,
            },
        },
    )


@app.post("/api/parse")
def parse_text(input_data: TextInput):
    """
    Receives a JSON body like: {"text": "some natural-language input"}.
    Calls process_nl_text(...) to do the NLP + parsing,
    and returns the resulting SNL + graph data.
    """
    try:
        _, graph_dict = process_nl_text(input_data.text)
    except ParserError as exc:
        _raise_http_parse_error(exc)

    return {
        "graph": graph_dict,
    }


@app.post("/api/update_snl")
def update_snl(input_data: TextInput):
    try:
        return {"graph": process_snl_only(input_data.text)}
    except ParserError as exc:
        _raise_http_parse_error(exc)


@app.post("/api/optimize_nl")
def optimize_nl(input_data: TextInput):
    result = optimize_text(input_data.text)
    return {
        "text": result.text,
        "optimized": result.optimized,
        "fallback": result.fallback,
    }


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(exporter_router)
