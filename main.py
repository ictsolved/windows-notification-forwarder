"""
Windows Notification Forwarder
Forwards Windows notifications to multiple channels (FCM, Pushbullet, Ntfy)
"""
import asyncio
import logging
import sys
from pathlib import Path

from config import Config
from notification_listener import WindowsNotificationListener
from providers import ProviderManager, FCMProvider, PushbulletProvider, NtfyProvider


def setup_logging():
    """Configure logging for the application with UTF-8 encoding support"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler with UTF-8 encoding for Windows compatibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler("notification_forwarder.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[console_handler, file_handler]
    )

    # Ensure stdout uses UTF-8 on Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class NotificationForwarder:
    """Main application class that coordinates notification listening and forwarding"""

    def __init__(self):
        """Initialize the notification forwarder"""
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.provider_manager: ProviderManager = ProviderManager()
        self.listener: WindowsNotificationListener = None

    async def run(self):
        """Main application loop"""
        try:
            # Validate configuration
            self.logger.info("=" * 60)
            self.logger.info("Starting Windows Notification Forwarder")
            self.logger.info("=" * 60)

            if not self.config.validate():
                self.logger.error("Invalid configuration. Please check your .env file.")
                return

            # Initialize providers
            self.logger.info("Initializing notification providers...")

            # Add FCM provider if enabled
            if self.config.fcm_enabled:
                fcm = FCMProvider(
                    service_account_file=self.config.fcm_service_account_file,
                    topic=self.config.fcm_topic
                )
                self.provider_manager.add_provider(fcm)

            # Add Pushbullet provider if enabled
            if self.config.pushbullet_enabled:
                pushbullet = PushbulletProvider(
                    api_token=self.config.pushbullet_api_token
                )
                self.provider_manager.add_provider(pushbullet)

            # Add Ntfy provider if enabled
            if self.config.ntfy_enabled:
                ntfy = NtfyProvider(
                    server_url=self.config.ntfy_server_url,
                    topic=self.config.ntfy_topic,
                    username=self.config.ntfy_username if self.config.ntfy_username else None,
                    password=self.config.ntfy_password if self.config.ntfy_password else None
                )
                self.provider_manager.add_provider(ntfy)

            # Check if any providers are enabled
            provider_count = self.provider_manager.get_provider_count()
            if provider_count == 0:
                self.logger.error("No notification providers enabled!")
                return

            self.logger.info(f"{self.provider_manager.get_summary()}")
            self.logger.info("=" * 60)

            # Initialize notification listener
            self.listener = WindowsNotificationListener(self._on_notification_received)

            # Request notification access
            self.logger.info("Requesting notification access...")
            if not await self.listener.request_access():
                self.logger.error(
                    "Failed to get notification access. "
                    "Please grant permission in Windows Settings > Privacy > Notifications"
                )
                return

            # Start listening
            self.logger.info("Starting notification listener...")
            self.logger.info("Forwarding Windows notifications to enabled providers. Press Ctrl+C to stop.")
            self.logger.info("=" * 60)

            await self.listener.start_listening()

        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
        finally:
            await self.shutdown()

    def _on_notification_received(self, notification: dict):
        """
        Callback function called when a notification is received

        Args:
            notification: Dict containing app_name, title, text, timestamp
        """
        try:
            app_name = notification.get("app_name", "Unknown")
            title = notification.get("title", "")
            text = notification.get("text", "")

            self.logger.info(f"Received notification from {app_name}: {title}")

            # Check if we should forward this notification
            if not self.config.should_forward_notification(app_name):
                self.logger.debug(f"Skipping notification from {app_name} (filtered)")
                return

            # Forward to all enabled providers
            results = self.provider_manager.send_notification(
                title=title,
                body=text,
                source_app=app_name
            )

        except Exception as e:
            self.logger.error(f"Error handling notification: {e}", exc_info=True)

    async def shutdown(self):
        """Cleanup resources"""
        self.logger.info("Shutting down...")
        if self.listener:
            await self.listener.stop_listening()
        self.logger.info("Shutdown complete")


async def main():
    """Application entry point"""
    # Setup logging
    setup_logging()

    # Get the directory where the script/exe is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent

    # Check if .env file exists in app directory
    env_file = app_dir / ".env"
    logging.info(f"Looking for .env file at: {env_file}")
    logging.info(f"Current working directory: {Path.cwd()}")
    logging.info(f"App directory: {app_dir}")

    if not env_file.exists():
        logging.error(
            f"No .env file found at {env_file}!"
        )
        logging.error("Please copy .env.example to .env and configure it in the same folder as the executable.")
        input("\nPress Enter to exit...")
        return

    logging.info(f"Found .env file at: {env_file}")

    # Change to app directory so dotenv can find .env
    import os
    os.chdir(app_dir)

    # Create and run the forwarder
    forwarder = NotificationForwarder()
    await forwarder.run()


if __name__ == "__main__":
    # Run the async application
    asyncio.run(main())
