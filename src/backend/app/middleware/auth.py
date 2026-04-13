"""Auth middleware dependency exports.

This module provides a stable import path for route dependencies while the
actual JWT logic is implemented in app.services.auth_service.
"""

from app.services.auth_service import UserContext, get_current_user, require_role

__all__ = ["UserContext", "get_current_user", "require_role"]

