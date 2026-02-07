"""Task names and utilities for cross-service communication via RabbitMQ.

This package provides shared contracts for Taskiq-based task communication:
- names.py: Task name constants (TaskNames enum)

Future extensions:
- payloads.py: Pydantic schemas for task parameters validation
- results.py: Task result schemas
- decorators.py: Common task decorators and utilities
"""

from .names import TaskNames

__all__ = ["TaskNames"]
