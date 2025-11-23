# Windows Notification Forwarder

Forward all Windows 10/11 notifications to multiple notification channels. Get notified about what's happening on your Windows PC and remotely manage it from anywhere.

Supports **Firebase Cloud Messaging (FCM)**, **Pushbullet**, and **Ntfy** - use one or all simultaneously!

## Features

- ✅ Captures all Windows toast notifications from any app
- ✅ **Multi-provider support** - Forward to FCM, Pushbullet, and/or Ntfy simultaneously
- ✅ **Firebase Cloud Messaging (FCM)** - Modern HTTP v1 API with OAuth2, topic-based messaging
- ✅ **Pushbullet** - Send to all your devices instantly
- ✅ **Ntfy** - Self-hosted or public ntfy.sh server support
- ✅ Configurable app filtering (whitelist/blacklist)
- ✅ Auto-detect and enable/disable providers based on credentials
- ✅ Detailed logging for monitoring
- ✅ Lightweight and runs in the background
- ✅ Integrates with NotifyHub Flutter app

## Prerequisites

- **Windows 10/11** (required for WinRT APIs)
- **Python 3.8+** installed
- **At least one notification provider:**
  - **Firebase project** (for FCM) - [Setup Guide](https://console.firebase.google.com/)
  - **Pushbullet account** (for Pushbullet) - [Get API Token](https://www.pushbullet.com/#settings/account)
  - **Ntfy server** (for Ntfy) - Use [ntfy.sh](https://ntfy.sh) or self-hosted
- **NotifyHub Flutter app** (optional, for FCM notifications on mobile)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Providers

```bash
copy .env.example .env
notepad .env
```

Edit the `.env` file and configure **at least one provider**:

#### Option A: Firebase Cloud Messaging (FCM)

1. Go to [Firebase Console](https://console.firebase.google.com/) and create/select your project
2. Navigate to **Project Settings** → **Service Accounts**
3. Click **"Generate new private key"** and save as `service-account.json`
4. Enable Cloud Messaging API at `https://console.developers.google.com/apis/api/fcm.googleapis.com`

```env
ENABLE_FCM=true
FCM_SERVICE_ACCOUNT_FILE=service-account.json
FCM_TOPIC=windows_notifications
```

#### Option B: Pushbullet

1. Get your API token from: https://www.pushbullet.com/#settings/account

```env
ENABLE_PUSHBULLET=true
PUSHBULLET_API_TOKEN=your_api_token_here
```

#### Option C: Ntfy

Use ntfy.sh public server or your own self-hosted instance:

```env
ENABLE_NTFY=true
NTFY_SERVER_URL=https://ntfy.sh
NTFY_TOPIC=windows_notifications

# Optional: Basic auth for self-hosted servers
NTFY_USERNAME=your_username
NTFY_PASSWORD=your_password
```

**Self-Hosted with Auth:** If your ntfy server requires authentication, set `NTFY_USERNAME` and `NTFY_PASSWORD`.

**Note:** You can enable multiple providers simultaneously! Notifications will be sent to all enabled providers.

#### App Filtering (Optional)

```env
# Ignore specific apps (comma-separated)
IGNORED_APPS=Spotify,Discord

# Only forward from specific apps (takes precedence)
WHITELIST_APPS=Outlook,Teams,Slack
```

### 3. Grant Notification Access

**Important:** Python needs permission to access Windows notifications.

1. Run the diagnostic script first:
   ```bash
   python tools/diagnose.py
   ```

2. If access is **DENIED** or **UNSPECIFIED**:
   - Open **Settings** → **Privacy & Security** → **Notifications**
   - Scroll down and find **"Python"** or **"python.exe"**
   - Toggle notification access **ON**
   - Run `python tools/diagnose.py` again to verify

### 4. Run the Application

```bash
python main.py
```

Or use the startup script:

```bash
start.bat
```

The application will:
- Initialize all enabled providers (FCM, Pushbullet, Ntfy)
- Display a summary of active notification channels
- Start listening for Windows notifications
- Forward them to all enabled providers in real-time

Press **Ctrl+C** to stop.

## Configuration

Edit the `.env` file to customize behavior:

```env
# ==============================================================================
# NOTIFICATION PROVIDERS (Configure at least one)
# ==============================================================================

# Firebase Cloud Messaging
ENABLE_FCM=true
FCM_SERVICE_ACCOUNT_FILE=service-account.json
FCM_TOPIC=windows_notifications

# Pushbullet
ENABLE_PUSHBULLET=true
PUSHBULLET_API_TOKEN=your_api_token

# Ntfy
ENABLE_NTFY=true
NTFY_SERVER_URL=https://ntfy.sh
NTFY_TOPIC=windows_notifications
NTFY_USERNAME=              # Optional: for self-hosted servers with auth
NTFY_PASSWORD=              # Optional: for self-hosted servers with auth

# ==============================================================================
# APP FILTERING (Optional)
# ==============================================================================

# Ignore specific apps (comma-separated)
# These apps will NOT be forwarded
IGNORED_APPS=Spotify,Discord,Steam

# Only forward from specific apps (comma-separated)
# If set, ONLY these apps will be forwarded (takes precedence over IGNORED_APPS)
WHITELIST_APPS=Outlook,Teams,Slack
```

**Provider Auto-Detection:**
- If `ENABLE_X` is not set or credentials are missing, that provider is auto-disabled
- At least one provider must be enabled for the app to run
- You can use all three providers simultaneously

## Running as Windows Service (Auto-Start on Boot)

To run automatically when Windows starts, use **NSSM** (Non-Sucking Service Manager):

### 1. Download NSSM

Download from: https://nssm.cc/download

### 2. Install as Service

Open **Command Prompt as Administrator** and run:

```bash
nssm install NotificationForwarder "C:\Path\To\Python\python.exe" "C:\Path\To\windows-notification-forwarder\main.py"
nssm set NotificationForwarder AppDirectory "C:\Path\To\windows-notification-forwarder"
nssm start NotificationForwarder
```

Replace the paths with your actual Python and project paths.

### 3. Manage the Service

```bash
# Check status
nssm status NotificationForwarder

# Stop service
nssm stop NotificationForwarder

# Restart service
nssm restart NotificationForwarder

# Remove service
nssm remove NotificationForwarder confirm
```

## Testing

### Run Diagnostics

Check if everything is working:

```bash
python tools/diagnose.py
```

This will verify:
- Python version and environment
- All dependencies installed
- Notification access granted
- Connection to notification listener

### Test Notification

Use the included PowerShell script to create a test notification:

```powershell
powershell -ExecutionPolicy Bypass -File tools/test_notification.ps1
```

**Important:** Make sure the notification appears in **Windows Action Center** (Win+N). Only notifications that persist in the Action Center can be captured and forwarded.

## Troubleshooting

### No notifications being forwarded

**Check Windows Settings:**
1. Settings → Privacy & Security → Notifications
2. Turn OFF **"Focus Assist"** / **"Do Not Disturb"**
3. Ensure **"Get notifications from apps and other senders"** is ON
4. Grant notification access to **Python** / **python.exe**

**Check Action Center:**
- Press **Win+N** to open Action Center
- Verify notifications appear there (not just toast popups)
- Only **persistent notifications** can be captured

**Check Logs:**
- Look at `notification_forwarder.log` for detailed errors

### "Access denied" or "Access unspecified"

Run diagnostics:
```bash
python tools/diagnose.py
```

Then manually grant permission:
1. Settings → Privacy & Security → Notifications
2. Find **Python** in the list
3. Toggle ON

### Module not found errors

Install missing dependencies:
```bash
pip install -r requirements.txt
```

### FCM API errors

- Verify `service-account.json` is in the correct location
- Check that the service account has FCM permissions
- Verify the FCM topic name matches your mobile app subscription
- Check internet connection
- Ensure Cloud Messaging API is enabled in Firebase Console

### Application exits immediately

- Make sure `.env` file exists with proper configuration
- Verify `service-account.json` exists and is valid JSON (if using FCM)
- Run `python tools/diagnose.py` to see the exact error
- Check `notification_forwarder.log`

## Project Structure

```
windows-notification-forwarder/
├── main.py                       # Main application entry point
├── config.py                     # Configuration management
├── notification_listener.py      # Windows notification listener (WinRT)
├── start.bat                     # Windows startup script
├── requirements.txt              # Python dependencies
├── .env.example                 # Configuration template
├── .env                         # Your configuration (not in git)
├── .gitignore                   # Git ignore rules
├── service-account.json         # Firebase service account (not in git)
├── README.md                    # This file
│
├── providers/                    # Notification provider implementations
│   ├── __init__.py              # Package exports
│   ├── base_provider.py         # Abstract base provider class
│   ├── fcm_provider.py          # Firebase Cloud Messaging provider
│   ├── pushbullet_provider.py   # Pushbullet provider
│   ├── ntfy_provider.py         # Ntfy provider
│   └── provider_manager.py      # Multi-provider orchestration
│
├── utils/                        # Utility modules
│   ├── __init__.py              # Package exports
│   └── fcm_v1_helper.py         # FCM v1 HTTP API implementation
│
└── tools/                        # Diagnostic and testing tools
    ├── diagnose.py              # System diagnostic tool
    └── test_notification.ps1    # Test notification generator
```

## How It Works

1. **Polling**: Checks Windows Action Center every 0.5 seconds for new notifications
2. **Deduplication**: Tracks seen notifications to avoid duplicates
3. **Filtering**: Applies whitelist/blacklist rules from `.env`
4. **Provider Initialization**: Auto-detects and initializes enabled providers
5. **Multi-Provider Forwarding**: Sends notifications to all active providers simultaneously
   - **FCM**: Uses OAuth2 with service account, sends to topic via HTTP v1 API
   - **Pushbullet**: Uses API token, sends to all linked devices
   - **Ntfy**: HTTP POST to ntfy.sh or self-hosted server
6. **Delivery**: Each provider delivers notifications to their respective platforms instantly

## Limitations

- Only captures **persistent notifications** (ones in Action Center)
- Requires **Windows 10/11** (WinRT APIs not available on older versions)
- Must be running to capture notifications (use Windows service for auto-start)
- Requires at least one provider configured (FCM, Pushbullet, or Ntfy)
- Does not capture notifications from apps that don't use Windows notification system

## Privacy & Security

- Provider credentials stored locally in `.env` file (never committed to git)
- Notifications only sent to configured providers (FCM, Pushbullet, Ntfy)
- Logs stored locally in `notification_forwarder.log`
- **Never commit service-account.json or .env to version control** (already in .gitignore)
- FCM uses OAuth2 with short-lived access tokens
- Pushbullet and Ntfy use HTTPS for secure transmission
- Source code is open and auditable

## Performance

- **CPU usage:** Minimal (~0.1% on modern CPUs)
- **Memory usage:** ~30-50 MB
- **Network usage:** ~1 KB per notification
- **Battery impact:** Negligible

## FAQ

**Q: Can I use multiple providers at the same time?**
A: Yes! You can enable FCM, Pushbullet, and Ntfy simultaneously. Notifications will be sent to all enabled providers.

**Q: Which provider should I use?**
A:
- **FCM**: Best for mobile apps, free unlimited notifications, requires Firebase setup
- **Pushbullet**: Easiest setup (just API token), works across all devices, has free tier limits
- **Ntfy**: Privacy-focused, self-hostable, completely free, simple HTTP API

**Q: Can I run this on multiple PCs?**
A: Yes! Use the same provider credentials and different topics (or same topic to receive all). Notifications will include the source app name.

**Q: Can I filter by notification content?**
A: Not currently, but you can filter by app name using `WHITELIST_APPS` or `IGNORED_APPS`.

**Q: Will it capture notifications when I'm away from PC?**
A: Yes, as long as the PC is powered on and the app is running.

**Q: Does it work with notifications from Chrome/Firefox?**
A: Yes, if the browser shows notifications through Windows (not just in-browser).

**Q: Can I customize the notification format?**
A: The format is `[AppName] Title` with the notification text as body. You can modify this in the provider files.

**Q: Do I need all three providers configured?**
A: No! Configure at least one provider. The app will auto-detect which providers are enabled based on credentials.

## License

MIT License - Free to use and modify

## Support

- Check `notification_forwarder.log` for errors
- Run `python tools/diagnose.py` for diagnostics

## Integration with NotifyHub

This project works perfectly with the [NotifyHub Flutter app](../notification_hub/README.md):

1. Set up NotifyHub on your Android/iOS device
2. Note the topic it subscribes to (default: `windows_notifications`)
3. Configure this forwarder to use the same topic
4. Receive all your Windows notifications on your phone!

## Credits

Built with:
- [Python WinRT](https://github.com/pywinrt/python-winsdk) for Windows notification access
- [Firebase Cloud Messaging v1 API](https://firebase.google.com/docs/cloud-messaging) for FCM notifications
- [Pushbullet API](https://docs.pushbullet.com/) for Pushbullet notifications
- [Ntfy](https://ntfy.sh/) for simple, privacy-focused notifications
- [Google Auth](https://github.com/googleapis/google-auth-library-python) for OAuth2 authentication
- [Requests](https://requests.readthedocs.io/) for HTTP API calls
- [python-dotenv](https://github.com/theskumar/python-dotenv) for configuration

---

**Made with ❤️ for remote PC management and multi-channel notifications**
