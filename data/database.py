from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
# from sqlalchemy.ext.declarative import declarative_base  # Deprecated in 2.0

Base = declarative_base()

class Database:
    def __init__(self, db_url: str = "sqlite:///new_web_server.db", echo: bool = False):
        """Initialize the database connection.

        Args:
            db_url: The database URL to connect to.
            echo: If True, the database will echo SQL commands.
        """
        self.engine = create_engine(db_url, echo=echo)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Create all tables defined in the models."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Provides a new database session."""
        return self.SessionLocal()

    def commit_session(self, session: Session):
        """Commits a session's changes to the database and closes the session."""
        session.commit()
        session.close()

    def close_session(self, session: Session):
        """Closes a session without committing any changes."""
        session.close()
        
    def rollback_session(self, session: Session):
        """Rolls back a session and closes it."""
        session.rollback()
        session.close() 