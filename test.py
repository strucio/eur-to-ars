#!/usr/bin/env python
"""Test script to verify Exchange Rate Monitor components"""
import os
import sys
from dotenv import load_dotenv
from modules.web_scraper import WebScraper
from modules.discord_notifier import DiscordNotifier

class ExchangeRateMonitorTester:
    """Test class for Exchange Rate Monitor components"""
    
    def __init__(self):
        load_dotenv()
        
        self.url = os.getenv('WESTERN_UNION_URL')
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.threshold = float(os.getenv('RATE_THRESHOLD', '1700.0'))
        
        self.scraper = WebScraper()
        self.discord_notifier = DiscordNotifier(self.webhook_url) if self.webhook_url else None
        self.results = {}
    
    def test_configuration(self) -> bool:
        """Test that all required environment variables are set"""
        print("🧪 Testing configuration...")
        
        if not self.url:
            print("   ❌ WESTERN_UNION_URL not set")
            return False
        print(f"   ✅ WESTERN_UNION_URL: {self.url}")
        
        if not self.webhook_url:
            print("   ❌ DISCORD_WEBHOOK_URL not set")
            return False
        print(f"   ✅ DISCORD_WEBHOOK_URL: {self.webhook_url[:50]}...")
        print(f"   ✅ RATE_THRESHOLD: {self.threshold}")
        
        return True
    
    def test_web_scraper(self) -> bool:
        """Test the web scraper functionality"""
        print("\n🧪 Testing web scraper...")
        
        try:
            rate = self.scraper.get_exchange_rate(self.url)
            
            if rate is None:
                print("   ❌ Failed to scrape exchange rate")
                return False
            
            print(f"   ✅ Successfully scraped rate: {rate:.2f} ARS per EUR")
            
            direction = "ABOVE" if rate >= self.threshold else "BELOW"
            emoji = "📈" if rate >= self.threshold else "📉"
            print(f"   {emoji} Rate is {direction} threshold ({self.threshold})")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error during scraping: {e}")
            return False
    
    def test_discord_notifier(self) -> bool:
        """Test Discord notification functionality"""
        print("\n🧪 Testing Discord notifier...")
        
        if not self.discord_notifier:
            print("   ❌ Discord notifier not initialized")
            return False
        
        try:
            if self.discord_notifier.send_test_notification():
                print("   ✅ Test notification sent successfully")
                print("   💬 Check your Discord channel")
                return True
            else:
                print("   ❌ Failed to send test notification")
                return False
        except Exception as e:
            print(f"   ❌ Error sending notification: {e}")
            return False
    
    def test_all_notifications(self):
        """Send all notification types for visual inspection"""
        print("\n🧪 Testing all notification types...")
        print("   This will send 3 notifications to Discord\n")
        
        if not self.discord_notifier:
            print("   ❌ Discord notifier not initialized")
            return
        
        # Test notification
        print("   1️⃣ Sending test notification...")
        self.discord_notifier.send_test_notification()
        
        # Rate above threshold
        print("   2️⃣ Sending rate ABOVE threshold alert...")
        self.discord_notifier.send_rate_alert(1750.50, self.threshold, True, self.url)
        
        # Error notification
        print("   3️⃣ Sending error notification...")
        self.discord_notifier.send_error_notification("Test error - Western Union unavailable")
        
        print("\n   ✅ All notifications sent! Check your Discord channel.")
    
    def run_standard_tests(self):
        """Run standard validation tests"""
        print("=" * 60)
        print("🚀 Exchange Rate Monitor - Test Suite")
        print("=" * 60)
        
        self.results['config'] = self.test_configuration()
        
        if self.results['config']:
            self.results['scraper'] = self.test_web_scraper()
            self.results['notifier'] = self.test_discord_notifier()
        
        self._display_summary()
    
    def _display_summary(self):
        """Display test results summary"""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.capitalize()}: {status}")
        
        print("\n" + "=" * 60)
        if all(self.results.values()):
            print("🎉 All tests passed! Monitor is ready to use.")
        else:
            print("❌ Some tests failed. Check configuration and try again.")
        print("=" * 60)

def main():
    """Main entry point with command line argument support"""
    tester = ExchangeRateMonitorTester()
    
    # Check for --notifications flag
    if len(sys.argv) > 1 and sys.argv[1] == '--notifications':
        tester.test_all_notifications()
    else:
        tester.run_standard_tests()

if __name__ == "__main__":
    main()