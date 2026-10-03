"""
Config Validator - Validates all settings on startup and reports issues
"""
import os
import logging

logger = logging.getLogger('gmail_creator_validator')


def validate_config():
    """
    Validate all configuration settings on startup.
    Returns: (warnings: list[str], errors: list[str])
    """
    from config.settings import Config

    warnings = []
    errors = []

    # Password
    if not Config.YOUR_PASSWORD:
        pw_file = "config/password.txt"
        if os.path.exists(pw_file):
            with open(pw_file, "r", encoding="utf-8") as f:
                pw = f.read().strip()
            if not pw:
                errors.append("No password set: YOUR_PASSWORD is empty and config/password.txt is empty")
        else:
            errors.append("No password set: YOUR_PASSWORD not in .env and config/password.txt not found")

    # Birthday format
    try:
        parts = Config.YOUR_BIRTHDAY.split()
        if len(parts) != 3:
            raise ValueError
        m, d, y = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= m <= 12):
            warnings.append(f"Birthday month {m} is invalid (1-12)")
        if not (1 <= d <= 31):
            warnings.append(f"Birthday day {d} is invalid (1-31)")
        if not (1940 <= y <= 2006):
            warnings.append(f"Birthday year {y} may cause issues (recommended: 1940-2006)")
    except (ValueError, AttributeError):
        warnings.append(f"Birthday format invalid: '{Config.YOUR_BIRTHDAY}' (expected: 'M D YYYY')")

    # Gender
    if str(Config.YOUR_GENDER) not in ("1", "2", "3"):
        warnings.append(f"Gender '{Config.YOUR_GENDER}' may be invalid (1=Male, 2=Female, 3=Other)")

    # Engine mode
    engine = getattr(Config, 'ENGINE_MODE', 'playwright').lower()
    if engine not in ('playwright', 'selenium', 'appium'):
        errors.append(f"Invalid ENGINE_MODE: '{engine}' (must be playwright/selenium/appium)")

    if engine == 'playwright':
        try:
            import playwright
        except ImportError:
            warnings.append("ENGINE_MODE=playwright but playwright not installed. Run: pip install playwright && playwright install")

    if engine == 'selenium':
        try:
            import selenium
        except ImportError:
            errors.append("ENGINE_MODE=selenium but selenium not installed. Run: pip install selenium")

    if engine == 'appium':
        try:
            import appium
        except ImportError:
            errors.append("ENGINE_MODE=appium but appium not installed. Run: pip install Appium-Python-Client")

    # SMS services check
    sms_keys = [
        ("FIVESIM_API_KEY", Config.FIVESIM_API_KEY),
        ("SMS_ACTIVATE_API_KEY", Config.SMS_ACTIVATE_API_KEY),
        ("ONLINESIM_API_KEY", Config.ONLINESIM_API_KEY),
        ("GETSMS_API_KEY", Config.GETSMS_API_KEY),
        ("HEROSMS_API_KEY", Config.HEROSMS_API_KEY),
    ]
    active_sms = [name for name, val in sms_keys if val and "YOUR_" not in val]
    if not active_sms:
        warnings.append("No SMS API keys configured. Premium mode won't work without at least one.")

    # Captcha services
    captcha_keys = [
        ("TWOCAPTCHA_API_KEY", Config.TWOCAPTCHA_API_KEY),
        ("ANTICAPTCHA_API_KEY", Config.ANTICAPTCHA_API_KEY),
        ("CAPMONSTER_API_KEY", Config.CAPMONSTER_API_KEY),
    ]
    active_captcha = [name for name, val in captcha_keys if val and "YOUR_" not in val]

    # Proxy
    if Config.ENABLE_PROXY:
        proxy_file = Config.PROXY_FILE
        if not os.path.exists(proxy_file):
            warnings.append(f"ENABLE_PROXY=True but proxy file '{proxy_file}' not found")
        else:
            with open(proxy_file, "r") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            if not lines:
                warnings.append(f"Proxy file '{proxy_file}' is empty")

    # Names file
    names_file = getattr(Config, 'NAMES_FILE', 'data/names.txt')
    if not os.path.exists(names_file):
        warnings.append(f"Names file '{names_file}' not found — will use fallback names")
    else:
        with open(names_file, "r", encoding="utf-8") as f:
            names = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        if len(names) < 10:
            warnings.append(f"Names file has only {len(names)} names — add more for variety")

    # Data directory
    if not os.path.exists("data"):
        warnings.append("data/ directory missing — will be created automatically")

    # Telegram notification
    tg_token = getattr(Config, 'TELEGRAM_BOT_TOKEN', '')
    tg_chat = getattr(Config, 'TELEGRAM_CHAT_ID', '')
    if tg_token and not tg_chat:
        warnings.append("TELEGRAM_BOT_TOKEN set but TELEGRAM_CHAT_ID missing")
    if tg_chat and not tg_token:
        warnings.append("TELEGRAM_CHAT_ID set but TELEGRAM_BOT_TOKEN missing")

    return warnings, errors


def print_validation_report(console, theme):
    """Print a formatted validation report to console."""
    warnings, errors = validate_config()

    if not warnings and not errors:
        console.print(f"[{theme['success']}]> Config validation: All OK[/]")
        return True

    if errors:
        for err in errors:
            console.print(f"[{theme['error']}]> ERROR: {err}[/]")

    if warnings:
        for warn in warnings:
            console.print(f"[{theme['warning']}]> WARNING: {warn}[/]")

    return len(errors) == 0
