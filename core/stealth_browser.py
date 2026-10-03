import os
import random
import logging
import asyncio
from config.settings import Config
from core.behavior import HumanBehavior
from core.warmup import WarmupEngine
from playwright.async_api import async_playwright

JS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "js")


def _load_js_file(filename):
    path = os.path.join(JS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Playwright stealth
try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None

logger = logging.getLogger('gmail_creator_stealth')

class PlaywrightStealthManager:
    """Manages the Playwright browser instance with advanced stealth capabilities"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_mobile = False

    async def initialize(self, proxy=None, is_premium=False):
        logger.info("Initializing Playwright Stealth Browser...")
        
        # Set environment variables for proxy before starting Playwright
        if Config.LOCAL_PROXY:
            import os
            os.environ['HTTP_PROXY'] = Config.LOCAL_PROXY
            os.environ['HTTPS_PROXY'] = Config.LOCAL_PROXY
            logger.info(f"Proxy environment variables set: {Config.LOCAL_PROXY}")
        
        self.playwright = await async_playwright().start()
        
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process,AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-background-networking=false',
            '--disable-breakpad',
            '--disable-component-update',
            '--disable-domain-reliability',
            '--disable-sync',
            '--metrics-recording-only',
            '--no-first-run',
            '--no-default-browser-check',
            '--lang=en-US',
            '--window-position=0,0',
        ]
        
        # Add proxy server to Chrome launch args
        if Config.LOCAL_PROXY:
            proxy_url = Config.LOCAL_PROXY
            if not proxy_url.startswith(('socks5://', 'socks5h://', 'http://', 'https://')):
                proxy_url = f"socks5://{proxy_url}"
            launch_args.append(f'--proxy-server={proxy_url}')
            logger.info(f"Proxy added to Chrome launch args: {proxy_url}")
        
        # Setup proxy formatting if provided
        proxy_settings = None
        use_cdp_proxy = False
        
        # Priority 1: Local proxy (for accessing Google in restricted regions)
        # Use CDP to set proxy - most reliable method
        if Config.LOCAL_PROXY:
            proxy_url = Config.LOCAL_PROXY
            if not proxy_url.startswith(('socks5://', 'socks5h://', 'http://', 'https://')):
                proxy_url = f"socks5://{proxy_url}"
            use_cdp_proxy = True
            logger.info(f"Local proxy configured via CDP: {proxy_url}")
        
        # Priority 2: External proxy pool (for IP rotation)
        elif proxy:
            parts = proxy.split(':')
            if len(parts) == 4:
                # Format: host:port:user:pass
                proxy_settings = {
                    "server": f"http://{parts[0]}:{parts[1]}",
                    "username": parts[2],
                    "password": parts[3]
                }
                logger.info(f"External proxy configured: {parts[0]}:{parts[1]} (authenticated)")
            elif len(parts) == 2:
                # Format: host:port
                proxy_settings = {"server": f"http://{parts[0]}:{parts[1]}"}
                logger.info(f"External proxy configured: {parts[0]}:{parts[1]}")
            else:
                logger.error(f"Invalid proxy format '{proxy}'. Expected 'host:port' or 'host:port:user:pass'. Proxy disabled.")
                proxy_settings = None
                
        # Launch real chrome/chromium — try installed Chrome first, fall back to bundled Chromium
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=Config.HEADLESS_MODE,
                args=launch_args,
                channel="chrome"
            )
        except Exception:
            logger.info("Installed Chrome not found, falling back to bundled Chromium...")
            self.browser = await self.playwright.chromium.launch(
                headless=Config.HEADLESS_MODE,
                args=launch_args
            )
        

        # ── Fingerprint profile (randomized per session) ───────────────────────
        chrome_versions = [
            "134.0.6998.117", "134.0.6998.89",  "133.0.6943.141",
            "133.0.6943.126", "132.0.6834.160", "132.0.6834.110",
            "131.0.6778.264", "131.0.6778.205",
        ]
        chrome_ver   = random.choice(chrome_versions)
        chrome_major = chrome_ver.split(".")[0]

        screen_profiles = [
            {"width": 1920, "height": 1080, "aw": 1920, "ah": 1040},
            {"width": 1366, "height": 768,  "aw": 1366, "ah": 728},
            {"width": 1536, "height": 864,  "aw": 1536, "ah": 824},
            {"width": 1440, "height": 900,  "aw": 1440, "ah": 860},
            {"width": 2560, "height": 1440, "aw": 2560, "ah": 1400},
        ]
        sp  = random.choice(screen_profiles)
        hw  = random.choice([4, 6, 8, 12, 16])
        mem = random.choice([4, 8, 16])

        geo_profiles = [
            {"tz": "America/New_York",    "lon": -74.006,   "lat": 40.7128},
            {"tz": "America/Chicago",     "lon": -87.6298,  "lat": 41.8781},
            {"tz": "America/Los_Angeles", "lon": -118.2437, "lat": 34.0522},
            {"tz": "Europe/London",       "lon": -0.1276,   "lat": 51.5074},
            {"tz": "Europe/Berlin",       "lon": 13.4050,   "lat": 52.5200},
        ]
        geo = random.choice(geo_profiles)

        if is_premium:
            # Mobile emulation forces SMS verification instead of QR (no QR scanning on mobile devices natively)
            ua = f"Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36"
            viewport = {"width": 412, "height": 915}
            is_mobile = True
            has_touch = True
        else:
            ua = (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Safari/537.36"
            )
            viewport = {"width": sp["width"], "height": sp["height"]}
            is_mobile = False
            has_touch = False

        self.context = await self.browser.new_context(
            viewport=viewport,
            user_agent=ua,
            locale="en-US",
            timezone_id=geo["tz"],
            has_touch=has_touch,
            is_mobile=is_mobile,
            geolocation={"longitude": geo["lon"], "latitude": geo["lat"]},
            permissions=["geolocation"],
            color_scheme="light",
            # Only set headers Chrome does NOT generate on its own.
            # Forcing sec-ch-ua*/sec-fetch-*/Accept-Encoding/Upgrade-Insecure-Requests
            # through CDP collides with the values Chrome attaches internally, and every
            # subresource request then fails with net::ERR_INVALID_ARGUMENT
            # (fonts.gstatic.com, gstatic JS/SVG). Chrome derives those headers
            # automatically from the user agent, so setting them here buys nothing.
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        self.is_mobile = is_mobile
        self.page = await self.context.new_page()
        
        # Set proxy via CDP if using local proxy
        if use_cdp_proxy and Config.LOCAL_PROXY:
            try:
                # Parse proxy URL
                proxy_url = Config.LOCAL_PROXY
                if proxy_url.startswith('http://'):
                    proxy_url = proxy_url[7:]
                    proxy_scheme = 'http'
                elif proxy_url.startswith('https://'):
                    proxy_url = proxy_url[8:]
                    proxy_scheme = 'https'
                elif proxy_url.startswith('socks5://'):
                    proxy_url = proxy_url[9:]
                    proxy_scheme = 'socks5'
                elif proxy_url.startswith('socks5h://'):
                    proxy_url = proxy_url[10:]
                    proxy_scheme = 'socks5'
                else:
                    proxy_scheme = 'socks5'
                
                # Use browser-level CDP session
                cdp = await self.browser.new_browser_cdp_session()
                await cdp.send('Network.setProxy', {
                    'proxyServer': f'{proxy_scheme}://{proxy_url}',
                    'proxyBypassList': '<-loopback>'
                })
                logger.info(f"Proxy set via browser CDP: {proxy_scheme}://{proxy_url}")
            except Exception as cdp_err:
                logger.warning(f"Failed to set proxy via browser CDP: {cdp_err}")
                # Fallback: try using environment variable
                import os
                os.environ['HTTP_PROXY'] = Config.LOCAL_PROXY
                os.environ['HTTPS_PROXY'] = Config.LOCAL_PROXY
                logger.info(f"Proxy set via environment variables: {Config.LOCAL_PROXY}")

        # ── Apply playwright-stealth ────────────────────────────────────────
        # Temporarily disabled due to conflict with poltergeist_fp.js
        # if False and stealth_async:
        #     try:
        #         await stealth_async(self.page)
        #         logger.info("Stealth plugin applied successfully.")
        #     except Exception as e:
        #         logger.warning(f"Failed to apply stealth plugin: {e}")

        # ── 12-point fingerprint spoofing (Clean & Dynamic) ────
        rtt     = random.choice([25, 50, 100, 150])
        dnl     = round(random.uniform(10, 100), 1)
        bat     = round(random.uniform(0.75, 1.0), 2)

        webgl_vendors = ["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)"]
        webgl_renderers = [
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
        ]
        gl_vendor = random.choice(webgl_vendors)
        gl_renderer = random.choice(webgl_renderers)

        await self.page.add_init_script(f"""
        (() => {{
            // 1. Remove webdriver flag (handled by poltergeist_fp.js)
            // try {{ delete navigator.__proto__.webdriver; }} catch(_) {{}}
            // Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});

            // 2. Battery API
            if(navigator.getBattery){{navigator.getBattery=()=>Promise.resolve({{
                charging: true, chargingTime: 0, dischargingTime: Infinity, level: {bat},
                onchargingchange: null, onchargingtimechange: null, ondischargingtimechange: null, onlevelchange: null
            }});}}

            // 3. Network connection - handled by poltergeist_fp.js
            // if (navigator.connection) {{
            //     Object.defineProperty(navigator, 'connection', {{ get: () =>
            //         ({{'effectiveType':'4g','rtt':{rtt},'downlink':{dnl},'saveData':false,'type':'wifi','onchange':null}})
            //     }});
            // }}

            // 4. Languages - handled by poltergeist_fp.js
            // Object.defineProperty(navigator, 'languages', {{get: () => ['en-US', 'en']}});
            // Object.defineProperty(navigator, 'language', {{get: () => 'en-US'}});

            // 5. Hardware concurrency & device memory - handled by poltergeist_fp.js
            // Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hw}}});
            // Object.defineProperty(navigator, 'deviceMemory', {{get: () => {mem}}});

            // 6. WebGL vendor/renderer spoof
            const origGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {{
                if (param === 37445) return '{gl_vendor}';
                if (param === 37446) return '{gl_renderer}';
                return origGetParameter.call(this, param);
            }};
            const origGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(param) {{
                if (param === 37445) return '{gl_vendor}';
                if (param === 37446) return '{gl_renderer}';
                return origGetParameter2.call(this, param);
            }};

            // 7. Plugins - handled by poltergeist_fp.js
            // Removed to avoid conflict with poltergeist_fp.js which defines navigator.plugins

            // 8. Permissions API spoof (avoid "prompt" for notifications — real browsers have "denied" or "granted")
            const origQuery = Permissions.prototype.query;
            Permissions.prototype.query = function(desc) {{
                if (desc.name === 'notifications') return Promise.resolve({{state: 'denied', onchange: null}});
                return origQuery.call(this, desc);
            }};

            // 9. Screen properties
            Object.defineProperty(screen, 'availWidth', {{get: () => {sp['aw']}}});
            Object.defineProperty(screen, 'availHeight', {{get: () => {sp['ah']}}});
            Object.defineProperty(screen, 'colorDepth', {{get: () => 24}});
            Object.defineProperty(screen, 'pixelDepth', {{get: () => 24}});

            // 10. Remove Playwright/automation traces from all frames
            ['__playwright','__pw_manual','_playwrightBinding','__playwright__binding__',
             'cdc_adoQpoasnfa76pfcZLmcfl_Array','cdc_adoQpoasnfa76pfcZLmcfl_Promise',
             'cdc_adoQpoasnfa76pfcZLmcfl_Symbol','__webdriver_evaluate','__selenium_evaluate',
             '__webdriver_script_function','__webdriver_script_func','__webdriver_script_fn',
             '__fxdriver_evaluate','__driver_evaluate','__webdriver_unwrapped',
             '__selenium_unwrapped','__fxdriver_unwrapped','_Selenium_IDE_Recorder',
             '_selenium','calledSelenium','_WEBDRIVER_ELEM_CACHE',
             'ChromeDriverw','driver-evaluate','webdriver-evaluate-response',
             'domAutomation','domAutomationController'
            ].forEach(k => {{ try {{ delete window[k]; }} catch(_) {{}} }});

            // 11. Chrome runtime (Google checks for this — must exist in Chrome)
            if (!window.chrome) {{
                window.chrome = {{
                    runtime: {{
                        connect: function() {{}},
                        sendMessage: function() {{}},
                        onMessage: {{addListener: function() {{}}, removeListener: function() {{}}}},
                        onConnect: {{addListener: function() {{}}, removeListener: function() {{}}}}
                    }},
                    loadTimes: function() {{ return {{}}; }},
                    csi: function() {{ return {{}}; }}
                }};
            }}

            // 12. Canvas fingerprint noise (subtle, not broken)
            const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                if (this.width > 16 && this.height > 16) {{
                    try {{
                        const ctx = this.getContext('2d');
                        if (ctx) {{
                            const imgData = ctx.getImageData(0, 0, 1, 1);
                            imgData.data[0] = (imgData.data[0] + {random.randint(1, 3)}) % 256;
                            ctx.putImageData(imgData, 0, 0);
                        }}
                    }} catch(_) {{}}
                }}
                return origToDataURL.apply(this, arguments);
            }};
        }})();
        """)

        # ── Session Warmup (builds trust cookies before signup) ─────────────
        if Config.ENABLE_SESSION_WARMING and not is_premium:
            logger.info("Session warming enabled — running warmup engine...")
            try:
                await WarmupEngine.run_warmup(self.page, duration_minutes=1)
            except Exception as wu_e:
                logger.warning(f"Warmup failed (non-fatal): {wu_e}")
        else:
            logger.info("Session warming disabled or Premium Mode active (skipping warmup).")

        # ── Inject Poltergeist fingerprint script from JS file ─────────────
        if Config.ENABLE_POLTERGEIST:
            poltergeist_js = _load_js_file("poltergeist_fp.js")
            if poltergeist_js:
                await self.page.add_init_script(poltergeist_js)
                logger.info("Poltergeist FP script injected from js/poltergeist_fp.js")

        # ── Inject Ghost Typer behavioral script from JS file ──────────────
        if Config.ENABLE_GHOST_TYPER:
            ghost_js = _load_js_file("ghost_typer.js")
            if ghost_js:
                await self.page.add_init_script(ghost_js)
                logger.info("Ghost Typer script injected from js/ghost_typer.js")

        # ── Inject Cookie Reaper trust cookies ─────────────────────────────
        if Config.ENABLE_COOKIE_REAPER:
            try:
                from core.cookie_reaper import inject_cookies_playwright
                injected = await inject_cookies_playwright(self.page)
                if injected:
                    logger.info("Cookie Reaper: Trust cookies injected into context")
            except Exception as cr_e:
                logger.warning(f"Cookie Reaper injection failed (non-fatal): {cr_e}")

        logger.info(f"FP: Chrome/{chrome_ver} | {sp['width']}x{sp['height']} | {geo['tz']} | {hw}c/{mem}GB")
        return True


    async def close(self):
        try:
            if self.page:
                await self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                await self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
            
    async def natural_type(self, selector, text):
        try:
            return await HumanBehavior.natural_type(self.page, selector, text, make_typos=Config.ENABLE_HUMAN_TYPING_ERRORS)
        except Exception as e:
            logger.warning(f"natural_type failed for '{selector}': {e}")
            return False
        
    async def natural_click(self, selector):
        try:
            element = await self.page.wait_for_selector(selector, timeout=8000)
            if element:
                box = await element.bounding_box()
                if box:
                    x = box["x"] + box["width"] / 2 + random.uniform(-2, 2)
                    y = box["y"] + box["height"] / 2 + random.uniform(-2, 2)
                    await self.page.mouse.move(x, y, steps=10)
                    await self.page.mouse.click(x, y)
                else:
                    await element.click()
                return True
            return False
        except Exception as e:
            logger.warning(f"natural_click failed for '{selector}': {e}")
            return False

    async def _wait_for_birthday_page(self, timeout_ms=20000):
        """Wait until the birthday/gender page is visible with multiple selector attempts."""
        birthday_selectors = [
            'input[name="day"]',
            'select#month',
            'select[name="month"]',
            'input[name="year"]',
            '#day', '#month', '#year',
        ]
        deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
        while asyncio.get_running_loop().time() < deadline:
            for sel in birthday_selectors:
                try:
                    el = await self.page.query_selector(sel)
                    if el and await el.is_visible():
                        return True
                except Exception:
                    pass
            await asyncio.sleep(0.3)
        return False

    async def fill_birthday_gender(self, month, day, year, gender):
        """Fill birthday (month, day, year) and gender on Google signup page."""
        try:
            logger.info(f"fill_birthday_gender: month={month}, day={day}, year={year}, gender={gender}")

            page_found = await self._wait_for_birthday_page(timeout_ms=20000)
            if not page_found:
                logger.warning("Birthday page not detected within 20s, attempting to fill anyway.")

            await self.page.wait_for_timeout(500)

            month_names = ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
            try:
                month_idx = int(month)
                if not (1 <= month_idx <= 12):
                    month_idx = 1
            except Exception:
                month_idx = 1
            month_text = month_names[month_idx - 1]
            month_str = str(month_idx)

            # ─── MONTH ───────────────────────────────────────────────────────
            month_ok = False

            for sel in ['select#month', 'select[name="month"]', 'select[aria-label*="onth" i]',
                        'select[aria-label*="شهر"]']:
                try:
                    el = await self.page.query_selector(sel)
                    if el and await el.is_visible():
                        try:
                            await el.select_option(value=month_str)
                            month_ok = True
                            break
                        except Exception:
                            pass
                        try:
                            await el.select_option(label=month_text)
                            month_ok = True
                            break
                        except Exception:
                            pass
                except Exception:
                    continue

            if not month_ok:
                for trigger_sel in ['#month', '[aria-label*="Month"]', '[placeholder="Month"]',
                                    'div[data-id="month"]', 'span:has-text("Month")']:
                    try:
                        trigger = await self.page.query_selector(trigger_sel)
                        if trigger and await trigger.is_visible():
                            await trigger.click()
                            await self.page.wait_for_timeout(500)
                            for opt_sel in [
                                f'li[data-value="{month_str}"]',
                                f'[role="option"][data-value="{month_str}"]',
                                f'[role="option"]:has-text("{month_text}")',
                                f'li:has-text("{month_text}")',
                            ]:
                                try:
                                    opt = await self.page.wait_for_selector(opt_sel, timeout=1500)
                                    if opt:
                                        await opt.click()
                                        month_ok = True
                                        break
                                except Exception:
                                    continue
                            if month_ok:
                                break
                    except Exception:
                        continue

            if not month_ok:
                await self.page.evaluate("""(m) => {
                    const s = document.querySelector('select#month')
                           || document.querySelector('select[name="month"]');
                    if (s) {
                        s.value = m;
                        s.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""", month_str)

            await self.page.wait_for_timeout(300)

            # ─── DAY ─────────────────────────────────────────────────────────
            day_ok = False
            for sel in ['input[name="day"]', '#day', 'input[aria-label*="Day" i]',
                        'input[placeholder="Day"]']:
                try:
                    el = await self.page.query_selector(sel)
                    if el and await el.is_visible():
                        await el.click()
                        await self.page.wait_for_timeout(100)
                        await el.click(click_count=3)
                        await el.fill(day)
                        await el.dispatch_event("input")
                        day_ok = True
                        break
                except Exception:
                    continue

            if not day_ok:
                await self.page.evaluate("""(d) => {
                    const inp = document.querySelector('input[name="day"]');
                    if (inp) { inp.value = d; inp.dispatchEvent(new Event('input', { bubbles: true })); }
                }""", day)

            await self.page.wait_for_timeout(300)

            # ─── YEAR ────────────────────────────────────────────────────────
            year_ok = False
            for sel in ['input[name="year"]', '#year', 'input[aria-label*="Year" i]',
                        'input[placeholder="Year"]']:
                try:
                    el = await self.page.query_selector(sel)
                    if el and await el.is_visible():
                        attr_name = await el.get_attribute("name")
                        if attr_name and attr_name.lower() == "day":
                            continue
                        await el.click()
                        await self.page.wait_for_timeout(100)
                        await el.click(click_count=3)
                        await el.fill(year)
                        await el.dispatch_event("input")
                        year_ok = True
                        break
                except Exception:
                    continue

            if not year_ok:
                await self.page.evaluate("""(y) => {
                    const inp = document.querySelector('input[name="year"]');
                    if (inp) { inp.value = y; inp.dispatchEvent(new Event('input', { bubbles: true })); }
                }""", year)

            await self.page.wait_for_timeout(300)

            # ─── GENDER (fast & correct) ─────────────────────────────────────
            # Debug: Log what select elements exist on the page
            try:
                select_info = await self.page.evaluate("""() => {
                    const selects = document.querySelectorAll('select');
                    const info = [];
                    for (const s of selects) {
                        const opts = Array.from(s.options).map(o => o.value + '=' + o.textContent.trim());
                        info.push({id: s.id, name: s.name, visible: s.offsetParent !== null, opts: opts});
                    }
                    return JSON.stringify(info);
                }""")
                logger.info(f"Page select elements: {select_info}")
            except Exception:
                pass

            gender_ok = False
            gender_text_map = {"1": "Male", "2": "Female", "3": "Rather not say", "0": "Rather not say"}
            gtext = gender_text_map.get(str(gender), "Male")

            # Google's <select> value mapping: 1=Female, 2=Male, 3=Rather not say, 4=Custom
            google_gender_val = {"1": "2", "2": "1", "3": "3", "0": "3"}
            gval = google_gender_val.get(str(gender), "2")

            # Strategy A: Super aggressive JS — find ANY select on the page and set it
            # (birthday uses <select> for month too, so we skip selects with month-like options)
            try:
                result = await self.page.evaluate("""(args) => {
                    const [gval, gtext] = args;
                    // Collect all selects on the page
                    const allSelects = document.querySelectorAll('select');
                    let genderSelect = null;

                    for (const sel of allSelects) {
                        // Skip month selects (they have January/February etc)
                        let isMonth = false;
                        for (const opt of sel.options) {
                            const t = opt.textContent.trim().toLowerCase();
                            if (t === 'january' || t === 'february' || t === 'march' ||
                                t === 'يناير' || t === 'فبراير') {
                                isMonth = true; break;
                            }
                        }
                        if (isMonth) continue;

                        // Check if this has gender-like options (Male/Female/Rather not say)
                        let hasGenderOption = false;
                        for (const opt of sel.options) {
                            const t = opt.textContent.trim().toLowerCase();
                            if (t === 'male' || t === 'female' || t === 'rather not say' ||
                                t === 'ذكر' || t === 'أنثى' || t.includes('gender') ||
                                t.includes('الجنس')) {
                                hasGenderOption = true; break;
                            }
                        }
                        if (hasGenderOption || sel.id === 'gender' || sel.name === 'gender') {
                            genderSelect = sel; break;
                        }

                        // If only one non-month select remains, it's probably gender
                        if (!genderSelect && allSelects.length <= 2) {
                            genderSelect = sel;
                        }
                    }

                    if (!genderSelect) return 'no_gender_select_found';

                    // Log what we found for debugging
                    const optionTexts = Array.from(genderSelect.options).map(o => o.value + ':' + o.textContent.trim());
                    const info = 'id=' + genderSelect.id + ',name=' + genderSelect.name + ',opts=' + optionTexts.join('|');

                    // Method 1: Match by option text
                    for (const opt of genderSelect.options) {
                        const txt = opt.textContent.trim().toLowerCase();
                        if (txt === gtext.toLowerCase()) {
                            genderSelect.selectedIndex = opt.index;
                            genderSelect.value = opt.value;
                            genderSelect.dispatchEvent(new Event('input', { bubbles: true }));
                            genderSelect.dispatchEvent(new Event('change', { bubbles: true }));
                            genderSelect.dispatchEvent(new Event('blur', { bubbles: true }));
                            return 'ok_text:' + opt.value + '|' + info;
                        }
                    }

                    // Method 2: Set by value directly
                    genderSelect.value = gval;
                    genderSelect.selectedIndex = parseInt(gval);
                    genderSelect.dispatchEvent(new Event('input', { bubbles: true }));
                    genderSelect.dispatchEvent(new Event('change', { bubbles: true }));
                    genderSelect.dispatchEvent(new Event('blur', { bubbles: true }));
                    return 'ok_val:' + gval + '|' + info;
                }""", [gval, gtext])
                if result and result.startswith('ok'):
                    gender_ok = True
                    logger.info(f"Gender set via JS: {result}")
                else:
                    logger.warning(f"Gender JS result: {result}")
            except Exception as e:
                logger.debug(f"Gender JS strategy failed: {e}")

            # Strategy B: Playwright select_option on all matching selectors
            if not gender_ok:
                gender_selectors = ['select#gender', 'select[name="gender"]', 'select[id="gender"]',
                                    'select[aria-label*="ender" i]', 'select[aria-label*="جنس"]',
                                    'select']
                for sel in gender_selectors:
                    try:
                        elements = await self.page.query_selector_all(sel)
                        for el in elements:
                            if not await el.is_visible():
                                continue
                            # Skip month select
                            try:
                                tag_name = await el.evaluate("e => e.id || e.name || ''")
                                if 'month' in str(tag_name).lower():
                                    continue
                            except Exception:
                                pass
                            try:
                                await el.select_option(value=gval)
                                gender_ok = True
                                logger.info(f"Gender set via select_option(value={gval})")
                                break
                            except Exception:
                                pass
                            try:
                                await el.select_option(label=gtext)
                                gender_ok = True
                                logger.info(f"Gender set via select_option(label={gtext})")
                                break
                            except Exception:
                                pass
                        if gender_ok:
                            break
                    except Exception:
                        continue

            # Strategy C: Focus the select + keyboard to select option
            if not gender_ok:
                try:
                    # Find gender select via evaluate and focus it
                    focused = await self.page.evaluate("""() => {
                        const allSelects = document.querySelectorAll('select');
                        for (const sel of allSelects) {
                            if (sel.id === 'gender' || sel.name === 'gender') {
                                sel.focus(); return true;
                            }
                            // Check if NOT a month select
                            let isMonth = false;
                            for (const opt of sel.options) {
                                const t = opt.textContent.trim().toLowerCase();
                                if (['january','february','march','april','may','june'].includes(t)) {
                                    isMonth = true; break;
                                }
                            }
                            if (!isMonth && sel.options.length >= 3) {
                                sel.focus(); return true;
                            }
                        }
                        return false;
                    }""")
                    if focused:
                        await self.page.wait_for_timeout(300)
                        # Arrow down to select the right option
                        presses = int(gval)
                        for _ in range(presses):
                            await self.page.keyboard.press("ArrowDown")
                            await self.page.wait_for_timeout(100)
                        await self.page.wait_for_timeout(200)
                        gender_ok = True
                        logger.info(f"Gender set via keyboard ({presses} ArrowDown)")
                except Exception as e:
                    logger.debug(f"Gender keyboard strategy failed: {e}")

            # Strategy D: Handle Material Design / Web Component dropdowns
            # Google may use <md-outlined-select>, div[role="listbox"], or custom elements
            if not gender_ok:
                try:
                    result = await self.page.evaluate("""(gtext) => {
                        // Check for Material Design select components
                        const mdSelects = document.querySelectorAll(
                            'md-outlined-select, md-filled-select, [role="listbox"], [role="combobox"], ' +
                            'div[data-value], div.VfPpkd-TkwUic, div[jsname]'
                        );

                        // Also check for any clickable dropdown-like elements with Gender text
                        const allElements = document.querySelectorAll('*');
                        let genderContainer = null;
                        for (const el of allElements) {
                            const text = el.textContent.trim();
                            if ((text === 'Gender' || text === 'الجنس') &&
                                el.tagName !== 'LABEL' && el.tagName !== 'SPAN' &&
                                el.offsetParent !== null) {
                                genderContainer = el.closest('[role="listbox"], [role="combobox"], [jscontroller]') || el;
                                break;
                            }
                        }

                        if (genderContainer) {
                            genderContainer.click();
                            return 'clicked_container';
                        }
                        return 'no_md_component';
                    }""", gtext)

                    if result == 'clicked_container':
                        await self.page.wait_for_timeout(800)
                        # Now find and click the option text (Male/Female etc)
                        try:
                            option_clicked = await self.page.evaluate("""(gtext) => {
                                const items = document.querySelectorAll(
                                    '[role="option"], [role="menuitem"], li, md-select-option, ' +
                                    'div[data-value], span'
                                );
                                for (const item of items) {
                                    const t = item.textContent.trim().toLowerCase();
                                    if (t === gtext.toLowerCase() && item.offsetParent !== null) {
                                        item.click();
                                        return 'clicked:' + t;
                                    }
                                }
                                return 'no_option';
                            }""", gtext)
                            if option_clicked and option_clicked.startswith('clicked'):
                                gender_ok = True
                                logger.info(f"Gender set via MD component: {option_clicked}")
                        except Exception:
                            pass
                except Exception as e:
                    logger.debug(f"Gender MD component strategy failed: {e}")

            if not gender_ok:
                logger.warning(f"Could not select gender '{gtext}' — continuing anyway")

            await self.page.wait_for_timeout(400)
            return True

        except Exception as e:
            logger.error(f"fill_birthday_gender error: {e}", exc_info=True)
            return True
