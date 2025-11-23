# Test notification script - creates a persistent Windows notification
# Run this with: powershell -ExecutionPolicy Bypass -File test_notification.ps1

[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$app_id = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'

$xml = @"
<toast scenario="reminder">
    <visual>
        <binding template="ToastGeneric">
            <text>Test Notification</text>
            <text>This is a test message from PowerShell - $(Get-Date -Format 'HH:mm:ss')</text>
        </binding>
    </visual>
    <actions>
        <action content="Dismiss" arguments="dismiss"/>
    </actions>
</toast>
"@

$XmlDocument = [Windows.Data.Xml.Dom.XmlDocument]::new()
$XmlDocument.LoadXml($xml)

$toast = [Windows.UI.Notifications.ToastNotification]::new($XmlDocument)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app_id).Show($toast)

Write-Host "Notification sent!"
