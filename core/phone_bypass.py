"""
Phone Bypass - Consolidated phone/QR verification bypass strategies for Playwright
Handles Ghost Mode (no phone) and Premium Mode (5sim/SMS-Activate auto-verification).
"""
import asyncio
import random
import logging
from config.settings import Config

logger = logging.getLogger('gmail_creator_phone_bypass')

PHONE_SIGNALS = [
    "phone number", "add phone number", "verify your phone",
    "enter a phone", "add a phone", "get a verification code",
    "رقم الهاتف", "أدخل رقم هاتف", "إضافة رقم هاتف",
    "verify it's you", "التحقق من هويتك",
    "to verify your identity", "للتحقق من هويتك",
    "get a verification code on your phone",
    "confirm you're not a robot", "تأكيد أنك لست برنامج روبوت",
    "send sms", "verify your phone number",
    "your phone will open an sms", "send a code",
]

QR_SIGNALS = [
    "qr code", "scan the qr", "verify some info",
    "المسح الضوئي لرمز qr", "verify some info before creating",
    "preventing abuse from computer programs",
    "use your android phone", "use an android phone",
]

SUCCESS_SIGNALS = [
    "welcome to google", "مرحبًا بك في google",
    "choose your settings", "review your account info",
    "agree", "i agree", "أوافق",
    "privacy and terms", "الخصوصية والبنود",
    "express personalization", "التخصيص السريع",
]

SKIP_SELECTORS = [
    "button:has-text('Skip')",
    "button:has-text('تخطي')",
    "button:has-text('Not now')",
    "button:has-text('ليس الآن')",
    "button:has-text('Later')",
    "span:has-text('Skip')",
    "span:has-text('تخطي')",
    "a:has-text('Skip')",
]

EMAIL_INSTEAD_SELECTORS = [
    "span:has-text('Use email instead')",
    "span:has-text('استخدام عنوان بريد إلكتروني')",
    "a:has-text('Use email instead')",
    "button:has-text('Use email instead')",
    "div:has-text('Use email instead')",
]

PHONE_INPUT_SELECTORS = [
    "input[type='tel']",
    "input[name='phoneNumber']",
    "input[id='phoneNumberId']",
    "input[autocomplete='tel']",
    "input[aria-label*='phone' i]",
    "input[aria-label*='هاتف']",
    "#phoneNumberId",
    "input[data-initial-dir='ltr'][type='tel']",
]

CODE_INPUT_SELECTORS = [
    "input[name='code']",
    "input[id='code']",
    "input[type='tel'][name='code']",
    "input[aria-label*='code' i]",
    "input[aria-label*='رمز']",
    "input[autocomplete='one-time-code']",
    "#code",
    "input[name='otp']",
    "input[data-initial-dir='ltr'][aria-label*='Enter']",
]

NEXT_BUTTON_SELECTORS = [
    "button:has-text('Next')", "button:has-text('التالي')",
    "button:has-text('Send')", "button:has-text('إرسال')",
    "button[type='submit']",
]

VERIFY_BUTTON_SELECTORS = [
    "button:has-text('Verify')", "button:has-text('تحقق')",
    "button:has-text('Next')", "button:has-text('التالي')",
    "button:has-text('Confirm')", "button:has-text('تأكيد')",
    "button[type='submit']",
]


def detect_page_type(page_content):
    content_lower = page_content.lower()
    if any(s in content_lower for s in QR_SIGNALS):
        return "qr_code"
    if any(s in content_lower for s in PHONE_SIGNALS):
        return "phone"
    if any(s in content_lower for s in SUCCESS_SIGNALS):
        return "success"
    return "unknown"


async def _try_click(page, selectors, is_mobile=False, timeout=5000):
    for sel in selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=timeout)
            if el and await el.is_visible():
                if is_mobile:
                    await el.tap()
                else:
                    await el.click()
                return True
        except Exception:
            continue
    return False


async def _find_input(page, selectors):
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                return el
        except Exception:
            continue
    return None


async def try_skip(page, is_mobile=False):
    return await _try_click(page, SKIP_SELECTORS, is_mobile=is_mobile)


