import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from spotify.Spotify import Spotify
from models.db import DB

class TestSpotify(unittest.TestCase):

    @patch('Spotify.DB.find_token')
    @patch('Spotify.Spotify.refresh_spotify_token')
    def test_is_spotify_authenticated(self, mock_refresh_token, mock_find_token):
        # Mock token with expiry in the future
        mock_token = MagicMock()
        mock_token.expires_in = datetime.now() + timedelta(hours=1)
        mock_find_token.return_value = mock_token

        spotify = Spotify()
        session_id = 'test_session_id'
        result = spotify.is_spotify_authenticated(session_id)

        self.assertTrue(result)
        mock_refresh_token.assert_not_called()

        # Mock token with expiry in the past
        mock_token.expires_in = datetime.now() - timedelta(hours=1)
        mock_find_token.return_value = mock_token

        result = spotify.is_spotify_authenticated(session_id)

        self.assertTrue(result)
        mock_refresh_token.assert_called_once_with(session_id)

        # Mock no token found
        mock_find_token.return_value = None

        result = spotify.is_spotify_authenticated(session_id)

        self.assertFalse(result)

    @patch('Spotify.requests.post')
    @patch('Spotify.DB.find_token')
    def test_add_queue(self, mock_find_token, mock_requests_post):
        # Mock token
        mock_token = MagicMock()
        mock_token.access_token = 'test_access_token'
        mock_find_token.return_value = mock_token

        spotify = Spotify()
        session_id = 'test_session_id'
        track_uri = 'spotify:track:test_uri'
        spotify.add_queue(session_id, track_uri)

        mock_find_token.assert_called_once_with(session_id)
        mock_requests_post.assert_called_once_with(
            'https://api.spotify.com/v1/me/player/queue',
            headers={'Authorization': 'Bearer test_access_token'},
            params={'uri': track_uri}
        )

        # Mock no token found
        mock_find_token.return_value = None
        mock_requests_post.reset_mock()

        spotify.add_queue(session_id, track_uri)

        mock_requests_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
