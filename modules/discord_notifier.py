import requests
import logging
from datetime import datetime, timezone

class DiscordNotifier:
    """
    Handles sending notifications to Discord via webhook
    """
    
    def __init__(self, webhook_url: str):
        """
        Initialize the Discord notifier
        
        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url
    
    def send_rate_alert(self, current_rate: float, threshold: float, is_above_threshold: bool, url: str = None) -> bool:
        """
        Send exchange rate alert to Discord
        
        Args:
            current_rate: Current EUR/ARS exchange rate
            threshold: The threshold value
            is_above_threshold: True if rate is above threshold, False if below
            url: Optional URL to Western Union page
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        direction = "above" if is_above_threshold else "below"
        emoji = "📈" if is_above_threshold else "📉"
        color = 0x00FF00 if is_above_threshold else 0xFF6B6B  # Green for above, red for below
        
        message = (
            f"{emoji} **Exchange rate is {direction} threshold!**\n\n"
            f"**Current Rate:** {current_rate:.2f} ARS per EUR\n"
            f"**Threshold:** {threshold:.2f} ARS per EUR"
        )
        
        if url:
            message += f"\n\n[View on Western Union]({url})"
        
        title = f"EUR/ARS Rate Alert - {direction.capitalize()} Threshold"
        
        return self._send_notification(message, title, color)
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification to Discord
        
        Args:
            error_message: Error message to send
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        message = f"❌ **Error occurred:**\n\n{error_message}"
        title = "Exchange Rate Monitor Error"
        color = 0xFF0000  # Red
        
        return self._send_notification(message, title, color)
    
    def send_test_notification(self) -> bool:
        """
        Send a test notification to verify webhook is working
        
        Returns:
            True if notification sent successfully, False otherwise
        """
        message = "🧪 Test notification from Exchange Rate Monitor\n\nIf you see this, notifications are working! ✅"
        title = "Test Notification"
        color = 0x3498DB  # Blue
        
        return self._send_notification(message, title, color)
    
    def _send_notification(self, message: str, title: str, color: int) -> bool:
        """
        Internal method to send notification to Discord
        
        Args:
            message: Message content
            title: Embed title
            color: Embed color (hex)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": self._get_current_timestamp(),
            "footer": {
                "text": "Exchange Rate Monitor"
            }
        }
        
        payload = {
            "embeds": [embed],
            "username": "EUR/ARS Monitor"
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logging.info(f"Discord notification sent successfully: {title}")
            return True
        except requests.RequestException as e:
            logging.error(f"Failed to send Discord notification: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending notification: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp string
        """
        return datetime.now(timezone.utc).isoformat()