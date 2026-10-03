"""
Selenium Runner - Chrome WebDriver-based Gmail account creation flow
Handles driver creation, account creation, and verification for Selenium engine.
"""
import os
import glob
import time
import random
import logging
import tempfile
import uuid
import string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

from config.settings import Config
from core.fingerprint import inject_selenium_poltergeist
from core.trust_builder import (
    warm_up_session, ghost_mode_prepare,
)
from core.account_manager import account_manager

logger = logging.getLogger('gmail_creator_selenium')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

SCREEN_SIZES = [
    (1366, 768), (1440, 900), (1536, 864),
    (1600, 900), (1920, 1080), (1280, 720),
]


def _load_names():
    names_file = Config.NAMES_FILE if hasattr(Config, 'NAMES_FILE') else "data/names.txt"
    names = []
    try:
        with open(names_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    names.append(line)
    except FileNotFoundError:
        pass
    return names


_names_list = _load_names()


def generate_name():
    if _names_list:
        return random.choice(_names_list)
    return f"User{random.randint(1000, 9999)}"


def generate_password(length=14):
    """Generate a strong unique password per account."""
    upper = random.choices(string.ascii_uppercase, k=3)
    lower = random.choices(string.ascii_lowercase, k=5)
    digits = random.choices(string.digits, k=3)
    specials = random.choices("!@#$%&*", k=2)
    filler = random.choices(string.ascii_letters + string.digits, k=max(0, length - 13))
    pool = upper + lower + digits + specials + filler
    random.shuffle(pool)
    return "".join(pool)


def validate_birthday(birthday_str):
    try:
        month, day, year = birthday_str.split()
        month = str(int(month))
        if not (1 <= int(month) <= 12):
            month = "1"
        if not (1 <= int(day) <= 31):
            day = "1"
        if not (1900 <= int(year) <= 2010):
            year = "1990"
        return month, day, year
    except Exception:
        return "1", "1", "1990"


def _parse_proxy(proxy_string):
    """Parse proxy string into components: host:port or user:pass@host:port."""
    try:
        proxy_string = proxy_string.strip()
        if not proxy_string:
            return None

        if "@" in proxy_string:
            auth, hostport = proxy_string.rsplit("@", 1)
            user, passwd = auth.split(":", 1)
            host, port = hostport.rsplit(":", 1)
            return {"host": host, "port": port, "user": user, "pass": passwd}
        else:
            parts = proxy_string.rsplit(":", 1)
            if len(parts) == 2:
                return {"host": parts[0], "port": parts[1], "user": None, "pass": None}
    except Exception:
        pass
    return None


def create_driver(proxy=None):
    """Create and configure Chrome driver with unique fingerprint per session."""
    # Selenium reaches ChromeDriver over loopback (127.0.0.1). When HTTP_PROXY /
    # HTTPS_PROXY are set, urllib3 sends even that localhost traffic to the proxy,
    # which cannot reach the local driver and answers 502 -> driver creation dies with
    # "Message: Bad Gateway" no matter what proxy Chrome itself uses. Keep loopback
    # direct; this does not affect Chrome's own --proxy-server or outbound API calls.
    _loopback = "localhost,127.0.0.1,::1"
    for _var in ("NO_PROXY", "no_proxy"):
        _parts = [p.strip() for p in os.environ.get(_var, "").split(",") if p.strip()]
        for _host in _loopback.split(","):
            if _host not in _parts:
                _parts.append(_host)
        os.environ[_var] = ",".join(_parts)

    try:
        chrome_options = ChromeOptions()

        profile_id = str(uuid.uuid4())[:8]
        profile_dir = os.path.join(tempfile.gettempdir(), f"chrome_profile_{profile_id}")
        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')

        width, height = random.choice(SCREEN_SIZES)
        chrome_options.add_argument(f'--window-size={width},{height}')
        chrome_options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')

        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("--disable-webrtc")
        chrome_options.add_argument("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--no-experiments')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')

        if Config.HEADLESS_MODE:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--window-size=1920,1080')

        # Priority 1: Local proxy (for accessing Google in restricted regions)
        if Config.LOCAL_PROXY:
            proxy_url = Config.LOCAL_PROXY
            if not proxy_url.startswith(('socks5://', 'socks5h://', 'http://', 'https://')):
                proxy_url = f"socks5://{proxy_url}"
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
            logger.info(f"Using local proxy: {proxy_url}")
        # Priority 2: External proxy pool (for IP rotation)
        elif proxy:
            parsed = _parse_proxy(proxy)
            if parsed and not parsed["user"]:
                chrome_options.add_argument(f'--proxy-server={parsed["host"]}:{parsed["port"]}')
                logger.info(f"Using proxy: {parsed['host']}:{parsed['port']}")

        service = _get_chrome_service()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver = webdriver.Chrome(service=service, options=chrome_options)

                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'hardwareConcurrency', {
                            get: () => [2, 4, 6, 8][Math.floor(Math.random() * 4)]
                        });
                        Object.defineProperty(navigator, 'deviceMemory', {
                            get: () => [4, 8, 16][Math.floor(Math.random() * 3)]
                        });
                        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                        HTMLCanvasElement.prototype.toDataURL = function(type) {
                            if (this.width > 0 && this.height > 0) {
                                const ctx = this.getContext('2d');
                                ctx.fillStyle = 'rgba(' + Math.random()*255 + ',' + Math.random()*255 + ',' + Math.random()*255 + ',0.01)';
                                ctx.fillRect(0, 0, 1, 1);
                            }
                            return originalToDataURL.apply(this, arguments);
                        };
                    '''
                })

                driver.set_page_load_timeout(30)
                driver.get("https://www.google.com")
                time.sleep(2)
                logger.info("Selenium browser created successfully")
                return driver
            except Exception as e:
                logger.warning(f"Browser creation attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                try:
                    if 'driver' in locals():
                        driver.quit()
                except Exception:
                    pass
                time.sleep(2)

    except Exception as e:
        logger.error(f"Failed to create Selenium driver: {e}")
        return None


def _get_chrome_service():
    """Try multiple methods to get a ChromeDriver service."""
    if ChromeDriverManager:
        try:
            path = ChromeDriverManager().install()
            if path and os.path.exists(path) and os.path.isfile(path):
                return ChromeService(path)
        except Exception:
            pass

    common_paths = [
        os.path.join(os.getcwd(), "chromedriver.exe"),
        "C:\\chromedriver\\chromedriver.exe",
    ]
    wdm_glob = os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver", "*", "chromedriver.exe")
    matches = glob.glob(wdm_glob)
    if matches:
        common_paths.insert(0, matches[0])

    for path in common_paths:
        if os.path.exists(path) and os.path.isfile(path):
            return ChromeService(path)

    return ChromeService()


def _click_next(driver):
    """Find and click the Next button using multiple strategies."""
    selectors = [
        "//button[contains(text(), 'Next')]",
        "//button[contains(@class, 'VfPpkd-LgbsSe')]",
        "//button[@type='submit']",
        "//button[contains(@aria-label, 'Next')]",
        "//span[contains(text(), 'Next')]/parent::button",
    ]
    for sel in selectors:
        try:
            elements = driver.find_elements(By.XPATH, sel)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(0.5)
                    try:
                        el.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", el)
                    return True
        except Exception:
            continue
    return False


def _human_typing(element, text, delay_range=(0.08, 0.18)):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))


def _fill_field(driver, element, value):
    """Fill a field using multiple methods."""
    try:
        element.clear()
        time.sleep(0.3)
        element.send_keys(value)
        return True
    except Exception:
        pass
    try:
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            element, value
        )
        return True
    except Exception:
        pass
    try:
        ActionChains(driver).move_to_element(element).click().send_keys(value).perform()
        return True
    except Exception:
        return False


def create_account_selenium(driver, wait, username, password, birthday_str, gender,
                            mode="standard", progress=None, task_id=None):
    """
    Create a Gmail account using Selenium WebDriver.

    Returns: (success: bool, error_type: str or None)
    """
    try:
        if mode == "youtube":
            driver.get("https://accounts.google.com/signup/v2/webcreateaccount?"
                        "continue=https://www.youtube.com/&flowName=GlifWebSignIn&flowEntry=SignUp")
        elif mode == "workspace":
            driver.get("https://accounts.google.com/signup/v2/webcreateaccount?"
                        "continue=https://workspace.google.com/&flowName=GlifWebSignIn&flowEntry=SignUp")
        else:
            driver.get("https://accounts.google.com/signup/v2/createaccount?"
                        "flowName=GlifWebSignIn&flowEntry=SignUp")

        wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
        time.sleep(random.uniform(1, 3))

        full_name = generate_name()
        parts = full_name.split()
        first_name = parts[0] if parts else "User"
        last_name = parts[-1] if len(parts) > 1 else "User"

        first_el = driver.find_element(By.NAME, "firstName")
        _fill_field(driver, first_el, first_name)

        last_el = driver.find_element(By.NAME, "lastName")
        _fill_field(driver, last_el, last_name)

        time.sleep(1.5)
        _click_next(driver)
        time.sleep(3)

        month, day, year = validate_birthday(birthday_str)
        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]

        driver.execute_script("""
            var sel = document.getElementById('month');
            if (sel) { sel.value = arguments[0]; sel.dispatchEvent(new Event('change', {bubbles:true})); }
        """, month)
        time.sleep(0.5)

        driver.execute_script("""
            var d = document.querySelector('input[name="day"]');
            if (d) { d.value = arguments[0]; d.dispatchEvent(new Event('input', {bubbles:true})); }
            var y = document.querySelector('input[name="year"]');
            if (y) { y.value = arguments[1]; y.dispatchEvent(new Event('input', {bubbles:true})); }
        """, day, year)

        driver.execute_script("""
            var sel = document.getElementById('gender');
            if (sel) { sel.value = arguments[0]; sel.dispatchEvent(new Event('change', {bubbles:true})); }
        """, gender)
        time.sleep(1)

        _click_next(driver)
        time.sleep(3)

        # Find and click "Create your own Gmail address"
        _select_create_own(driver)
        time.sleep(2)

        # Fill username
        username_field = _find_username_field(driver, wait)
        if username_field:
            _fill_field(driver, username_field, username)
            time.sleep(1)
            _click_next(driver)
            time.sleep(2)
        else:
            logger.error("Username field not found")
            return False, "USERNAME_FIELD_NOT_FOUND"

        # Fill password
        try:
            pw_field = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
            confirm_field = wait.until(EC.presence_of_element_located((By.NAME, "PasswdAgain")))
            wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))

            pw_field.clear()
            confirm_field.clear()
            time.sleep(0.5)
            _human_typing(pw_field, password, (0.05, 0.12))
            time.sleep(0.5)
            _human_typing(confirm_field, password, (0.05, 0.12))
            time.sleep(1)

            _click_next(driver)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Password entry failed: {e}")
            return False, "PASSWORD_ENTRY_FAILED"

        # Check what page we're on now
        page_source = driver.page_source.lower()

        if "phone" in page_source and ("verify" in page_source or "number" in page_source):
            logger.warning("Phone verification detected")
            return False, "PHONE_REQUIRED"

        if "qr" in page_source or "scan" in page_source:
            logger.warning("QR code verification detected")
            return False, "QR_BLOCKED"

        email = f"{username}@gmail.com"
        account_manager.save(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            strategy=f"selenium_{mode}",
        )
        logger.info(f"Account created: {email}")
        return True, None

    except Exception as e:
        logger.error(f"Selenium account creation error: {e}")
        return False, "UNKNOWN_ERROR"


def _select_create_own(driver):
    """Try to click 'Create your own Gmail address' option."""
    selectors = [
        "//div[contains(text(), 'Create your own Gmail address')]",
        "//span[contains(text(), 'Create your own Gmail address')]",
        "//span[contains(text(), 'Create your own')]",
        "//div[contains(text(), 'Create your own')]",
    ]
    for sel in selectors:
        try:
            elements = driver.find_elements(By.XPATH, sel)
            for el in elements:
                if el.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(0.5)
                    el.click()
                    return True
        except Exception:
            continue
    return False


def _find_username_field(driver, wait):
    """Find the username input field using multiple strategies."""
    selectors = [
        "//input[@type='text' and contains(@name, 'user')]",
        "//input[@type='text' and contains(@id, 'user')]",
        "//input[@type='text' and contains(@aria-label, 'email')]",
        "//input[@type='text' and contains(@aria-label, 'Email')]",
        "//input[@name='Username']",
        "//input[@jsname='YPqjbf']",
        "//input[contains(@class, 'whsOnd')]",
    ]
    for sel in selectors:
        try:
            elements = driver.find_elements(By.XPATH, sel)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    return el
        except Exception:
            continue

    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
    except Exception:
        return None


def run_selenium_flow(i, num_accounts, username, password, warmup_minutes=5,
                      stealth_mode=True, mode="standard", proxy=None):
    """
    Complete Selenium-based account creation flow.

    Returns: bool (success)
    """
    driver = create_driver(proxy=proxy)
    if not driver:
        return False

    try:
        wait = WebDriverWait(driver, Config.BROWSER_TIMEOUT)

        # Inject trust cookies via Cookie Reaper
        if Config.ENABLE_COOKIE_REAPER:
            try:
                from core.cookie_reaper import inject_cookies_selenium
                inject_cookies_selenium(driver)
            except Exception:
                pass

        if stealth_mode:
            ghost_mode_prepare(driver, warmup_minutes)
        else:
            if Config.ENABLE_FINGERPRINT_MASKING:
                inject_selenium_poltergeist(driver)
            if Config.ENABLE_SESSION_WARMING:
                warm_up_session(driver)

        birthday = Config.YOUR_BIRTHDAY
        gender = str(Config.YOUR_GENDER)

        success, error_type = create_account_selenium(
            driver, wait, username, password,
            birthday, gender, mode=mode,
        )

        # Post-creation account warming
        if success and Config.ENABLE_SESSION_WARMING:
            try:
                from core.account_warmer import warm_account_selenium
                warm_account_selenium(f"{username}@gmail.com", password, duration_minutes=2)
            except Exception:
                pass

        # Telegram notification
        if success:
            try:
                from core.telegram_notifier import notifier
                notifier.notify_account_created(
                    email=f"{username}@gmail.com", password=password,
                    strategy=mode, proxy=proxy or "",
                )
            except Exception:
                pass

        return success

    except Exception as e:
        logger.error(f"Selenium flow error: {e}")
        return False
    finally:
        try:
            driver.quit()
        except Exception:
            pass
