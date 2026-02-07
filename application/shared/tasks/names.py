"""Centralized task names for Taskiq cross-service communication.

All task names must be defined here to ensure consistency between services.
Using Enum provides type safety and autocomplete support.

Naming Convention:
    Format: "tasks.{service}.{action}"
    - service: target service name (ingestion, indexing, retrieval, etc.)
    - action: what the task does (process_document, create_embeddings, etc.)

Usage:
    # In producer service (app):
    from shared.tasks import TaskNames
    await task.kiq(...) where task decorated with str(TaskNames.PROCESS_DOCUMENT)

    # In consumer service (ingestion):
    from shared.tasks import TaskNames
    @broker.task(task_name=str(TaskNames.PROCESS_DOCUMENT))
"""

from enum import Enum


class TaskNames(str, Enum):
    """Task names for RabbitMQ message routing between microservices."""

    # ===== Document Ingestion Service =====
    PROCESS_DOCUMENT = "tasks.ingestion.process_document"
    # Future: EXTRACT_TEXT, PARSE_STRUCTURE, etc.

    # ===== Indexing Service (future) =====
    # CREATE_EMBEDDINGS = "tasks.indexing.create_embeddings"
    # UPDATE_VECTORS = "tasks.indexing.update_vectors"
    # INDEX_CHUNKS = "tasks.indexing.index_chunks"

    def __str__(self) -> str:
        """Return string value for direct usage."""
        return self.value
