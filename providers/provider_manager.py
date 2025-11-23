"""
Provider Manager
Manages multiple notification providers and sends to all enabled providers
"""

import logging
from typing import List, Optional
from .base_provider import BaseProvider


class ProviderManager:
    """Manages multiple notification providers"""

    def __init__(self):
        """Initialize the provider manager"""
        self.providers: List[BaseProvider] = []
        self.logger = logging.getLogger(__name__)

    def add_provider(self, provider: BaseProvider) -> bool:
        """
        Add a provider to the manager

        Args:
            provider: Provider instance to add

        Returns:
            True if provider added successfully
        """
        try:
            # Initialize the provider
            if provider.initialize():
                self.providers.append(provider)
                self.logger.info(f"✅ Added provider: {provider.get_name()}")
                return True
            else:
                self.logger.warning(f"⚠️  Failed to initialize provider: {provider.get_name()}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error adding provider {provider.get_name()}: {e}")
            return False

    def get_enabled_providers(self) -> List[BaseProvider]:
        """Get list of enabled providers"""
        return [p for p in self.providers if p.is_enabled()]

    def get_provider_count(self) -> int:
        """Get number of enabled providers"""
        return len(self.get_enabled_providers())

    def test_all_connections(self) -> dict:
        """
        Test all provider connections

        Returns:
            Dictionary with provider names as keys and test results as values
        """
        results = {}
        for provider in self.providers:
            if provider.is_enabled():
                results[provider.get_name()] = provider.test_connection()
        return results

    def send_notification(
        self,
        title: str,
        body: str,
        source_app: Optional[str] = None
    ) -> dict:
        """
        Send notification to all enabled providers

        Args:
            title: Notification title
            body: Notification body/message
            source_app: Source application name (optional)

        Returns:
            Dictionary with provider names as keys and send results as values
        """
        results = {}
        enabled_providers = self.get_enabled_providers()

        if not enabled_providers:
            self.logger.warning("No enabled providers to send notification")
            return results

        for provider in enabled_providers:
            try:
                success = provider.send_notification(title, body, source_app)
                results[provider.get_name()] = success
            except Exception as e:
                self.logger.error(f"Error sending via {provider.get_name()}: {e}")
                results[provider.get_name()] = False

        # Log summary
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        self.logger.info(f"📤 Sent to {successful}/{total} providers")

        return results

    def get_summary(self) -> str:
        """Get a summary of enabled providers"""
        enabled = self.get_enabled_providers()
        if not enabled:
            return "No providers enabled"

        provider_names = [p.get_name() for p in enabled]
        return f"Enabled providers ({len(provider_names)}): {', '.join(provider_names)}"
