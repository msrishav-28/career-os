"""
Database package — exports all repository singletons and session utilities.
"""
from db.session import get_db_session, get_sessionmaker
from db.users_repo import users_repo
from db.contacts_repo import contacts_repo
from db.messages_repo import messages_repo
from db.campaigns_repo import campaigns_repo
from db.opportunities_repo import opportunities_repo
from db.insights_repo import insights_repo
from db.activity_repo import activity_repo

__all__ = [
    "get_db_session",
    "get_sessionmaker",
    "users_repo",
    "contacts_repo",
    "messages_repo",
    "campaigns_repo",
    "opportunities_repo",
    "insights_repo",
    "activity_repo",
]
