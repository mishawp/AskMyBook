__all__ = ("user_router", "chat_router", "document_router", "auth_router")

from .user import router as user_router
from .chat import router as chat_router
from .document import router as document_router
from .auth import router as auth_router
