#!/usr/bin/env python3
"""Module to encrypt a password"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
import bcrypt
from models.db import DB
from models.user import User
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> bytes:
    """Method to encrypt passowrd using bcrypt"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed


def _generate_uuid() -> str:
    """
    Generate a random uuid and convert to string
    """
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Method to register a unregistered user"""
        if email and password:
            try:
                self._db.find_user_by(email=email)
            except NoResultFound:
                return self._db.add_user(email, _hash_password(password))
            raise ValueError(f'User {email} already exists')

    def valid_login(self, email: str, password: str) -> bool:
        """Method to validate a user's password"""
        try:
            user = self._db.find_user_by(email=email)
            hashed_password = user.hashed_password.encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """Method to create a session in the DB"""
        try:
            user = self._db.find_user_by(email=email)
            id = _generate_uuid()
            self._db.update_user(user.id, session_id=id)
            user.session_id = id
            return id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> str:
        """Method to retrieve a user with a given session_id"""
        if session_id:
            try:
                user = self._db.find_user_by(session_id=session_id)
                return user
            except NoResultFound:
                return None
        return None

    def destroy_session(self, user_id: int) -> None:
        """Method to destroy a user session id"""
        if user_id:
            self._db.update_user(user_id, session_id=None)
        return None

    def get_reset_password_token(self, email: str) -> None:
        """Method to generate the reset token of a user"""
        if email:
            try:
                user = self._db.find_user_by(email=email)
                reset_token = _generate_uuid()
                self._db.update_user(user.id, reset_token=reset_token)
                return reset_token
            except NoResultFound:
                raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """Method to update the password using reset token"""
        if reset_token and password:
            try:
                user = self._db.find_user_by(reset_token=reset_token)
                hashed_passwd = _hash_password(password)
                self._db.update_user(user.id,
                                     hashed_password=hashed_passwd,
                                     reset_token=None)
                return None
            except NoResultFound:
                raise ValueError

