"""Base model class."""
from app.database import Base as DatabaseBase

# Re-export database base
Base = DatabaseBase
