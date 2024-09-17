#!/usr/bin/env python3
"""
DB module
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from datetime import timedelta, datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User
from spotify_tokens import SpotifyToken

class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("mysql+pymysql://root:Kellyjunior6387..@localhost/doba",
                                     echo=False)
        # Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Create a User object and save it to the database
        Args:
            email (str): user's email address
            hashed_password (str): password hashed by bcrypt's hashpw
        Return:
            Newly created User object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

   
    def find_user_by(self, **kwargs) -> User:
        """
        Return a user who has an attribute matching the attributes passed
        as arguments
        Args:
            attributes (dict): a dictionary of attributes to match the user
        Return:
            matching user or raise error
        """
        users = self._session.query(User)
        for k, v in kwargs.items():
            if k not in User.__dict__:
                raise InvalidRequestError
            for usr in users:
                if getattr(usr, k) == v:
                    return usr
        raise NoResultFound

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes
        Args:
            user_id (int): user's id
            kwargs (dict): dict of key, value pairs representing the
                           attributes to update and the values to update
                           them with
        Return:
            No return value
        """
        user = self.find_user_by(id=user_id)
        if user:
            try:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                        self._session.commit()
                    else:
                        raise ValueError
            except NoResultFound:
                raise ValueError

    def add_token(self, session_id: str, access_token: str, refresh_token: str, expires_in: str):
        expiry = datetime.now() + timedelta(seconds=expires_in)
        token = SpotifyToken(session_id=session_id,
                             access_token=access_token,
                             refresh_token=refresh_token,
                             expires_in=expiry)
        self._session.add(token)
        self._session.commit()
        return token
    
    def find_token(self, session_id: str) -> SpotifyToken:
        """
        Return a token with the matching session id
        Args:
            session_id (str): session id to match
        Return:
            matching SpotifyToken object or None if not found
        """
        token = self._session.query(SpotifyToken).filter_by(session_id=session_id).first()
        return token

    def update_token(self, session_id: int, **kwargs) -> None:
        """
        Update a user's attributes
        Args:
            user_id (int): user's id
            kwargs (dict): dict of key, value pairs representing the
                           attributes to update and the values to update
                           them with
        Return:
            No return value
        """
        token = self.find_token(session_id=session_id)
        if token:
            try:
                for key, value in kwargs.items():
                    if hasattr(token, key):
                        setattr(token, key, value)
                        self._session.commit()
                    else:
                        raise ValueError
            except NoResultFound:
                raise ValueError
