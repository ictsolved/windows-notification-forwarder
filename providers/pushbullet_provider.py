"""
Pushbullet Provider
Send notifications via Pushbullet API
"""

import requests
from typing import Optional
from .base_provider import BaseProvider

class PushbulletProvider(BaseProvider):
    """Pushbullet notification provider"""

    API_URL = "https://api.pushbullet.com/v2"

    def __init__(self, api_token: str):
        """
        Initialize Pushbullet provider

        Args:
            api_token: Pushbullet API access token
        """
        super().__init__("Pushbullet")
        self.api_token = api_token
        self.headers = {
            "Access-Token": api_token,
            "Content-Type": "application/json"
        }

    def initialize(self) -> bool:
        """Initialize Pushbullet provider"""
        if not self.api_token or len(self.api_token) < 10:
            self.logger.error("Invalid Pushbullet API token")
            return False

        self.enabled = True
        self.logger.info("✅ Pushbullet initialized")
        return True

    def test_connection(self) -> bool:
        """Test Pushbullet connection"""
        if not self.enabled:
            return False

        try:
            # Test by getting user info
            response = requests.get(
                f"{self.API_URL}/users/me",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("✅ Pushbullet connection test successful")
                return True
            else:
                self.logger.error(f"❌ Pushbullet connection test failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Pushbullet connection test failed: {e}")
            return False

    def send_notification(
        self,
        title: str,
        body: str,
        source_app: Optional[str] = None
    ) -> bool:
        """Send notification via Pushbullet"""
        if not self.enabled:
            return False

        try:
            # Format title with source app if provided
            formatted_title = f"{title}" if source_app else title

            payload = {
                "type": "note",
                "title": formatted_title,
                "body": body or "(No content)"
            }

            response = requests.post(
                f"{self.API_URL}/pushes",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.debug(f"✅ Pushbullet: {title}")
                return True
            else:
                self.logger.warning(f"❌ Pushbullet: Failed ({response.status_code})")
                return False

        except Exception as e:
            self.logger.error(f"❌ Pushbullet error: {e}")
            return False
