from flask import Blueprint
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spotify.Spotify import Spotify
from models.db import DB
from flask import (
    request,
    jsonify,
    abort,
    redirect,
    session
      )
DB = DB()
Spotify = Spotify()

spotify = Blueprint('spotify', __name__)


@spotify.route("/spotify-auth", methods=["GET"], strict_slashes=False)
def authorize_spotify() -> str:
    """Authorise spotfify"""
    session_id = request.cookies.get("session_id")
    if session_id is None:
        return jsonify({'ERROR':'You must to be logged in'}), 400
    token = DB.find_token(session_id=session_id)
    if token:
        return jsonify({'Message': 'Already logged in '}), 200
    link = Spotify.authorize(session_id)
    return f'Follow this link to authorize: {link}', 200

@spotify.route("/redirect", strict_slashes=False)
def get_access_token():
    """Function to get access token from spotify and store in DB"""
    session_id = request.args.get('state')
    code = request.args.get('code')
    print(code)
    token = DB.find_token(session_id=session_id)
    if token:
        return jsonify({'Message': 'Token already exists'})
    response = Spotify.get_access_token(code=code)
    if response:
        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')
        DB.add_token(session_id=session_id,
                            access_token=access_token,
                            refresh_token=refresh_token,
                            expires_in=expires_in)
        return jsonify({'message': 'Succesfully created token'}, 200)

@spotify.route("/search-songs", methods=["GET"], strict_slashes=False)
def search_song():
    """Add songs to the users to queue"""
    song = request.args.get('song')
    artist = request.args.get('artist')
    if song is None or artist is None:
        return jsonify({'Error': 'Please provide all the arguments'}), 400
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return jsonify({'Error': 'You must be logged in'}), 401
    if Spotify.is_spotify_authenticated(session_id=session_id):
        token = DB.find_token(session_id=session_id)
        access_token = token.access_token
        uri = Spotify.search_song(song, artist, access_token)
        Spotify.add_queue(session_id, uri)
        return jsonify({'uri': uri}), 200

@spotify.route('/add-songs-to-queue', methods=['POST'], strict_slashes=False)
def add_to_queue():
    """Add songs to the queue"""
    data = request.get_json()
    playlist = data.get('playlist')
    session_id = request.cookies.get('session_id')
    if Spotify.is_spotify_authenticated(session_id=session_id):
        token = DB.find_token(session_id=session_id)
        if playlist and session_id:
            for song in playlist:
                title = song['title']
                artist = song['artist']
                track_uri = Spotify.search_song(title, artist, token.access_token)
                if track_uri:
                    Spotify.add_queue(session_id, track_uri)
                else:
                    print(f"Could not find URI for {title} by {artist}")
            return jsonify({'Message': 'Succesfully added to queue'}), 200
    return jsonify({'Error': 'An error occurred'}), 400


