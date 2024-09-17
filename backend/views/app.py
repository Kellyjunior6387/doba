#!usr/bin/python3
"""Module to start the flask app"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from groq_llm import groq
from auth import auth
from views.Spotify import spotify
from flask_swagger_ui import get_swaggerui_blueprint

AUTH_URL = '/docs/auth'
AUTH_API_URL = os.path.join(os.path.dirname(__file__), '/static/docs/auth_swagger.yaml')
auth_swagger_ui_blueprint = get_swaggerui_blueprint(AUTH_URL, AUTH_API_URL,config={'app_name': "AUTH API"})

LLM_URL = '/docs/llm'
LLM_API_URL = os.path.join(os.path.dirname(__file__), '/static/docs/llm-swagger.yaml')
llm_swagger_ui_blueprint = get_swaggerui_blueprint(LLM_URL, LLM_API_URL,config={'app_name': "LLM API"})

SPOTIFY_URL = '/docs/spotify'
SPOTIFY_API_URL = os.path.join(os.path.dirname(__file__), '/static/docs/spotify-swagger.yaml')
spotify_swagger_ui_blueprint = get_swaggerui_blueprint(SPOTIFY_URL, SPOTIFY_API_URL,config={'app_name': "Spotify API"})

app = Flask(__name__)

# Register blueprints with the app
app.register_blueprint(groq)
app.register_blueprint(auth)
app.register_blueprint(spotify)
app.register_blueprint(auth_swagger_ui_blueprint, url_prefix=AUTH_URL, name='auth_swagger_ui')
app.register_blueprint(llm_swagger_ui_blueprint, url_prefix=LLM_URL, name='llm_swagger_ui')
app.register_blueprint(spotify_swagger_ui_blueprint, url_prefix=SPOTIFY_URL, name='spotify_swagger_ui')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000",debug=True, )
