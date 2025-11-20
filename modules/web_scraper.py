import logging
import time
import re
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WebScraper:
    """
    Handles web scraping of EUR/ARS exchange rate from Western Union using Selenium
    """
    
    def __init__(self, max_retries: int = 3, delay_between_requests: float = 1.0):
        """
        Initialize the web scraper
        
        Args:
            max_retries: Maximum number of retry attempts
            delay_between_requests: Delay in seconds between retry attempts
        """
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.debug_html = os.getenv('DEBUG_HTML', 'false').lower() == 'true'
        self.page_load_timeout = 30
        self.element_wait_timeout = 20

    def _create_driver(self) -> webdriver.Chrome:
        """
        Create and configure Chrome WebDriver
        
        Returns:
            Configured Chrome WebDriver instance
        """
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.page_load_timeout)
        return driver

    def get_exchange_rate(self, url: str) -> Optional[float]:
        """
        Scrape EUR to ARS exchange rate from Western Union
        
        Args:
            url: Western Union currency converter URL
            
        Returns:
            Exchange rate as float, or None if scraping failed
        """
        for attempt in range(self.max_retries):
            driver = None
            try:
                logging.info(f"Scraping attempt {attempt + 1}/{self.max_retries}")
                driver = self._create_driver()
                driver.get(url)
                
                # Wait for the exchange rate element
                wait = WebDriverWait(driver, self.element_wait_timeout)
                rate_element = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fx-to"))
                )
                
                # Get text, wait a bit if empty (JavaScript still loading)
                rate_text = rate_element.text.strip()
                if not rate_text:
                    time.sleep(2)
                    rate_text = rate_element.text.strip()
                
                if self.debug_html:
                    self._save_debug_html(driver.page_source, attempt)
                
                if rate_text:
                    rate = self._extract_numeric_value(rate_text)
                    if rate:
                        logging.info(f"Successfully scraped rate: {rate:.2f} ARS/EUR")
                        return rate
                
                logging.warning(f"Could not extract rate on attempt {attempt + 1}")
                
            except TimeoutException:
                logging.error(f"Timeout waiting for exchange rate element")
            except Exception as e:
                logging.error(f"Error on attempt {attempt + 1}: {e}")
            finally:
                if driver:
                    driver.quit()
            
            if attempt < self.max_retries - 1:
                time.sleep(self.delay_between_requests)
        
        logging.error("Failed to scrape exchange rate after all attempts")
        return None

    def _save_debug_html(self, html_content: str, attempt: int):
        """Save HTML content for debugging"""
        try:
            output_dir = os.getenv('DEBUG_OUTPUT_DIR', '/app/debug_output')
            os.makedirs(output_dir, exist_ok=True)
            
            filename = os.path.join(output_dir, f"debug_attempt_{attempt + 1}.html")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"Saved debug HTML: {filename}")
        except Exception as e:
            logging.error(f"Failed to save debug HTML: {e}")

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """
        Extract numeric value from text (e.g., "1688.5590 ARS" -> 1688.56)
        
        Args:
            text: Text containing the numeric value
            
        Returns:
            Exchange rate as float, or None if extraction failed
        """
        try:
            # Remove non-numeric characters except . and ,
            cleaned = re.sub(r'[^\d.,]', '', text.strip())
            if not cleaned:
                return None
            
            # Handle decimal separators
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace(',', '')  # Comma is thousands separator
            elif ',' in cleaned:
                # European style: comma as decimal
                parts = cleaned.split(',')
                if len(parts[-1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            
            value = float(cleaned)
            
            # Sanity check: EUR/ARS should be between 100-10000
            if 100 < value < 10000:
                return value
            
            logging.warning(f"Value {value} outside expected range (100-10000)")
            return None
            
        except ValueError:
            logging.error(f"Could not convert to float: '{text}'")
            return None