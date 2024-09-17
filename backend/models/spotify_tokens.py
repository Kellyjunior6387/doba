from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()

class SpotifyToken(Base):
    """Class to declare the Spotify tokens"""
    __tablename__ = 'spotify_tokens'
    id = Column(Integer, primary_key=True)
    access_token = Column(String(250), nullable=False)
    refresh_token = Column(String(250), nullable=False)
    session_id = Column(String(250), ForeignKey('users.session_id'))  # Keep the foreign key here
    expires_in = Column(DateTime())
