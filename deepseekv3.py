import logging
import os
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from waitress import serve

from src.stream import sync_stream

app = Flask(__name__)
CORS(app)

HOST: str = os.getenv("DEEPSEEKV3_HOST", "127.0.0.1")
PORT: int = os.getenv("DEEPSEEKV3_PORT", 5000)
DEBUG: bool = os.getenv("DEEPSEEKV3_DEBUG", False)

MODELS: List[Dict[str, Any]] = [
    {
        "id": "deepseek-chat",
        "object": "model",
        "created": 1735693261,
        "owned_by": "deepseek",
    },
    {
        "id": "deepseek-coder",
        "object": "model",
        "created": 1735693262,
        "owned_by": "deepseek",
    },
]

logging.basicConfig(filename="deepseekv3.log", encoding="utf-8", level=logging.INFO)


def models():
    return jsonify({"object": "list", "data": MODELS})


def chat_completions():
    request_data = request.get_json()
    request_data = {"messages": request_data["messages"], "turnstileToken": ""}

    stream = stream_with_context(sync_stream(request_data))
    return Response(stream, status=200, content_type="text/event-stream")


if __name__ == "__main__":
    app.add_url_rule("/v1/models", None, models, methods=["GET"])
    app.add_url_rule("/v1/chat/completions", None, chat_completions, methods=["POST"])

    if DEBUG:
        app.run(HOST, PORT, DEBUG)
    else:
        logging.info(f"[SERVE] Server running at http://{HOST}:{PORT}/")
        serve(app, host=HOST, port=PORT)
