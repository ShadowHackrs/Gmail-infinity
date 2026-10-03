import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger('gmail_creator_config')


class Config:
    # ═══════════════════════════════════════════════════════════════
    #                  ACCOUNT CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    YOUR_BIRTHDAY = os.getenv("YOUR_BIRTHDAY", "2 4 1990")
    YOUR_GENDER = os.getenv("YOUR_GENDER", "1")           # 1=Male, 2=Female, 3=Other
    YOUR_PASSWORD = os.getenv("YOUR_PASSWORD", "")
    RECOVERY_EMAIL = os.getenv("RECOVERY_EMAIL", "")
    RECOVERY_PHONE = os.getenv("RECOVERY_PHONE", "")

    # ═══════════════════════════════════════════════════════════════
    #                  SMS SERVICES
    # ═══════════════════════════════════════════════════════════════
    # 5sim
    FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")
    FIVESIM_COUNTRY = os.getenv("FIVESIM_COUNTRY", "usa")
    FIVESIM_OPERATOR = os.getenv("FIVESIM_OPERATOR", "any")

    # SMS-Activate
    SMS_ACTIVATE_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY", "")
    SMS_ACTIVATE_COUNTRY = os.getenv("SMS_ACTIVATE_COUNTRY", "0")

    # OnlineSIM
    ONLINESIM_API_KEY = os.getenv("ONLINESIM_API_KEY", "")
    ONLINESIM_COUNTRY = os.getenv("ONLINESIM_COUNTRY", "7")

    # GetSMS
    GETSMS_API_KEY = os.getenv("GETSMS_API_KEY", "")
    GETSMS_COUNTRY = os.getenv("GETSMS_COUNTRY", "us")

    # HeroSMS
    HEROSMS_API_KEY = os.getenv("HEROSMS_API_KEY", "")
    HEROSMS_COUNTRY = os.getenv("HEROSMS_COUNTRY", "0")  # 0 = any country

    # ═══════════════════════════════════════════════════════════════
    #                  CAPTCHA SERVICES
    # ═══════════════════════════════════════════════════════════════
    TWOCAPTCHA_API_KEY = os.getenv("TWOCAPTCHA_API_KEY", "")
    ANTICAPTCHA_API_KEY = os.getenv("ANTICAPTCHA_API_KEY", "")
    CAPMONSTER_API_KEY = os.getenv("CAPMONSTER_API_KEY", "")

    # ═══════════════════════════════════════════════════════════════
    #                  ANTI-QR CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    ENABLE_REALISTIC_WARMUP = os.getenv("ENABLE_REALISTIC_WARMUP", "True").lower() == "true"
    WARMUP_MIN_DURATION = int(os.getenv("WARMUP_MIN_DURATION", "300"))
    FORCE_RECOVERY_EMAIL = os.getenv("FORCE_RECOVERY_EMAIL", "True").lower() == "true"
    QR_MAX_RETRIES = int(os.getenv("QR_MAX_RETRIES", "3"))

    # ═══════════════════════════════════════════════════════════════
    #                  IDENTITY ROTATION
    # ═══════════════════════════════════════════════════════════════
    ROTATE_USER_AGENT = os.getenv("ROTATE_USER_AGENT", "True").lower() == "true"
    ROTATE_SCREEN_SIZE = os.getenv("ROTATE_SCREEN_SIZE", "True").lower() == "true"
    ROTATE_TIMEZONE = os.getenv("ROTATE_TIMEZONE", "True").lower() == "true"

    # ═══════════════════════════════════════════════════════════════
    #                  PROXY CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    ENABLE_PROXY = os.getenv("ENABLE_PROXY", "False").lower() == "true"
    PROXY_FILE = os.getenv("PROXY_FILE", "config/proxies.txt")
    PROXY_TYPE = os.getenv("PROXY_TYPE", "residential")  # residential / mobile / datacenter
    ROTATE_PROXY_EVERY = int(os.getenv("ROTATE_PROXY_EVERY", "1"))
    PROXY_COUNTRY_ROTATION = os.getenv("PROXY_COUNTRY_ROTATION", "US,GB,CA,AU").split(",")

    # Local Proxy (for accessing Google in restricted regions)
    # Format: socks5://127.0.0.1:10808 or http://127.0.0.1:7890
    LOCAL_PROXY = os.getenv("LOCAL_PROXY", "")

    # Mobile Proxy
    MOBILE_PROXY_IP_CHANGE_URL = os.getenv("MOBILE_PROXY_IP_CHANGE_URL", "")
    PROXY_CHANGE_WAIT_TIME = int(os.getenv("PROXY_CHANGE_WAIT_TIME", "10"))

    # ═══════════════════════════════════════════════════════════════
    #                  BROWSER & ENGINE
    # ═══════════════════════════════════════════════════════════════
    ENGINE_MODE = os.getenv("ENGINE_MODE", "playwright")   # "appium", "playwright"
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))

    # ═══════════════════════════════════════════════════════════════
    #                  ANTI-DETECTION & BEHAVIOR
    # ═══════════════════════════════════════════════════════════════
    ENABLE_SESSION_WARMING = os.getenv("ENABLE_SESSION_WARMING", "True").lower() == "true"
    ENABLE_FINGERPRINT_MASKING = os.getenv("ENABLE_FINGERPRINT_MASKING", "True").lower() == "true"
    ENABLE_HUMAN_TYPING_ERRORS = os.getenv("ENABLE_HUMAN_TYPING_ERRORS", "True").lower() == "true"
    DELAY_BETWEEN_ACCOUNTS = int(os.getenv("DELAY_BETWEEN_ACCOUNTS", "30"))
    WARMING_INTENSITY = os.getenv("WARMING_INTENSITY", "high")   # low, medium, high

    # ═══════════════════════════════════════════════════════════════
    #                  MAC ADDRESS ROTATION
    # ═══════════════════════════════════════════════════════════════
    ENABLE_MAC_ROTATION = os.getenv("ENABLE_MAC_ROTATION", "True").lower() == "true"
    CHANGE_MAC_EVERY = int(os.getenv("CHANGE_MAC_EVERY", "2"))

    # ═══════════════════════════════════════════════════════════════
    #                  RECOVERY CHAIN
    # ═══════════════════════════════════════════════════════════════
    ENABLE_RECOVERY_CHAIN = os.getenv("ENABLE_RECOVERY_CHAIN", "True").lower() == "true"
    CHAIN_FILE = os.getenv("CHAIN_FILE", "data/chain.json")

    # ═══════════════════════════════════════════════════════════════
    #                  ADVANCED STEALTH MODULES
    # ═══════════════════════════════════════════════════════════════
    ENABLE_WORM_AI = os.getenv("ENABLE_WORM_AI", "True").lower() == "true"
    ENABLE_CDP_INJECTION = os.getenv("ENABLE_CDP_INJECTION", "True").lower() == "true"
    ENABLE_COOKIE_REAPER = os.getenv("ENABLE_COOKIE_REAPER", "True").lower() == "true"
    ENABLE_GHOST_TYPER = os.getenv("ENABLE_GHOST_TYPER", "True").lower() == "true"
    ENABLE_POLTERGEIST = os.getenv("ENABLE_POLTERGEIST", "True").lower() == "true"

    # ═══════════════════════════════════════════════════════════════
    #                  METHODS
    # ═══════════════════════════════════════════════════════════════
    ENABLE_YOUTUBE_MODE = os.getenv("ENABLE_YOUTUBE_MODE", "True").lower() == "true"
    ENABLE_EDU_SPOOF = os.getenv("ENABLE_EDU_SPOOF", "False").lower() == "true"

    # ═══════════════════════════════════════════════════════════════
    #                  NAMES & PATHS
    # ═══════════════════════════════════════════════════════════════
    USE_ARABIC_NAMES = os.getenv("USE_ARABIC_NAMES", "True").lower() == "true"
    NAMES_FILE = os.getenv("NAMES_FILE", "data/names.txt")
    USER_AGENTS_FILE = os.getenv("USER_AGENTS_FILE", "config/user_agents.txt")

    # ═══════════════════════════════════════════════════════════════
    #                  LOGGING & EXPORT
    # ═══════════════════════════════════════════════════════════════
    ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
    LOG_FILE = os.getenv("LOG_FILE", "data/gmail_creator.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ACCOUNTS_FILE = os.getenv("ACCOUNTS_FILE", "data/accounts.txt")
    EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "txt")

    # ═══════════════════════════════════════════════════════════════
    #                  TELEGRAM NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # ═══════════════════════════════════════════════════════════════
    #                  VOICE SERVER SECURITY
    # ═══════════════════════════════════════════════════════════════
    VOICE_SERVER_TOKEN = os.getenv("VOICE_SERVER_TOKEN", "")

    @classmethod
    def validate(cls):
        """Validate critical config on startup and warn about insecure defaults."""
        warnings = []

        if not cls.VOICE_SERVER_TOKEN:
            warnings.append(
                "⚠️  VOICE_SERVER_TOKEN is not set in .env — voice server is unprotected! "
                "Set a strong secret token."
            )

        if not cls.YOUR_PASSWORD:
            warnings.append("⚠️  YOUR_PASSWORD is empty in .env — accounts may use a default password!")

        sms_keys = [
            cls.FIVESIM_API_KEY, cls.SMS_ACTIVATE_API_KEY,
            cls.ONLINESIM_API_KEY, cls.GETSMS_API_KEY,
        ]
        if not any(sms_keys):
            warnings.append(
                "ℹ️  No SMS API key configured — Ghost Mode (free bypass) only. "
                "Add a key to .env for Premium Mode."
            )

        for w in warnings:
            logger.warning(w)

        return warnings
