"""
Testing utilities for the chat application.
These functions should ONLY be used in tests, never in production code.
"""
from data.database import Database 
from sqlalchemy.orm import Session
from domain.models import User, Guild, Channel, Message

class DatabaseCleaner:
    """Utility class for cleaning up test data in the database.
    This should only be used in test environments, never in production."""
    
    def __init__(self, db: Database):
        self._db = db
        
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self._db.get_session()
        
    def _cleanup_with_session(self, session: Session, delete_fn) -> bool:
        """Execute a cleanup function with proper session handling."""
        try:
            delete_fn(session)
            session.commit()
            return True
        except Exception as e:
            print(f"Error during test cleanup: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def clear_all_messages(self) -> bool:
        """Delete all messages from the database."""
        session = self._get_session()
        return self._cleanup_with_session(session, lambda s: s.query(Message).delete())
    
    def clear_all_channels(self) -> bool:
        """Delete all channels from the database."""
        session = self._get_session()
        return self._cleanup_with_session(session, lambda s: s.query(Channel).delete())
    
    def clear_all_guilds(self) -> bool:
        """Delete all guilds from the database."""
        session = self._get_session()
        return self._cleanup_with_session(session, lambda s: s.query(Guild).delete())
    
    def clear_all_users_except_default(self) -> bool:
        """Delete all users except the default one (colton)."""
        session = self._get_session()
        return self._cleanup_with_session(
            session, 
            lambda s: s.query(User).filter(User.username != "colton").delete()
        )
    
    def reset_database(self) -> bool:
        """Reset the entire database to a clean state.
        Preserves only the default user (colton)."""
        # Order matters due to foreign key constraints
        return (self.clear_all_messages() and 
                self.clear_all_channels() and 
                self.clear_all_guilds() and 
                self.clear_all_users_except_default()) 