"""
Auto-updater module for the Unsplash Image Search application.

This module provides:
- GitHub releases integration
- Version comparison and checksum verification
- Background download and safe update application
- UI components for update notifications
- Rollback capability
- Optional and configurable update checking
"""

from .auto_updater import AutoUpdater, UpdateInfo, UpdateError
from .update_dialog import UpdateDialog, UpdateProgressDialog

__all__ = ["AutoUpdater", "UpdateInfo", "UpdateError", "UpdateDialog", "UpdateProgressDialog"]