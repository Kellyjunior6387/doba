import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import uuid
import base64
from models.db import DB
from datetime import timedelta, datetime

CLIENT_ID = '5e95d38b93a1476e84353b37d746a7a9'
REDIRECT_URI = 'http://127.0.0.1:5000/redirect'
CLIENT_SECRET_KEY = os.getenv('CLIENT_SECRET_KEY')

DB = DB()

class Spotify:
    def authorize(self, state):
        """Function to authorize a user in spotify"""
        params = {
            'scope':'user-modify-playback-state',
            'response_type':'code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'state': state
        }
        response = requests.get('https://accounts.spotify.com/authorize',params=params)
        if response.status_code == 200:
            return response
        else:
            # Handle error
            print(f"Error: {response.status_code}")
            return None


    def get_access_token(self, code):
        """Function to get an access token"""
        url = "https://accounts.spotify.com/api/token"
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET_KEY}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'Authorization': f'Basic {b64_auth_str}'

        }
        data = {
            "grant_type": "authorization_code",
             'redirect_uri': REDIRECT_URI,
             'code': code
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def refresh_spotify_token(self, session_id):
        """"""
        token = DB.find_token(session_id=session_id)
        if token:
            refresh_token = token.refresh_token
            print(refresh_token)
        if not refresh_token:            
            return 
        url = 'https://accounts.spotify.com/api/token'
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET_KEY}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {b64_auth_str}'
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            body = response.json()
            print(body)
            access_token= body.get('access_token'),
            refresh_token = body.get('refresh_token', refresh_token),
            expires_in = datetime.now() + timedelta(seconds=body.get('expires_in'))
            DB.update_token(session_id, access_token=access_token,
                            refresh_token=refresh_token,
                            expires_in=expires_in)

    
        
    def is_spotify_authenticated(self, session_id):
        tokens = DB.find_token(session_id=session_id)
        if tokens:
            expiry = tokens.expires_in
            if expiry <= datetime.now():
                self.refresh_spotify_token(session_id)

            return True
        return False

    def add_queue(self, session_id, track_uri):
        """Function to add songs to a user queue"""
        token = DB.find_token(session_id)
        if token:
            access_token = token.access_token
            url = 'https://api.spotify.com/v1/me/player/queue'
            headers = {
                'Authorization': f'Bearer {access_token}'
                }
            params = {
                'uri': track_uri
            }

            response = requests.post(url, headers=headers, params=params)

            if response.status_code == 200:
                print("Track added to queue successfully.")
            else:
                print(f"Failed to add track to queue: {response.status_code}")
                print(response)

    def search_song(self, song: str,artist: str, access_token: str):
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        query = f"track:{song} artist:{artist}"
        params = {
            "q": query,  # Search query (track name)
            "type": "track",  # Specify that you're searching for tracks
            "limit": 1  # Limit the result to 1 track
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['tracks']['items']:
                track = data['tracks']['items'][0]
                #track_id = track['id']  # Track ID
                track_uri = track['uri']  # Track URI
                return track_uri,
            else:
                print("No tracks found.")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    def process_playlist(self, playlist: list):
        """Process the playlist, search for URIs and add them to the queue"""
        for song in playlist:
            title = song['title']
            artist = song['artist']
            track_uri = self.search_song(title, artist)
            if track_uri:
                self.add_to_queue(track_uri,)
            else:
                print(f"Could not find URI for {title} by {artist}")

