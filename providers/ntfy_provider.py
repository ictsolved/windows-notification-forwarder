"""
Ntfy Provider
Send notifications via ntfy.sh (or self-hosted ntfy server)
"""

import requests
from typing import Optional
from .base_provider import BaseProvider

class NtfyProvider(BaseProvider):
    """Ntfy notification provider"""

    def __init__(
        self,
        server_url: str = "https://ntfy.sh",
        topic: str = "windows_notifications",
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Ntfy provider

        Args:
            server_url: Ntfy server URL (default: https://ntfy.sh)
            topic: Ntfy topic to publish to
            username: Optional username for basic auth
            password: Optional password for basic auth
        """
        super().__init__("Ntfy")
        self.server_url = server_url.rstrip('/')
        self.topic = topic
        self.endpoint = f"{self.server_url}/{self.topic}"

        # Setup basic auth if credentials provided
        self.auth = None
        if username and password:
            self.auth = (username, password)
            self.logger.debug(f"Basic auth enabled for user: {username}")

    def initialize(self) -> bool:
        """Initialize Ntfy provider"""
        if not self.server_url or not self.topic:
            self.logger.error("Invalid Ntfy configuration")
            return False

        self.enabled = True
        self.logger.info(f"✅ Ntfy initialized (server: {self.server_url}, topic: {self.topic})")
        return True

    def test_connection(self) -> bool:
        """Test Ntfy connection"""
        if not self.enabled:
            return False

        try:
            # Test by sending a simple ping
            response = requests.post(
                self.endpoint,
                data="Connection test",
                headers={
                    "Title": "Connection Test",
                    "Priority": "low",
                    "Tags": "white_check_mark"
                },
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("✅ Ntfy connection test successful")
                return True
            else:
                self.logger.error(f"❌ Ntfy connection test failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ntfy connection test failed: {e}")
            return False

    def send_notification(
        self,
        title: str,
        body: str,
        source_app: Optional[str] = None
    ) -> bool:
        """Send notification via Ntfy"""
        if not self.enabled:
            return False

        try:
            # Format title with source app if provided
            formatted_title = f"{title}" if source_app else title

            headers = {
                "Title": formatted_title,
                "Priority": "default",
                "Tags": "computer"
            }

            # Add source app as a tag if provided
            if source_app:
                headers["Tags"] = f"computer,{source_app.lower().replace(' ', '_')}"

            response = requests.post(
                self.endpoint,
                data=body or "(No content)",
                headers=headers,
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.debug(f"✅ Ntfy: {title}")
                return True
            else:
                self.logger.warning(f"❌ Ntfy: Failed ({response.status_code})")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ntfy error: {e}")
            return False
