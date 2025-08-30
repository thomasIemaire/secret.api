"""Base class for service layers."""

from dataclasses import dataclass
from pymongo.database import Database


@dataclass(slots=True)
class BaseService:
    """Simple container for the Mongo database instance."""

    db: Database

