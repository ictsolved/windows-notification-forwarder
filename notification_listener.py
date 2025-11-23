"""
Windows Notification Listener using WinRT APIs
Captures all Windows 10/11 toast notifications from any app
"""
import asyncio
import logging
from typing import Callable, Optional
from winrt.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winrt.windows.ui.notifications import NotificationKinds


class WindowsNotificationListener:
    """Listens to Windows notifications and triggers a callback"""

    def __init__(self, callback: Callable[[dict], None]):
        """
        Initialize the notification listener

        Args:
            callback: Function to call when a notification is received.
                     Receives a dict with keys: app_name, title, text
        """
        self.callback = callback
        self.listener: Optional[UserNotificationListener] = None
        self.logger = logging.getLogger(__name__)
        self.event_token = None
        self.seen_notification_ids = set()  # Track processed notifications
        self.poll_interval = 0.5  # Poll every 0.5 seconds

    async def request_access(self) -> bool:
        """
        Request permission to access notifications

        Returns:
            True if permission granted, False otherwise
        """
        try:
            self.listener = UserNotificationListener.current
            access_status = await self.listener.request_access_async()

            if access_status == UserNotificationListenerAccessStatus.ALLOWED:
                self.logger.info("Notification listener access granted")
                return True
            elif access_status == UserNotificationListenerAccessStatus.DENIED:
                self.logger.error("Notification listener access denied by user")
                return False
            else:
                self.logger.error(f"Notification listener access status: {access_status}")
                return False

        except Exception as e:
            self.logger.error(f"Error requesting notification access: {e}")
            return False

    async def _poll_notifications(self):
        """Poll for new notifications periodically"""
        try:
            # Get all current notifications
            notifications = await self.listener.get_notifications_async(NotificationKinds.TOAST)

            if not notifications:
                self.logger.debug("No notifications found in notification center")
                return

            self.logger.debug(f"Found {len(notifications)} notifications in notification center")

            # Process each notification
            for notification in notifications:
                try:
                    # Get notification ID to track duplicates
                    notif_id = notification.id

                    # Skip if we've already processed this notification
                    if notif_id in self.seen_notification_ids:
                        self.logger.debug(f"Skipping already seen notification ID: {notif_id}")
                        continue

                    # Mark as seen
                    self.seen_notification_ids.add(notif_id)
                    self.logger.info(f"Processing new notification ID: {notif_id}")

                    # Process the notification
                    self._process_notification(notification)

                except Exception as e:
                    self.logger.error(f"Error processing individual notification: {e}", exc_info=True)
                    continue

        except Exception as e:
            self.logger.debug(f"Error polling notifications: {e}")

    def _process_notification(self, notification):
        """Process and extract notification details"""
        try:
            # Extract notification details
            app_name = "Unknown App"
            try:
                app_info = notification.app_info
                if app_info and hasattr(app_info, 'display_info') and app_info.display_info:
                    app_name = app_info.display_info.display_name
            except Exception as e:
                self.logger.debug(f"Could not get app name: {e}")

            # Get notification content
            notification_data = notification.notification
            if not notification_data:
                return

            # Extract visual content
            title = ""
            text = ""

            try:
                visual = notification_data.visual
                if visual and hasattr(visual, 'bindings') and visual.bindings:
                    for binding in visual.bindings:
                        try:
                            text_elements = binding.get_text_elements()
                            if text_elements and len(text_elements) > 0:
                                # First element is usually the title
                                if not title and len(text_elements) > 0:
                                    title = text_elements[0].text or ""
                                # Second element is usually the message body
                                if not text and len(text_elements) > 1:
                                    text = text_elements[1].text or ""
                                break
                        except Exception as e:
                            self.logger.debug(f"Error getting text elements from binding: {e}")
                            continue
            except Exception as e:
                self.logger.debug(f"Error extracting visual content: {e}")

            # Build notification dict
            notification_dict = {
                "app_name": app_name,
                "title": title,
                "text": text,
                "timestamp": notification.creation_time.timestamp() if hasattr(notification, 'creation_time') and notification.creation_time else None
            }

            # Call the callback
            if title or text:  # Only trigger if we have some content
                self.callback(notification_dict)

        except Exception as e:
            self.logger.error(f"Error processing notification: {e}", exc_info=True)

    async def start_listening(self):
        """Start listening for notifications using polling"""
        try:
            if not self.listener:
                self.logger.error("Listener not initialized. Call request_access() first.")
                return

            self.logger.info("Started listening for notifications (polling mode)")
            self.logger.info(f"Polling interval: {self.poll_interval} seconds")

            # Try to use event-based listener first, fall back to polling if it fails
            try:
                self.event_token = self.listener.add_notification_changed(self._on_event_notification)
                self.logger.info("Using event-based notification listener")
            except Exception as e:
                self.logger.warning(f"Event-based listener not available: {e}")
                self.logger.info("Falling back to polling mode")

            # Poll for notifications
            while True:
                await self._poll_notifications()
                await asyncio.sleep(self.poll_interval)

        except Exception as e:
            self.logger.error(f"Error in notification listener: {e}", exc_info=True)

    def _on_event_notification(self, sender, args):
        """Handler for event-based notifications (if available)"""
        try:
            notification_id = args.user_notification_id
            notification = self.listener.get_notification(notification_id)
            if notification and notification.id not in self.seen_notification_ids:
                self.seen_notification_ids.add(notification.id)
                self._process_notification(notification)
        except Exception as e:
            self.logger.debug(f"Error in event notification handler: {e}")

    async def stop_listening(self):
        """Stop listening for notifications"""
        try:
            if self.listener and self.event_token:
                self.listener.remove_notification_changed(self.event_token)
                self.logger.info("Stopped listening for notifications")
        except Exception as e:
            self.logger.error(f"Error stopping listener: {e}")
