import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

import logging

logger = logging.getLogger(__name__)


class Browser:
    """
    Browser class provides every kind of interaction for the browser agent.

    The purpose of browser is to navigate web pages, interact with elements,
    extract information, and support the agent's decision making.

    Tools available:
    - navigate(url): Go to a URL
    - click(selector): Click an element by CSS selector
    - type(selector, text): Type text into an element
    - scroll(direction, amount): Scroll up/down by pixels
    - extract_text(): Get visible text from current page
    - extract_html(): Get full HTML of current page
    - get_current_url(): Get current page URL
    - get_page_title(): Get current page title
    - screenshot(path): Take a screenshot of current page
    - press_key(key): Press a keyboard key
    - wait(seconds): Wait for a given duration
    - find_element(selector): Find a single element by CSS selector
    - find_elements(selector): Find all elements by CSS selector
    - get_element_text(selector): Get text content of an element
    - get_element_attribute(selector, attribute): Get attribute of an element
    - highlight(selector): Highlight an element for visibility
    - execute_script(script): Execute JavaScript on the page
    - switch_tab(index): Switch to a specific tab
    - new_tab(url): Open a new tab with optional URL
    - go_back(): Navigate back
    - go_forward(): Navigate forward
    - close(): Close the browser
    - get_state(): Get comprehensive page state
    - get_links(): Get all links on the page
    """

    GOOGLE_URL = "https://google.com/"

    def __init__(self, headless=True, window_size=(1920, 1080)):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self._default_wait = 10

    def navigate(self, url: str) -> dict:
        """Navigate to a URL and wait for page to load."""
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            return {"success": True, "url": self.get_current_url(), "title": self.get_page_title()}
        except WebDriverException as e:
            logger.error(f"Navigation error: {e}")
            return {"success": False, "error": str(e)}

    def click(self, selector: str, timeout: int = 10) -> dict:
        """Click an element identified by CSS selector."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            self._wait_for_page_load(1)
            return {"success": True, "selector": selector}
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Click error on '{selector}': {e}")
            return {"success": False, "error": str(e)}

    def type(self, selector: str, text: str, timeout: int = 10, clear_first: bool = True) -> dict:
        """Type text into an input element identified by CSS selector."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            if clear_first:
                element.clear()
            element.send_keys(text)
            return {"success": True, "selector": selector, "text": text}
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Type error on '{selector}': {e}")
            return {"success": False, "error": str(e)}

    def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """Scroll the page up or down by a given number of pixels."""
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            else:
                return {"success": False, "error": f"Invalid direction: {direction}. Use 'up' or 'down'."}
            time.sleep(0.3)
            return {"success": True, "direction": direction, "amount": amount}
        except WebDriverException as e:
            return {"success": False, "error": str(e)}

    def extract_text(self) -> str:
        """Extract visible text from the current page."""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            return body.text
        except Exception as e:
            logger.error(f"Extract text error: {e}")
            return ""

    def extract_html(self) -> str:
        """Extract full HTML of the current page."""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Extract HTML error: {e}")
            return ""

    def get_current_url(self) -> str:
        """Get the current page URL."""
        try:
            return self.driver.current_url
        except Exception:
            return ""

    def get_page_title(self) -> str:
        """Get the current page title."""
        try:
            return self.driver.title
        except Exception:
            return ""

    def screenshot(self, path: str = "./tmp/screenshot/screenshot.png") -> dict:
        """Take a screenshot of the current page."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.driver.save_screenshot(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def press_key(self, key: str) -> dict:
        """Press a keyboard key. Common keys: ENTER, ESC, TAB, BACK_SPACE, etc."""
        key_map = {
            "enter": Keys.RETURN,
            "escape": Keys.ESCAPE,
            "esc": Keys.ESCAPE,
            "tab": Keys.TAB,
            "backspace": Keys.BACK_SPACE,
            "delete": Keys.DELETE,
            "space": Keys.SPACE,
            "page_up": Keys.PAGE_UP,
            "page_down": Keys.PAGE_DOWN,
            "end": Keys.END,
            "home": Keys.HOME,
            "arrow_left": Keys.ARROW_LEFT,
            "arrow_up": Keys.ARROW_UP,
            "arrow_right": Keys.ARROW_RIGHT,
            "arrow_down": Keys.ARROW_DOWN,
        }
        key = key.lower()
        if key in key_map:
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(key_map[key])
                actions.perform()
                return {"success": True, "key": key}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Unknown key: {key}"}

    def wait(self, seconds: float = 1.0) -> dict:
        """Wait for a given duration in seconds."""
        time.sleep(seconds)
        return {"success": True, "waited": seconds}

    def find_element(self, selector: str, timeout: int = 10) -> dict:
        """Find a single element by CSS selector and return its properties."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return {
                "success": True,
                "selector": selector,
                "tag": element.tag_name,
                "text": element.text[:500] if element.text else "",
                "visible": element.is_displayed(),
            }
        except (TimeoutException, NoSuchElementException) as e:
            return {"success": False, "error": str(e)}

    def find_elements(self, selector: str, timeout: int = 10) -> dict:
        """Find all elements by CSS selector and return their properties."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return {
                "success": True,
                "selector": selector,
                "count": len(elements),
                "elements": [
                    {
                        "tag": el.tag_name,
                        "text": el.text[:200] if el.text else "",
                        "visible": el.is_displayed(),
                    }
                    for el in elements[:50]
                ],
            }
        except (TimeoutException, NoSuchElementException) as e:
            return {"success": False, "error": str(e)}

    def get_element_text(self, selector: str, timeout: int = 10) -> dict:
        """Get the text content of an element."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return {"success": True, "text": element.text}
        except (TimeoutException, NoSuchElementException) as e:
            return {"success": False, "error": str(e)}

    def get_element_attribute(self, selector: str, attribute: str, timeout: int = 10) -> dict:
        """Get a specific attribute of an element."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            value = element.get_attribute(attribute)
            return {"success": True, "attribute": attribute, "value": value}
        except (TimeoutException, NoSuchElementException) as e:
            return {"success": False, "error": str(e)}

    def highlight(self, selector: str, timeout: int = 5) -> dict:
        """Highlight an element on the page with a red border for visibility."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            self.driver.execute_script(
                "arguments[0].style.border = '3px solid red'; arguments[0].style.backgroundColor = 'yellow';",
                element,
            )
            return {"success": True, "selector": selector}
        except (TimeoutException, NoSuchElementException) as e:
            return {"success": False, "error": str(e)}

    def execute_script(self, script: str) -> dict:
        """Execute JavaScript on the page and return the result."""
        try:
            result = self.driver.execute_script(script)
            return {"success": True, "result": str(result)[:1000]}
        except WebDriverException as e:
            return {"success": False, "error": str(e)}

    def switch_tab(self, index: int) -> dict:
        """Switch to a specific tab by index (0-based)."""
        try:
            handles = self.driver.window_handles
            if 0 <= index < len(handles):
                self.driver.switch_to.window(handles[index])
                return {"success": True, "index": index, "title": self.get_page_title(), "url": self.get_current_url()}
            else:
                return {"success": False, "error": f"Tab index {index} out of range. Total tabs: {len(handles)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def new_tab(self, url: str = "https://google.com") -> dict:
        """Open a new tab with an optional URL."""
        try:
            self.driver.switch_to.new_window("tab")
            self.driver.get(url)
            return {"success": True, "url": url, "title": self.get_page_title()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def go_back(self) -> dict:
        """Navigate back in history."""
        try:
            self.driver.back()
            self._wait_for_page_load()
            return {"success": True, "url": self.get_current_url()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def go_forward(self) -> dict:
        """Navigate forward in history."""
        try:
            self.driver.forward()
            self._wait_for_page_load()
            return {"success": True, "url": self.get_current_url()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_state(self) -> dict:
        """Get comprehensive state of the current page."""
        try:
            return {
                "url": self.get_current_url(),
                "title": self.get_page_title(),
                "text_length": len(self.extract_text()),
                "tab_count": len(self.driver.window_handles),
                "current_tab": self.driver.window_handles.index(self.driver.current_window_handle),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_links(self) -> list[dict]:
        """Get all links on the current page."""
        try:
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)
                if text and href and not href.startswith("#"):
                    links.append({"text": text[:100], "href": href[:500]})
            return links[:100]
        except Exception as e:
            logger.error(f"Get links error: {e}")
            return []

    def close(self):
        """Close the browser and clean up."""
        try:
            self.driver.quit()
        except Exception:
            pass

    def _wait_for_page_load(self, timeout: int = 10):
        """Wait for the page to finish loading."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("Page load timeout")

    def GoogleSearch(self, query: str):
        """Legacy: Search Google for the given query."""
        self.driver.get(Browser.GOOGLE_URL)
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_bar.send_keys(query)
            search_bar.send_keys(Keys.RETURN)
            self._wait_for_page_load()
        except TimeoutException:
            logger.error("Google search timed out")
