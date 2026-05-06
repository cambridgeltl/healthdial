"""Socket.IO dummy dialogue service for reproducing the evaluation workflow.

The original study connected the evaluation UI to a separate dialogue system.
This lightweight server implements the same frontend-facing Socket.IO contract
so readers can run the full UI flow without access to the original service.
"""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit


DEFAULT_RESPONSE = (
    "This dummy health-information assistant is running in reproducibility "
    "mode. For the study task, compare the information you find on the WHO "
    "website with this dialogue experience. This response is deterministic "
    "and is not medical advice."
)


def _evidence_snippets() -> list[dict[str, Any]]:
    """Return evidence objects in the exact shape consumed by the React UI."""
    return [
        {
            "url": "https://www.who.int/health-topics",
            "data": {
                "title": "WHO health topics",
                "content": (
                    "The dummy server returns this evidence block to exercise "
                    "the frontend evidence-display path used in the evaluation."
                ),
            },
        },
        {
            "url": "https://www.who.int/news-room/questions-and-answers",
            "data": {
                "title": "WHO questions and answers",
                "content": (
                    "Use the production dialogue server URL in "
                    "REACT_APP_DIALOGUE_SERVER_URL to connect a real system."
                ),
            },
        },
    ]


def _build_text_response(user_text: str) -> dict[str, Any]:
    """Build a deterministic text response for reproducibility smoke tests."""
    cleaned_text = user_text.strip()
    if cleaned_text:
        response_text = (
            f"You asked about: \"{cleaned_text}\". {DEFAULT_RESPONSE} "
            "For urgent or severe symptoms, seek professional medical care."
        )
    else:
        response_text = (
            "I received an empty message. Please ask a health-information "
            f"question. {DEFAULT_RESPONSE}"
        )

    return {
        "type": "text",
        "system_text": response_text,
        "snippet": _evidence_snippets(),
    }


def _build_voice_response(payload: Any) -> dict[str, Any]:
    """Acknowledge voice payloads without doing speech recognition."""
    has_audio = isinstance(payload, dict) and bool(payload.get("audio"))
    received_state = "received" if has_audio else "did not receive"
    return {
        "type": "text",
        "system_text": (
            f"I {received_state} a voice input. The dummy server does not run "
            "speech recognition, but it returns a compatible text response so "
            "the evaluation workflow can be reproduced end to end."
        ),
        "snippet": _evidence_snippets(),
    }


def create_app() -> tuple[Flask, SocketIO]:
    """Create the Flask/Socket.IO app used by both tests and local runs."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("DUMMY_DIALOGUE_SECRET_KEY", "dummy-dialogue-secret")
    CORS(app, resources={r"/*": {"origins": "*"}})

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    @app.get("/healthz")
    def health_check():
        return jsonify({"status": "ok", "service": "dummy-dialogue-server"})

    @socketio.on("connect")
    def handle_connect():
        app.logger.info("Client connected to dummy dialogue server: %s", request.sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        app.logger.info("Client disconnected from dummy dialogue server: %s", request.sid)

    @socketio.on("user_message")
    def handle_user_message(message: Any):
        # Frontend contract: the browser emits raw text on user_message.
        user_text = message if isinstance(message, str) else ""
        emit("system_message", _build_text_response(user_text))

    @socketio.on("user_voice")
    def handle_user_voice(payload: Any):
        # Frontend contract: the browser emits {"audio": data_url} on user_voice.
        emit("system_message", _build_voice_response(payload))

    return app, socketio


app, socketio = create_app()


if __name__ == "__main__":
    port = int(os.getenv("DUMMY_DIALOGUE_PORT", "5050"))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
