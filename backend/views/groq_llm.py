from flask import Blueprint
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from llm.Groq import Groq_API

from flask import (
    request,
    jsonify,
    abort,
    redirect,
)

Groq = Groq_API()
groq = Blueprint('groq', __name__)


@groq.route("/message", methods=["GET"], strict_slashes=False)
def message() -> str:
    """Start the auth"""
    return jsonify({"message": "Bienvenue"})

@groq.route("/get-songs", methods=["POST"], strict_slashes=False)
def index() -> str:
    """Fetch the songs from the groq api"""
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Invalid format'}), 400
    system_content = 'You are a playlist generator. You are to receive a prompt containing mood of the user.You are suppose to generate a playlist matching the user mode and return the songs in json.Return an json response with error message if the prompt is other than songs genaration'
    response = Groq.get_response(message, system_content, 1, 800, False, {"type": "json_object"})

    return response, 200
