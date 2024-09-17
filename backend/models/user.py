from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """Class to declare the user"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True, index=True)  # Remove foreign key constraint here
    reset_token = Column(String(250), nullable=True)
    spotify_tokens = relationship("SpotifyToken", backref="user")
