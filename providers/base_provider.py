"""
Base Provider Interface
Abstract base class for all notification providers
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging


class BaseProvider(ABC):
    """Abstract base class for notification providers"""

    def __init__(self, name: str):
        """
        Initialize the provider

        Args:
            name: Provider name (e.g., 'FCM', 'Pushbullet', 'Ntfy')
        """
        self.name = name
        self.logger = logging.getLogger(f"Provider.{name}")
        self.enabled = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the provider with configuration

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def send_notification(
        self,
        title: str,
        body: str,
        source_app: Optional[str] = None
    ) -> bool:
        """
        Send a notification

        Args:
            title: Notification title
            body: Notification body/message
            source_app: Source application name (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the provider connection

        Returns:
            True if connection is working, False otherwise
        """
        pass

    def is_enabled(self) -> bool:
        """Check if provider is enabled"""
        return self.enabled

    def get_name(self) -> str:
        """Get provider name"""
        return self.name
