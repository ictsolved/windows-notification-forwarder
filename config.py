"""
Configuration management for the notification forwarder
"""
import os
import logging
from typing import List, Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""

    def __init__(self):
        """Load configuration from environment variables"""
        # Load .env file if it exists
        load_dotenv()

        self.logger = logging.getLogger(__name__)

        # ======================
        # Provider Configurations
        # ======================

        # FCM Configuration
        self.fcm_enabled: bool = self._is_provider_enabled("FCM")
        self.fcm_service_account_file: str = os.getenv("FCM_SERVICE_ACCOUNT_FILE", "service-account.json")
        self.fcm_topic: str = os.getenv("FCM_TOPIC", "windows_notifications")

        # Pushbullet Configuration
        self.pushbullet_enabled: bool = self._is_provider_enabled("PUSHBULLET")
        self.pushbullet_api_token: str = os.getenv("PUSHBULLET_API_TOKEN", "")

        # Ntfy Configuration
        self.ntfy_enabled: bool = self._is_provider_enabled("NTFY")
        self.ntfy_server_url: str = os.getenv("NTFY_SERVER_URL", "https://ntfy.sh")
        self.ntfy_topic: str = os.getenv("NTFY_TOPIC", "windows_notifications")
        self.ntfy_username: str = os.getenv("NTFY_USERNAME", "")
        self.ntfy_password: str = os.getenv("NTFY_PASSWORD", "")

        # ======================
        # App Filtering
        # ======================
        ignored_apps = os.getenv("IGNORED_APPS", "")
        self.ignored_apps: List[str] = [app.strip() for app in ignored_apps.split(",") if app.strip()]

        whitelist_apps = os.getenv("WHITELIST_APPS", "")
        self.whitelist_apps: List[str] = [app.strip() for app in whitelist_apps.split(",") if app.strip()]

    def _is_provider_enabled(self, provider: str) -> bool:
        """
        Check if a provider is enabled via environment variable

        Args:
            provider: Provider name (FCM, PUSHBULLET, NTFY)

        Returns:
            True if provider should be enabled
        """
        env_key = f"ENABLE_{provider}"
        env_value = os.getenv(env_key, "").lower()

        # If not explicitly set, we'll check for credentials later
        if not env_value:
            return True  # Default to enabled if not specified

        return env_value in ('true', '1', 'yes', 'on')

    def validate_fcm(self) -> bool:
        """Validate FCM configuration"""
        if not self.fcm_enabled:
            return True  # Skip validation if disabled

        if not os.path.exists(self.fcm_service_account_file):
            self.logger.warning(f"⚠️  FCM disabled: Service account file not found: {self.fcm_service_account_file}")
            self.fcm_enabled = False
            return False

        return True

    def validate_pushbullet(self) -> bool:
        """Validate Pushbullet configuration"""
        if not self.pushbullet_enabled:
            return True  # Skip validation if disabled

        if not self.pushbullet_api_token or len(self.pushbullet_api_token) < 10:
            self.logger.warning("⚠️  Pushbullet disabled: API token not configured")
            self.pushbullet_enabled = False
            return False

        return True

    def validate_ntfy(self) -> bool:
        """Validate Ntfy configuration"""
        if not self.ntfy_enabled:
            return True  # Skip validation if disabled

        if not self.ntfy_server_url or not self.ntfy_topic:
            self.logger.warning("⚠️  Ntfy disabled: Server URL or topic not configured")
            self.ntfy_enabled = False
            return False

        return True

    def validate(self) -> bool:
        """
        Validate all provider configurations

        Returns:
            True if at least one provider is valid
        """
        self.validate_fcm()
        self.validate_pushbullet()
        self.validate_ntfy()

        # Check if at least one provider is enabled
        enabled_count = sum([
            self.fcm_enabled,
            self.pushbullet_enabled,
            self.ntfy_enabled
        ])

        if enabled_count == 0:
            self.logger.error("❌ No notification providers enabled!")
            self.logger.error("Please configure at least one provider in .env file")
            return False

        return True

    def should_forward_notification(self, app_name: str) -> bool:
        """
        Check if a notification from the given app should be forwarded

        Args:
            app_name: Name of the app that sent the notification

        Returns:
            True if notification should be forwarded, False otherwise
        """
        # If whitelist is defined, only forward apps in whitelist
        if self.whitelist_apps:
            return app_name in self.whitelist_apps

        # If no whitelist, forward all except ignored apps
        if self.ignored_apps:
            return app_name not in self.ignored_apps

        # If no filters defined, forward everything
        return True

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled provider names"""
        providers = []
        if self.fcm_enabled:
            providers.append("FCM")
        if self.pushbullet_enabled:
            providers.append("Pushbullet")
        if self.ntfy_enabled:
            providers.append("Ntfy")
        return providers

    def __repr__(self) -> str:
        """String representation of config"""
        enabled_providers = self.get_enabled_providers()
        return (
            f"Config(\n"
            f"  enabled_providers={enabled_providers}\n"
            f"  ignored_apps={self.ignored_apps}\n"
            f"  whitelist_apps={self.whitelist_apps}\n"
            f")"
        )
