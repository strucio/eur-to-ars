import os
import logging
import sys
from modules.web_scraper import WebScraper
from modules.discord_notifier import DiscordNotifier
from dotenv import load_dotenv

class ExchangeRateMonitor:
    """Monitors EUR/ARS exchange rate and sends Discord alerts when threshold is crossed"""
    
    def __init__(self):
        """Initialize the monitor with configuration from environment variables"""
        load_dotenv()
        
        # Load configuration
        self.url = os.getenv('WESTERN_UNION_URL')
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.threshold = float(os.getenv('RATE_THRESHOLD', '1700.0'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.delay = float(os.getenv('DELAY_BETWEEN_REQUESTS', '1.0'))
        
        # Validate and initialize
        self._validate_config()
        self._setup_logging()
        
        self.scraper = WebScraper(max_retries=self.max_retries, delay_between_requests=self.delay)
        self.discord_notifier = DiscordNotifier(self.webhook_url)
    
    def _validate_config(self):
        """Validate that all required environment variables are set"""
        if not self.webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL environment variable not set")
        if not self.url:
            raise ValueError("WESTERN_UNION_URL environment variable not set")
    
    def _setup_logging(self):
        """Configure logging to console"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
    
    def run(self):
        """Run the monitor - check rate and send alert if above threshold"""
        try:
            logging.info(f"Checking EUR/ARS rate (threshold: {self.threshold})")
            
            # Scrape current rate
            current_rate = self.scraper.get_exchange_rate(self.url)
            
            if current_rate is None:
                logging.error("Failed to retrieve exchange rate")
                self.discord_notifier.send_error_notification("Failed to scrape exchange rate from Western Union")
                sys.exit(1)
            
            logging.info(f"Current rate: {current_rate:.2f} ARS/EUR")
            
            # Only send alert if rate is ABOVE threshold
            if current_rate >= self.threshold:
                logging.warning(f"Rate is ABOVE threshold - sending alert")
                self.discord_notifier.send_rate_alert(current_rate, self.threshold, True, self.url)
            else:
                logging.info(f"Rate is below threshold ({current_rate:.2f} < {self.threshold}) - no alert sent")
            
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.discord_notifier.send_error_notification(f"Unexpected error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    monitor = ExchangeRateMonitor()
    monitor.run()