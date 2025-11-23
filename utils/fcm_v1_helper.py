"""
FCM HTTP v1 API Helper - Modern way to send notifications
Uses service account credentials and OAuth2 instead of legacy server key

Prerequisites:
    pip install google-auth requests

Setup:
    1. Go to Firebase Console > Project Settings > Service Accounts
    2. Click "Generate new private key"
    3. Save the JSON file as 'service-account.json'
    4. Place it in the same directory as this script

Usage:
    from fcm_v1_helper import FCMv1Notifier

    fcm = FCMv1Notifier('service-account.json')
    fcm.send_to_topic('all_notifications', 'Hello', 'This is a test')
"""
import json
import requests
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2 import service_account

class FCMv1Notifier:
    """Send push notifications via Firebase Cloud Messaging HTTP v1 API"""

    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

    def __init__(self, service_account_file: str):
        """
        Initialize FCM v1 Notifier

        Args:
            service_account_file: Path to Firebase service account JSON file
        """
        self.service_account_file = service_account_file
        self.project_id = self._load_project_id()
        self.fcm_url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"

    def _load_project_id(self) -> str:
        """Load project ID from service account file"""
        with open(self.service_account_file, 'r') as f:
            service_account_info = json.load(f)
        return service_account_info['project_id']

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token using service account credentials

        Returns:
            Access token string
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.SCOPES
        )
        request = Request()
        credentials.refresh(request)
        return credentials.token

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        category: str = "General",
        source: str = "Python",
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send a push notification to a topic

        Args:
            topic: Topic name (e.g., 'all_notifications', 'windows_notifications')
            title: Notification title
            body: Notification body/message
            category: Category (General, Windows, Alert, Info, System)
            source: Source of the notification
            data: Additional custom data (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        access_token = self._get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        payload = {
            'message': {
                'topic': topic,
                'notification': {
                    'title': title,
                    'body': body
                },
                'data': {
                    'category': category,
                    'source': source,
                    **(data or {})
                },
                'android': {
                    'priority': 'high',
                    'notification': {
                        'sound': 'default'
                    }
                }
            }
        }

        try:
            response = requests.post(
                self.fcm_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Notification sent to topic '{topic}': {title}")
                print(f"  Message ID: {result.get('name', 'N/A')}")
                return True
            else:
                print(f"✗ HTTP Error {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def send_windows_notification(
        self,
        app_name: str,
        title: str,
        body: str,
        topic: str = 'windows_notifications'
    ) -> bool:
        """
        Send a Windows notification to topic (shortcut method)

        Args:
            app_name: Windows app that triggered the notification
            title: Notification title
            body: Notification body
            topic: Topic to send to (default: 'windows_notifications')

        Returns:
            True if sent successfully
        """
        return self.send_to_topic(
            topic=topic,
            title=f"{title}" if title else f"[{app_name}]",
            body=body,
            category="Windows",
            source=app_name
        )

    def send_to_condition(
        self,
        condition: str,
        title: str,
        body: str,
        category: str = "General",
        source: str = "Python"
    ) -> bool:
        """
        Send notification based on a condition (advanced targeting)

        Args:
            condition: FCM condition expression
                      Example: "'windows_notifications' in topics && 'premium' in topics"
            title: Notification title
            body: Notification body
            category: Category
            source: Source

        Returns:
            True if sent successfully
        """
        access_token = self._get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        payload = {
            'message': {
                'condition': condition,
                'notification': {
                    'title': title,
                    'body': body
                },
                'data': {
                    'category': category,
                    'source': source
                }
            }
        }

        try:
            response = requests.post(
                self.fcm_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print(f"✓ Notification sent to condition: {title}")
                return True
            else:
                print(f"✗ HTTP Error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize with service account file
    fcm = FCMv1Notifier('service-account.json')

    # Send to all_notifications topic
    print("\n=== Sending to all_notifications topic ===")
    fcm.send_to_topic(
        topic='all_notifications',
        title='Test Notification',
        body='This is a test from FCM HTTP v1 API',
        category='General',
        source='Python Script'
    )

    # Send Windows notification
    print("\n=== Sending Windows notification ===")
    fcm.send_windows_notification(
        app_name='Outlook',
        title='New Email',
        body='You have received a new email'
    )

    # Send to multiple topics using condition
    print("\n=== Sending to multiple topics with condition ===")
    fcm.send_to_condition(
        condition="'windows_notifications' in topics || 'all_notifications' in topics",
        title='Multi-topic Test',
        body='This goes to multiple topics',
        category='Info',
        source='Python Script'
    )