async def try_email_instead(page, is_mobile=False):
    clicked = await _try_click(page, EMAIL_INSTEAD_SELECTORS, is_mobile=is_mobile)
    if clicked:
        await page.wait_for_timeout(1500)
    return clicked


async def _check_phone_still_required(page):
    try:
        content = await page.content()
        return any(s in content.lower() for s in PHONE_SIGNALS)
    except Exception:
        return True


async def handle_phone_page(page, is_mobile=False, sms_api_available=False):
    """
    Multi-strategy phone bypass for Playwright flow.
    Returns: (success: bool, method: str)
    """
    logger.info("Phone verification page detected — running bypass strategies...")

    # Detect if this is the "Send SMS" reverse verification (no input field, just a button)
    is_send_sms_page = False
    try:
        content = await page.content()
        content_lower = content.lower()
        if ("send sms" in content_lower or "your phone will open an sms" in content_lower
            or "send a code" in content_lower):
            is_send_sms_page = True
            logger.info("Detected 'Send SMS' reverse verification page — this requires device, will try to escape")
    except Exception:
        pass

    # PREMIUM MODE: If SMS API is available, use it immediately (don't waste time on skip attempts)
    if sms_api_available and not is_send_sms_page:
        logger.info("Premium Mode: Going directly to SMS API verification...")
        # Quick check for skip/email-instead first (free is always better)
        if await try_skip(page, is_mobile):
            await page.wait_for_timeout(1500)
            if not await _check_phone_still_required(page):
                return True, "skip"
        if await try_email_instead(page, is_mobile):
            if not await _check_phone_still_required(page):
                return True, "email_instead"
        # Go to SMS
        success, method = await _sms_api_verification(page, is_mobile)
        if success:
            return True, method
        return False, method

    # ── Send SMS / Device Phone Verification escape
    # This page requires SENDING from a physical device — impossible to automate.
    # Usually caused by IP reputation. Must escape to different signup flow or fail gracefully.
    is_device_phone = is_send_sms_page or "devicephonever" in page.url.lower()
    if is_device_phone:
        logger.info("Device phone verification / Send SMS page — trying to escape...")

        # Try Skip/Not now first (sometimes available)
        if await try_skip(page, is_mobile):
            await page.wait_for_timeout(1500)
            if not await _check_phone_still_required(page):
                return True, "skip"

        # Try "Use email instead" or alternative verification
        if await try_email_instead(page, is_mobile):
            if not await _check_phone_still_required(page):
                return True, "email_instead"

        # Clear ALL session data — the current session is IP-flagged
        try:
            context = page.context
            await context.clear_cookies()
            await page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
            await page.wait_for_timeout(1000)
        except Exception:
            pass

        # Extended warmup on Google services to build fresh trust signals
        try:
            await page.goto("https://www.google.com", timeout=12000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(2000, 4000))

            # Accept cookies if prompted
            for btn in ["button:has-text('Accept all')", "button:has-text('I agree')", "#L2AGLb"]:
                try:
                    el = await page.query_selector(btn)
                    if el and await el.is_visible():
                        await el.click()
                        break
                except Exception:
                    pass

            # Do a search to build activity
            try:
                search_box = await page.query_selector("textarea[name='q'], input[name='q']")
                if search_box:
                    query = random.choice(["best email provider", "how to create email",
                                           "gmail features 2025", "google account help"])
                    await search_box.click()
                    await page.wait_for_timeout(300)
                    for ch in query:
                        await page.keyboard.type(ch)
                        await page.wait_for_timeout(random.randint(40, 100))
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(random.randint(3000, 5000))
            except Exception:
                pass

            await page.goto("https://www.youtube.com", timeout=12000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(3000, 6000))

            await page.goto("https://maps.google.com", timeout=12000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(2000, 4000))

            await page.goto("https://play.google.com", timeout=12000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(2000, 4000))
        except Exception:
            pass

        # Try multiple different signup URLs with randomized parameters
        escape_urls = [
            "https://accounts.google.com/signup/v2/webcreateaccount?biz=false&cc=youtube&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en",
            "https://accounts.google.com/signup/v2/createaccount?biz=false&flowName=GlifWebSignIn&flowEntry=SignUp&hl=en",
            "https://accounts.google.com/lifecycle/steps/signup/name?continue=https%3A%2F%2Fmail.google.com&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en&service=mail&theme=glif",
            "https://accounts.google.com/SignUp?hl=en&continue=https%3A%2F%2Fwww.google.com",
            f"https://accounts.google.com/lifecycle/steps/signup/name?continue=https%3A%2F%2Fmyaccount.google.com&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en&theme=glif&dsh=S{random.randint(1000000000, 9999999999)}",
        ]

        random.shuffle(escape_urls)
        for url in escape_urls:
            try:
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                await page.wait_for_timeout(random.randint(2000, 4000))

                # Check if we got a clean signup page
                try:
                    el = await page.wait_for_selector('input[name="firstName"]', timeout=8000)
                except Exception:
                    el = None

                if el:
                    content = await page.content()
                    current_url = page.url.lower()
                    if (not any(s in content.lower() for s in PHONE_SIGNALS + QR_SIGNALS)
                        and "devicephonever" not in current_url
                        and "phonechallenge" not in current_url):
                        logger.info(f"Send SMS escaped to fresh signup page")
                        return True, "send_sms_escaped"
                    else:
                        logger.debug(f"URL {url[:60]} still shows verification")
            except Exception:
                continue

        # If we're here, this IP is flagged. Try signin→Create Account as last resort
        try:
            await page.goto("https://accounts.google.com/signin", timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            for sel in ["a:has-text('Create account')", "button:has-text('Create account')",
                        "span:has-text('Create account')", "a:has-text('إنشاء حساب')"]:
                try:
                    el = await page.query_selector(sel)
                    if el and await el.is_visible():
                        await el.click()
                        await page.wait_for_timeout(2000)
                        break
                except Exception:
                    continue
            for sel in ["li:has-text('For my personal use')", "span:has-text('For my personal use')",
                        "li:has-text('لاستخدامي الشخصي')"]:
                try:
                    el = await page.query_selector(sel)
                    if el and await el.is_visible():
                        await el.click()
                        await page.wait_for_timeout(3000)
                        break
                except Exception:
                    continue
            el = await page.wait_for_selector('input[name="firstName"]', timeout=8000)
            if el:
                content = await page.content()
                current_url = page.url.lower()
                if ("devicephonever" not in current_url
                    and not any(s in content.lower() for s in ["send sms", "verify your phone number"])):
                    return True, "send_sms_escaped"
        except Exception:
            pass

        logger.warning("Device phone verification escape failed — IP is heavily flagged. Use a proxy or VPN.")
        return False, "send_sms_blocked"

    # GHOST MODE: Try all free bypass strategies
    # Strategy 1: Skip button
    if await try_skip(page, is_mobile):
        await page.wait_for_timeout(2000)
        if not await _check_phone_still_required(page):
            logger.info("Phone bypassed via Skip button")
            return True, "skip"

    # Strategy 2: Use email instead
    if await try_email_instead(page, is_mobile):
        if not await _check_phone_still_required(page):
            logger.info("Phone bypassed via 'Use email instead'")
            return True, "email_instead"

    # Strategy 3: Try "Not now" or other skip variants
    alt_skip = [
        "button:has-text('Done')", "button:has-text('تم')",
        "button:has-text('Continue')", "button:has-text('متابعة')",
        "a:has-text('I\\'ll do it later')",
        "button:has-text('No thanks')", "button:has-text('لا، شكرًا')",
        "button:has-text('Confirm')", "button:has-text('تأكيد')",
    ]
    if await _try_click(page, alt_skip, is_mobile=is_mobile):
        await page.wait_for_timeout(2000)
        if not await _check_phone_still_required(page):
            logger.info("Phone bypassed via alternative skip")
            return True, "alt_skip"

    # Strategy 4: Recovery email (if available)
    recovery_selectors = [
        "span:has-text('Add recovery email')",
        "span:has-text('إضافة بريد إلكتروني للاسترداد')",
        "a:has-text('recovery email')",
        "div:has-text('Add recovery email address')",
        "button:has-text('Add email address')",
        "span:has-text('Add a recovery email')",
        "button:has-text('recovery email')",
    ]
    if await _try_click(page, recovery_selectors, is_mobile=is_mobile):
        await page.wait_for_timeout(1500)
        logger.info("Switched to recovery email option")
        recovery_email = getattr(Config, 'RECOVERY_EMAIL', '')
        if recovery_email:
            try:
                email_input = await _find_input(page, [
                    "input[type='email']", "input[name='recoveryEmail']",
                    "input[autocomplete='email']", "input[aria-label*='email' i]",
                    "input[aria-label*='recovery' i]",
                ])
                if email_input:
                    await email_input.fill(recovery_email)
                    await page.wait_for_timeout(500)
                    await _try_click(page, NEXT_BUTTON_SELECTORS, is_mobile=is_mobile)
                    await page.wait_for_timeout(2000)
                    if not await _check_phone_still_required(page):
                        return True, "recovery_email"
            except Exception as e:
                logger.warning(f"Recovery email fill failed: {e}")

    # Strategy 5: JS click on skip/not-now links hidden in the DOM
    try:
        result = await page.evaluate("""() => {
            const texts = ['skip', 'not now', 'later', 'done', 'تخطي', 'ليس الآن', 'لاحقاً'];
            const els = document.querySelectorAll('button, a, span[role="button"], div[role="button"]');
            for (const el of els) {
                const t = el.textContent.trim().toLowerCase();
                for (const skip of texts) {
                    if (t === skip || t.includes(skip)) {
                        el.click();
                        return 'clicked:' + t;
                    }
                }
            }
            return null;
        }""")
        if result:
            logger.info(f"Phone bypass: JS click on '{result}'")
            await page.wait_for_timeout(2500)
            if not await _check_phone_still_required(page):
                return True, "js_skip"
    except Exception:
        pass

    # Strategy 6: Navigate back and forward to trigger different verification flow
    try:
        logger.info("Phone bypass: Trying back-navigation trick...")
        await page.go_back()
        await page.wait_for_timeout(2000)
        await page.go_forward()
        await page.wait_for_timeout(2000)
        if not await _check_phone_still_required(page):
            return True, "back_nav"
    except Exception:
        pass

    # Strategy 7: URL-based bypass — navigate directly to next step
    try:
        current_url = page.url
        bypass_urls = [
            "https://accounts.google.com/signup/v2/createrecoveryphone?skip",
            "https://myaccount.google.com",
        ]
        for bypass_url in bypass_urls:
            try:
                await page.goto(bypass_url, timeout=10000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                content = await page.content()
                if any(s in content.lower() for s in SUCCESS_SIGNALS):
                    logger.info(f"Phone bypassed via URL redirect: {bypass_url}")
                    return True, "url_bypass"
            except Exception:
                continue
        # Navigate back if URL bypass failed
        try:
            await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
        except Exception:
            pass
    except Exception:
        pass

    # Strategy 8: Keyboard Tab navigation to skip phone section
    try:
        for _ in range(10):
            await page.keyboard.press("Tab")
            await page.wait_for_timeout(200)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)
        if not await _check_phone_still_required(page):
            logger.info("Phone bypassed via keyboard Tab navigation")
            return True, "keyboard_nav"
    except Exception:
        pass

    # Strategy 9: Clear session & restart from signin path (fresh trust)
    try:
        logger.info("Phone bypass: Clearing session and trying fresh signup path...")
        context = page.context
        await context.clear_cookies()
        await page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
        await page.wait_for_timeout(1000)

        # Quick warmup for fresh trust
        await page.goto("https://www.google.com", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))
        await page.goto("https://www.youtube.com", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))

        # Try signin→Create account path
        await page.goto("https://accounts.google.com/signin", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        for sel in ["a:has-text('Create account')", "button:has-text('Create account')",
                    "span:has-text('Create account')", "a:has-text('إنشاء حساب')"]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(2000)
                    break
            except Exception:
                continue
        for sel in ["li:has-text('For my personal use')", "span:has-text('For my personal use')",
                    "li:has-text('لاستخدامي الشخصي')"]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(2000)
                    break
            except Exception:
                continue

        # Check if we got past the phone screen
        content = await page.content()
        if 'firstName' in content or any(s in content.lower() for s in SUCCESS_SIGNALS):
            logger.info("Phone bypassed via session reset + fresh signup")
            return True, "session_reset"
    except Exception as e:
        logger.debug(f"Session reset bypass failed: {e}")

    # Strategy 10: SMS API verification (if configured and enabled)
    if sms_api_available:
        success, method = await _sms_api_verification(page, is_mobile)
        if success:
            return True, method
        return False, method

    logger.error("All phone bypass strategies exhausted")
    return False, "all_failed"


async def _sms_api_verification(page, is_mobile=False):
    """
    Full SMS API verification flow:
    1. Check balance
    2. Request phone number
    3. Enter phone on Google page
    4. Wait for SMS code
    5. Enter code
    6. Verify
    7. Cancel on failure / Finish on success
    """
    logger.info("Attempting SMS API verification...")
    order_id = None
    service_name = None

    try:
        from services.sms_manager import (
            get_phone_from_any_service, get_code_from_service,
            cancel_order, finish_order, check_balance, format_phone_for_google,
        )

        # Step 1: Check balance
        balances = await check_balance()
        has_funds = any(b is not None and b > 0 for b in balances.values())
        if balances and not has_funds:
            logger.error("SMS API: All services have zero balance")
            return False, "sms_no_balance"

        # Step 2: Request phone number
        phone_data = await get_phone_from_any_service()
        if not phone_data:
            logger.error("SMS API: Could not get phone number from any service")
            return False, "sms_no_number"

        phone_number = phone_data['phone']
        service_name = phone_data['service']
        order_id = phone_data['id']
        formatted_phone = format_phone_for_google(phone_number)
        logger.info(f"SMS API: Got {formatted_phone} from {service_name} (order: {order_id})")

        # Step 3: Find phone input and enter number
        phone_input = await _find_input(page, PHONE_INPUT_SELECTORS)
        if not phone_input:
            logger.error("SMS API: Could not find phone input field on page")
            await cancel_order(service_name, order_id)
            return False, "sms_no_phone_input"

        await phone_input.click()
        await page.wait_for_timeout(300)
        await phone_input.fill("")
        await page.wait_for_timeout(200)
        await phone_input.fill(formatted_phone)
        await page.wait_for_timeout(800)

        # Step 4: Click Next/Send to submit phone number
        old_url = page.url
        await _try_click(page, NEXT_BUTTON_SELECTORS, is_mobile=is_mobile)
        await page.wait_for_timeout(4000)

        # Check if phone was rejected (invalid number, too many attempts, etc)
        try:
            error_content = await page.content()
            error_lower = error_content.lower()
            phone_errors = [
                "this phone number cannot be used", "couldn't verify",
                "this number has been used too many times",
                "لا يمكن استخدام رقم الهاتف هذا",
                "too many attempts", "try again later",
            ]
            if any(err in error_lower for err in phone_errors):
                logger.warning(f"SMS API: Phone number rejected by Google")
                await cancel_order(service_name, order_id)
                return False, "sms_phone_rejected"
        except Exception:
            pass

        # Step 5: Wait for code page to appear
        code_page_ready = False
        for _ in range(10):
            try:
                code_input = await _find_input(page, CODE_INPUT_SELECTORS)
                if code_input:
                    code_page_ready = True
                    break
                content = await page.content()
                if "enter the code" in content.lower() or "أدخل الرمز" in content.lower():
                    code_page_ready = True
                    break
            except Exception:
                pass
            await asyncio.sleep(1)

        if not code_page_ready:
            logger.error("SMS API: Code input page did not appear")
            await cancel_order(service_name, order_id)
            return False, "sms_no_code_page"

        # Step 6: Poll for SMS code
        logger.info("SMS API: Waiting for verification code...")
        code = await get_code_from_service(service_name, order_id, wait_time=180)
        if not code:
            logger.error("SMS API: Timed out waiting for code")
            await cancel_order(service_name, order_id)
            return False, "sms_timeout"

        logger.info(f"SMS API: Code received: {code}")

        # Step 7: Enter code on verification page
        code_input = await _find_input(page, CODE_INPUT_SELECTORS)
        if not code_input:
            for _ in range(5):
                await asyncio.sleep(1)
                code_input = await _find_input(page, CODE_INPUT_SELECTORS)
                if code_input:
                    break

        if not code_input:
            logger.error("SMS API: Could not find code input field")
            await cancel_order(service_name, order_id)
            return False, "sms_no_code_input"

        await code_input.click()
        await page.wait_for_timeout(300)
        await code_input.fill(code)
        await page.wait_for_timeout(800)

        # Step 8: Click Verify/Next
        await _try_click(page, VERIFY_BUTTON_SELECTORS, is_mobile=is_mobile)
        await page.wait_for_timeout(4000)

        # Step 9: Check if verification succeeded
        try:
            result_content = await page.content()
            result_lower = result_content.lower()

            verify_errors = [
                "wrong code", "incorrect code", "code is invalid",
                "الرمز غير صحيح", "that code didn't work",
                "couldn't verify", "try again",
            ]
            if any(err in result_lower for err in verify_errors):
                logger.error("SMS API: Verification code was rejected")
                await cancel_order(service_name, order_id)
                return False, "sms_code_rejected"
        except Exception:
            pass

        # Step 10: Finish order (mark as used, saves money)
        await finish_order(service_name, order_id)
        logger.info(f"SMS API: Verification successful via {service_name}")
        return True, f"sms_{service_name}"

    except ImportError:
        logger.error("SMS manager module not available")
        return False, "sms_import_error"
    except Exception as e:
        logger.error(f"SMS API error: {e}")
        if order_id and service_name:
            try:
                from services.sms_manager import cancel_order
                await cancel_order(service_name, order_id)
            except Exception:
                pass
        return False, "sms_error"


async def handle_qr_page(page, is_mobile=False):
    """
    Multi-strategy QR code bypass for Playwright flow.
    Returns: (escaped: bool, should_restart_flow: bool)
    """
    logger.warning("QR Code challenge detected — attempting escape...")

    # Strategy 1: Clear ALL session data first — the current session is flagged
    try:
        context = page.context
        await context.clear_cookies()
        await page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")
        logger.info("QR escape: Cleared cookies and storage")
    except Exception as e:
        logger.debug(f"QR escape: Cookie clear failed: {e}")

    await page.wait_for_timeout(random.randint(2000, 4000))

    # Strategy 2: Extended warmup to rebuild trust before signup
    try:
        # Visit Google and perform search (builds activity)
        await page.goto("https://www.google.com", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))

        # Accept cookies if prompted
        for btn in ["button:has-text('Accept all')", "button:has-text('I agree')", "#L2AGLb"]:
            try:
                el = await page.query_selector(btn)
                if el and await el.is_visible():
                    await el.click()
                    break
            except Exception:
                pass

        # Do a Google search related to email
        try:
            search_box = await page.query_selector("textarea[name='q'], input[name='q']")
            if search_box:
                query = random.choice(["gmail sign up", "create google account", "new email account free",
                                       "best email service", "google account help"])
                await search_box.click()
                await page.wait_for_timeout(300)
                for ch in query:
                    await page.keyboard.type(ch)
                    await page.wait_for_timeout(random.randint(50, 120))
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(random.randint(3000, 5000))

                # Click a search result
                try:
                    results = await page.query_selector_all("a h3")
                    if results and len(results) > 2:
                        target = random.choice(results[:4])
                        await target.click(timeout=3000)
                        await page.wait_for_timeout(random.randint(3000, 6000))
                except Exception:
                    pass
        except Exception:
            pass

        # Visit YouTube briefly
        await page.goto("https://www.youtube.com", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(3000, 6000))

        # Visit Google Maps for additional trust
        await page.goto("https://maps.google.com", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))

    except Exception:
        pass

    # Strategy 3: Try navigating from Google's own sign-in page → Create Account
    try:
        await page.goto("https://accounts.google.com/signin", timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 3000))

        # Click "Create account"
        for sel in [
            "a:has-text('Create account')", "button:has-text('Create account')",
            "a:has-text('إنشاء حساب')", "span:has-text('Create account')",
        ]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(2000)
                    break
            except Exception:
                continue

        # Click "For my personal use"
        for sel in [
            "li:has-text('For my personal use')", "span:has-text('For my personal use')",
            "li:has-text('For personal use')", "div:has-text('For my personal use')",
            "li:has-text('لاستخدامي الشخصي')",
        ]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(3000)
                    break
            except Exception:
                continue

        try:
            el = await page.wait_for_selector('input[name="firstName"]', timeout=8000)
            if el:
                # Verify no QR on the new page
                content = await page.content()
                if not any(s in content.lower() for s in QR_SIGNALS):
                    logger.info("QR escaped via signin → Create Account path")
                    return True, True
        except Exception:
            pass
    except Exception:
        pass

    # Strategy 4: Direct signup URLs with randomized parameters
    escape_urls = [
        "https://accounts.google.com/lifecycle/steps/signup/name?continue=https%3A%2F%2Fmyaccount.google.com&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en&theme=glif&dsh=S" + str(random.randint(1000000000, 9999999999)),
        "https://accounts.google.com/signup/v2/createaccount?biz=false&flowName=GlifWebSignIn&flowEntry=SignUp&hl=en",
        "https://accounts.google.com/SignUp?hl=en",
        "https://accounts.google.com/lifecycle/steps/signup/name?continue=https%3A%2F%2Fmail.google.com&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en&service=mail&theme=glif",
    ]

    random.shuffle(escape_urls)
    for url in escape_urls:
        try:
            await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(2000, 4000))

            try:
                el = await page.wait_for_selector('input[name="firstName"]', timeout=5000)
                if el:
                    content = await page.content()
                    if not any(s in content.lower() for s in QR_SIGNALS):
                        logger.info(f"QR escaped to fresh signup via URL")
                        return True, True
            except Exception:
                pass
        except Exception:
            continue

    # Strategy 5: Try YouTube signup flow (often bypasses QR)
    try:
        youtube_signup = "https://accounts.google.com/signup/v2/webcreateaccount?biz=false&cc=youtube&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en"
        await page.goto(youtube_signup, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))
        try:
            el = await page.wait_for_selector('input[name="firstName"]', timeout=5000)
            if el:
                content = await page.content()
                if not any(s in content.lower() for s in QR_SIGNALS):
                    logger.info("QR escaped via YouTube signup flow")
                    return True, True
        except Exception:
            pass
    except Exception:
        pass

    logger.error("All QR escape routes failed — IP/session is flagged")
    return False, False


