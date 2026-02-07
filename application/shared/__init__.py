"""Shared package for AskMyBook application.

This package contains:
- core: Database, storage, and broker managers
- models: SQLModel definitions shared across services
- tasks: Task names for cross-service communication
"""

from .tasks import TaskNames

__all__ = ["TaskNames"]
