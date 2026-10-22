"""
Caregiver Notification Service and Adapter Interface.
Manages high-priority emergency alerts, push notifications, and caregiver contacts.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from lumi_backend.config import settings

logger = logging.getLogger(__name__)


class NotificationAdapter(ABC):
    @abstractmethod
    def send_emergency_alert(self, title: str, message: str, event_data: Dict[str, Any]) -> bool:
        pass


class ConsoleAndLogNotificationAdapter(NotificationAdapter):
    """Default adapter logging alerts to console and logger with structured format."""

    def send_emergency_alert(self, title: str, message: str, event_data: Dict[str, Any]) -> bool:
        logger.critical(
            f"!!! CAREGIVER NOTIFICATION ALERT !!!\n"
            f"Title: {title}\n"
            f"Message: {message}\n"
            f"Contact: {settings.caregiver_name} ({settings.caregiver_phone})\n"
            f"Event Data: {event_data}"
        )
        return True


class NotificationManager:
    def __init__(self, adapter: Optional[NotificationAdapter] = None) -> None:
        self.adapter = adapter or ConsoleAndLogNotificationAdapter()
        self.emergency_contacts = [
            {"name": settings.caregiver_name, "phone": settings.caregiver_phone, "role": "Primary Caregiver"},
            {"name": "Emergency Services", "phone": settings.emergency_contact_phone, "role": "First Responder"},
        ]

    def notify_emergency(self, title: str, message: str, event_data: Dict[str, Any]) -> bool:
        return self.adapter.send_emergency_alert(title, message, event_data)

    def get_emergency_contacts(self) -> List[Dict[str, str]]:
        return self.emergency_contacts
