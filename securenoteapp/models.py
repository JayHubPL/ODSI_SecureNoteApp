from flask_login import UserMixin
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, CHAR

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String(1000), nullable=False)


class Note(db.Model):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    owner_id = Column(ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False, default="Untitled note")
    content = Column(Text, nullable=False, default="")
    is_public = Column(Boolean, default=False, nullable=False)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    password = Column(String(100), nullable=True)
    uuid = Column(CHAR(36), unique=True, nullable=True)


class Share(db.Model):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True)
    note_id = Column(ForeignKey("notes.id"))
    viewer_id = Column(ForeignKey("users.id"))
