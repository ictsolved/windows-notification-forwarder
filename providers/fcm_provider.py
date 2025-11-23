"""
Firebase Cloud Messaging Provider
Modern FCM HTTP v1 API with OAuth2 authentication
"""

import os
from typing import Optional
from .base_provider import BaseProvider
from utils.fcm_v1_helper import FCMv1Notifier


class FCMProvider(BaseProvider):
    """Firebase Cloud Messaging notification provider"""

    def __init__(self, service_account_file: str, topic: str = 'windows_notifications'):
        """
        Initialize FCM provider

        Args:
            service_account_file: Path to Firebase service account JSON file
            topic: FCM topic to send notifications to
        """
        super().__init__("FCM")
        self.service_account_file = service_account_file
        self.topic = topic
        self.fcm = None

    def initialize(self) -> bool:
        """Initialize FCM with service account"""
        try:
            # Check if service account file exists
            if not os.path.exists(self.service_account_file):
                self.logger.error(f"Service account file not found: {self.service_account_file}")
                return False

            # Initialize FCM notifier
            self.fcm = FCMv1Notifier(self.service_account_file)
            self.enabled = True
            self.logger.info(f"✅ FCM initialized (topic: {self.topic})")
            return True

        except Exception as e:
            self.logger.error(f"❌ FCM initialization failed: {e}")
            return False

    def test_connection(self) -> bool:
        """Test FCM connection"""
        if not self.enabled or not self.fcm:
            return False

        try:
            # Try to get access token (verifies service account)
            access_token = self.fcm.get_access_token()
            if access_token:
                self.logger.info("✅ FCM connection test successful")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ FCM connection test failed: {e}")
            return False

    def send_notification(
        self,
        title: str,
        body: str,
        source_app: Optional[str] = None
    ) -> bool:
        """Send notification via FCM"""
        if not self.enabled or not self.fcm:
            return False

        try:
            success = self.fcm.send_to_topic(
                topic=self.topic,
                title=title,
                body=body or "(No content)",
                category="Windows",
                source=source_app or "Unknown"
            )

            if success:
                self.logger.debug(f"✅ FCM: {title}")
            else:
                self.logger.warning(f"❌ FCM: Failed to send '{title}'")

            return success

        except Exception as e:
            self.logger.error(f"❌ FCM error: {e}")
            return False