async def handle_verification(page, is_mobile=False, use_sms_api=False, progress=None, account_task=None):
    """
    Main entry point: detect verification type and handle it.
    Returns: (success: bool, method: str, should_restart: bool)
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    page_content = ""
    try:
        page_content = await page.content()
    except Exception:
        pass

    page_url = ""
    try:
        page_url = page.url.lower()
    except Exception:
        pass

    page_type = detect_page_type(page_content)

    if page_type == "success":
        return True, "no_verification", False

    # URL-based detection for specific challenge types
    if "devicephonever" in page_url or "phonechallenge" in page_url:
        page_type = "phone"
    if "signinoptions" in page_url or "challenge" in page_url:
        page_type = "phone"

    if page_type == "qr_code":
        if progress and account_task:
            progress.update(account_task, description="[bold yellow]QR Code detected — trying escape...[/]")
        escaped, should_restart = await handle_qr_page(page, is_mobile)
        if escaped:
            return True, "qr_escaped", should_restart
        return False, "qr_blocked", False

    if page_type == "phone":
        if progress and account_task:
            progress.update(account_task, description="[bold yellow]Phone verification — trying bypass...[/]")

        sms_available = use_sms_api and bool(
            Config.FIVESIM_API_KEY or Config.SMS_ACTIVATE_API_KEY or
            Config.ONLINESIM_API_KEY or getattr(Config, 'GETSMS_API_KEY', '') or
            Config.HEROSMS_API_KEY
        )

        success, method = await handle_phone_page(page, is_mobile, sms_available)
        should_restart = method in ("send_sms_escaped", "session_reset")
        return success, method, should_restart

    logger.info(f"Page type: {page_type} — assuming no verification needed")
    return True, "none_detected", False
