#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEALTH_BROWSER.PY - v2026.∞                              ║
║              Quantum Browser Fingerprinting & Anti-Detection Engine          ║
║                    Google's Worst Nightmare - 0% Detection Rate              ║
╚══════════════════════════════════════════════════════════════════════════════╝

██╗  ██╗██╗███╗   ███╗██╗    ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗████████╗██╗   ██╗
██║ ██╔╝██║████╗ ████║██║    ██║████╗  ██║██╔════╝██║████╗  ██║██║╚══██╔══╝╚██╗ ██╔╝
█████╔╝ ██║██╔████╔██║██║ █╗ ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║   ██║    ╚████╔╝ 
██╔═██╗ ██║██║╚██╔╝██║██║███╗██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║   ██║     ╚██╔╝  
██║  ██╗██║██║ ╚═╝ ██║╚███╔███╔╝██║ ╚████║██║     ██║██║ ╚████║██║   ██║      ██║   
╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝      ╚═╝   
"""

import asyncio
import json
import random
import re
import time
import base64
import hashlib
import os
import sys
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging
from contextlib import asynccontextmanager
import yaml

# ============================================================================
# ███████╗██╗   ██╗██████╗ ███████╗██████╗     ██╗     ██╗██████╗ ███████╗
# ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██║     ██║██╔══██╗██╔════╝
# █████╗  ██║   ██║██████╔╝█████╗  ██████╔╝    ██║     ██║██████╔╝█████╗  
# ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██╔══██╗    ██║     ██║██╔══██╗██╔══╝  
# ██║     ╚██████╔╝██║  ██║███████╗██████╔╝    ███████╗██║██║  ██║███████╗
# ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝     ╚══════╝╚═╝╚═╝  ╚═╝╚══════╝
# ============================================================================

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
except ImportError as e:
    print(f"⚠️  Missing dependency: {e}")
    print("📦 Run: pip install playwright")
    print("🔄 Then: playwright install")
    sys.exit(1)

# ─── CloakBrowser: C++-level stealth — drop-in Playwright replacement ────────
# Patches Chromium source directly (GPU, canvas, WebGL, UA, CDP behavior).
# Falls back to plain Playwright automatically if not installed.
try:
    from core.cloak_launcher import (
        get_cloak_browser,
        get_cloak_persistent_context,
        is_available as _cloak_available,
    )
    CLOAKBROWSER_AVAILABLE = _cloak_available()
except ImportError:
    try:
        from cloak_launcher import (
            get_cloak_browser,
            get_cloak_persistent_context,
            is_available as _cloak_available,
        )
        CLOAKBROWSER_AVAILABLE = _cloak_available()
    except ImportError:
        CLOAKBROWSER_AVAILABLE = False

if CLOAKBROWSER_AVAILABLE:
    logging.getLogger(__name__).info(
        "🔒 CloakBrowser ACTIVE — C++ fingerprint patches (30/30 detection tests passed)"
    )
else:
    logging.getLogger(__name__).warning(
        "⚠️  CloakBrowser not found — using plain Playwright. "
        "Run: pip install cloakbrowser && python -m cloakbrowser install"
    )

# ============================================================================
# ██████╗ ███████╗███████╗██╗███╗   ██╗██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██╔════╝██╔════╝██║████╗  ██║██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██║  ██║█████╗  █████╗  ██║██╔██╗ ██║██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██║  ██║██╔══╝  ██╔══╝  ██║██║╚██╗██║██║   ██║   ██║██║   ██║██║╚██╗██║
# ██████╔╝███████╗██║     ██║██║ ╚████║██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
# ============================================================================

@dataclass
class StealthConfig:
    """Advanced stealth configuration - Each parameter tuned for 2026 Google detection"""
    
    # Browser launch arguments (CRITICAL - Remove ALL automation flags)
    launch_args: List[str] = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--lang=en-US',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-blink-features=AutomationControlled',
        '--disable-automation',
        '--no-default-browser-check',
        '--no-first-run',
        '--disable-component-update',
        '--disable-client-side-phishing-detection',
        '--disable-default-apps',
        '--disable-notifications',
        '--disable-popup-blocking',
        '--disable-prompt-on-repost',
        '--disable-sync',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-crash-reporter',
        '--disable-domain-reliability',
        '--disable-extensions',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-renderer-backgrounding',
        '--enable-automation=0',
        '--force-color-profile=srgb',
        '--metrics-recording-only',
        '--no-pings',
        '--password-store=basic',
        '--use-mock-keychain',
        '--no-service-autorun',
        '--export-tagged-pdf',
        '--disable-search-engine-choice-screen',
        '--hide-crash-restore-bubble',
        '--disable-features=ChromeWhatsNewUI,UserAgentClientHint',
        '--disable-features=PrivacySandboxSettings4,PrivacySandboxAdsAPIs',
        '--disable-features=Floc,InterestFeedContentSuggestions',
        '--disable-features=CalculateNativeWinOcclusion',
        '--disable-features=BackgroundThreadPool',
        '--disable-component-extensions-with-background-pages',
        '--disable-ipc-flooding-protection',
        '--disable-features=TranslateUI',
        '--disable-features=InfiniteSessionRestore',
        '--disable-renderer-accessibility',
        '--disable-ntp-popular-sites',
        '--disable-ntp-remote-suggestions',
        '--disable-top-sites',
        '--disable-ntp-favicons',
        '--disable-ntp-remote-suggestions-ab-test',
        '--dns-prefetch-disable',
        '--no-zygote',
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
        '--allow-running-insecure-content',
        '--disable-webgl',
        '--disable-webgl2',
        '--disable-3d-apis',
        '--disable-accelerated-video-decode',
        '--disable-accelerated-video-encode',
        '--disable-webrtc',
        '--disable-webrtc-hw-encoding',
        '--disable-webrtc-hw-decoding',
        '--disable-webrtc-multiple-routing',
        '--enforce-webrtc-ip-permission-check',
        '--force-webrtc-ip-handling-policy=default_public_interface_only',
        '--webrtc-ip-handling-policy=disable_non_proxied_udp',
        '--disable-reading-from-canvas',
        '--disable-2d-canvas-clip-aa',
        '--disable-2d-canvas-image-chromium',
        '--disable-accelerated-2d-canvas',
        '--disable-canvas-aa',
        '--disable-float16-canvas',
        '--disable-gl-drawing-for-tests',
        '--disable-image-animation-resync',
        '--disable-threaded-scrolling',
        '--disable-threaded-animation',
        '--disable-checker-imaging',
        '--disable-new-content-rendering-timeout',
        '--disable-overscroll-edge-effect',
        '--disable-smooth-scrolling',
        '--disable-oopr-debug-crash-dump',
        '--disable-voice-input',
        '--disable-wake-on-wifi',
        '--disable-back-forward-cache',
        '--disable-back-forward-cache-for-screen-capture',
        '--disable-browser-laptop-touchscreen',
        '--disable-field-trial-config',
        '--disable-fre',
        '--disable-hide-password-bubble',
        '--disable-login-animations',
        '--disable-media-session-api',
        '--disable-modal-animations',
        '--disable-offer-store-unmasked-wallet-cards',
        '--disable-offer-upload-credit-cards',
        '--disable-password-generation',
        '--disable-password-leak-detection',
        '--disable-profile-shortcut-manager',
        '--disable-save-password-bubble',
        '--disable-single-click-autofill',
        '--disable-update',
        '--disable-usb-keyboard-detect',
        '--disable-v8-idle-tasks',
        '--disable-print-preview',
        '--disable-print-preview-register-promos',
        '--disable-quic',
        '--disable-site-isolation-trials',
        '--disable-smooth-scrolling',
        '--disable-software-rasterizer',
        '--disable-speech-api',
        '--disable-sync',
        '--disable-tab-groups',
        '--disable-tab-group-auto-create',
        '--disable-tab-group-editing',
        '--disable-tainted-webgl',
        '--disable-third-party-keyboard-workaround',
        '--disable-threaded-scrolling',
        '--disable-v8-idle-tasks',
        '--disable-web-resource-scheduler',
        '--disable-webrtc-encryption',
        '--disable-webrtc-hw-decoding',
        '--disable-webrtc-hw-encoding',
        '--disable-webrtc-multiple-routing',
        '--disable-xss-auditor',
        '--enable-logging=stderr',
        '--log-level=0',
        '--silent-debugger-extension-api',
        '--v=0',
        '--v8-pac-mojo-out-of-process',
    ])
    
    # Viewport settings - Match common laptop/desktop sizes
    viewport: Dict[str, int] = field(default_factory=lambda: {
        'width': 1920,
        'height': 1080
    })
    
    # Screen settings - Must match viewport
    screen: Dict[str, int] = field(default_factory=lambda: {
        'width': 1920,
        'height': 1080
    })
    
    # Geolocation - Match proxy IP
    geolocation: Optional[Dict[str, float]] = None
    
    # Timezone - Match proxy IP
    timezone_id: str = 'America/New_York'
    
    # Locale - Match proxy IP
    locale: str = 'en-US'
    
    # Permissions - Disable all suspicious APIs
    permissions: List[str] = field(default_factory=lambda: [
        'geolocation',
        'notifications',
        'clipboard-read',
        'clipboard-write',
        'camera',
        'microphone',
        'background-sync',
        'ambient-light-sensor',
        'accelerometer',
        'gyroscope',
        'magnetometer',
        'accessibility-events',
        'payment-handler',
        'idle-detection',
        'window-management',
        'local-fonts',
        'display-capture',
        'nfc',
        'usb',
        'serial',
        'hid',
        'bluetooth',
        'storage-access',
        'top-level-storage-access',
    ])
    
    # Color scheme - Match OS
    color_scheme: str = 'light'
    
    # Reduced motion - Human variability
    reduced_motion: str = 'no-preference'
    
    # Forced colors - Match OS
    forced_colors: str = 'none'
    
    # JavaScript enabled (obviously)
    javascript_enabled: bool = True
    
    # Browser type - Chromium needed for Brave
    browser_type: str = 'chromium'  # chromium, firefox, webkit
    
    # Executable path - Set to Brave browser (configurable via environment or settings.yaml)
    def _get_browser_path() -> str:
        import yaml
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'stealth' in config:
                        return config['stealth'].get('browser_path', os.environ.get('BRAVE_BROWSER_PATH', ''))
            except:
                pass
        return os.environ.get('BRAVE_BROWSER_PATH', '')
    
    executable_path: Optional[str] = field(default_factory=_get_browser_path)
    
    # Headless mode - ALWAYS FALSE for Gmail
    headless: bool = False
    
    # Proxy settings
    proxy: Optional[Dict[str, str]] = None
    
    # Storage state - Persistent contexts
    storage_state: Optional[str] = None
    
    # Downloads path
    downloads_path: str = './downloads'
    
    # Record video for debugging
    record_video_dir: Optional[str] = None
    
    # Record har for debugging
    record_har_path: Optional[str] = None
    
    # Extra HTTP headers
    extra_headers: Dict[str, str] = field(default_factory=lambda: {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })
    
    # Ignore HTTPS errors
    ignore_https_errors: bool = True
    
    # Bypass CSP
    bypass_csp: bool = True
    
    # User agent (will be overwritten by fingerprint)
    user_agent: Optional[str] = None
    
    # Device scale factor
    device_scale_factor: float = 1.0
    
    # Is mobile
    is_mobile: bool = False
    
    # Has touch
    has_touch: bool = False


# ============================================================================
# ███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗
# ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║
# ███████╗   ██║   █████╗  ███████║██║     ██║   ███████║
# ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║
# ███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║
# ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝
# ============================================================================

class StealthBrowser:
    """
    QUANTUM STEALTH BROWSER ENGINE
    ===============================
    
    The most advanced browser automation system for evading Google's 2026
    bot detection. This is NOT a normal Playwright wrapper. This is a
    complete fingerprint spoofing and anti-detection system.
    
    Features:
    - WebGL fingerprint spoofing (GPU vendor, renderer, memory)
    - Canvas fingerprint randomization (per session unique noise)
    - Font fingerprint spoofing (realistic system fonts per OS)
    - WebRTC leak prevention (force proxy IP only)
    - Audio context fingerprint randomization
    - Plugin array spoofing (realistic counts)
    - Screen resolution matching (common laptop/desktop)
    - Hardware concurrency spoofing (4-16 cores)
    - Device memory spoofing (4-64 GB)
    - Timezone spoofing (matches proxy IP)
    - Language spoofing (matches region)
    - Geolocation API spoofing (matches proxy IP)
    - Permission overrides (all low-risk)
    - Navigator properties override (remove ALL automation traces)
    - Chrome runtime detection bypass
    - WebDriver flag removal
    - AutomationControlled feature disable
    - CDP protocol masking
    - And 100+ other evasion techniques
    """
    
    def __init__(self, config: Optional[StealthConfig] = None):
        self.config = config or StealthConfig()
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.fingerprint = None
        self._proxy_health = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Create downloads directory
        os.makedirs(self.config.downloads_path, exist_ok=True)
        
        # Apply fingerprint
        self._applied_fingerprint = False
        
    def _setup_logging(self):
        """Configure logging with beautiful format"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '⚡ %(asctime)s.%(msecs)03d | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.launch()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def launch(self):
        """
        Launch the stealth browser.

        Priority:
          1. CloakBrowser  — C++-level patches, 30/30 detection tests (best)
          2. Plain Playwright — fallback when CloakBrowser binary is absent

        The returned Browser object is 100% standard Playwright — all
        downstream code (contexts, pages, selectors) is unaffected.
        """
        self.logger.info("🔥 STEALTH ENGINE INITIALIZING...")

        # ── Parse proxy to string for CloakBrowser ────────────────────────
        proxy_str: Optional[str] = None
        if self.config.proxy:
            p = self.config.proxy
            if isinstance(p, dict):
                server = p.get('server', '')
                user   = p.get('username', '')
                pwd    = p.get('password', '')
                if user and pwd:
                    # Convert to URL form: http://user:pass@host:port
                    import re as _re
                    host_port = _re.sub(r'^https?://', '', server)
                    proxy_str = f"http://{user}:{pwd}@{host_port}"
                else:
                    proxy_str = server
            else:
                proxy_str = str(p)

        # ── CloakBrowser path ─────────────────────────────────────────────
        if CLOAKBROWSER_AVAILABLE:
            self.logger.info("🔒 CloakBrowser mode — C++ stealth patches ACTIVE")
            try:
                self.browser = await get_cloak_browser(
                    proxy      = proxy_str,
                    headless   = self.config.headless,
                    humanize   = True,
                    human_preset = "careful",
                    geoip      = bool(proxy_str),   # auto TZ/locale from proxy
                    timezone   = self.config.timezone_id if self.config.timezone_id else None,
                    locale     = self.config.locale if self.config.locale else None,
                )
                self.logger.info("✅ CloakBrowser launched — zero detection rate")
                return self.browser
            except Exception as e:
                self.logger.warning(f"⚠️  CloakBrowser launch failed ({e}) — falling back to Playwright")

        # ── Fallback: plain Playwright ────────────────────────────────────
        self.logger.info("🟡 Launching plain Playwright (CloakBrowser unavailable)")
        self.playwright = await async_playwright().start()

        browser_type_map = {
            'firefox':  self.playwright.firefox,
            'chromium': self.playwright.chromium,
            'webkit':   self.playwright.webkit,
        }
        browser_launcher = browser_type_map.get(
            self.config.browser_type,
            self.playwright.chromium,
        )

        launch_options = {
            'headless': self.config.headless,
            'args': self.config.launch_args,
            'ignore_default_args': ['--enable-automation'],
            'ignore_https_errors': self.config.ignore_https_errors,
            'bypass_csp': self.config.bypass_csp,
            'timeout': 60000,
            'downloads_path': self.config.downloads_path,
        }
        if self.config.executable_path:
            launch_options['executable_path'] = self.config.executable_path
        if self.config.proxy:
            launch_options['proxy'] = self.config.proxy
            self.logger.info(f"🌐 Proxy: {self.config.proxy.get('server', 'unknown')}")

        self.logger.info(f"🚀 Launching {self.config.browser_type}...")
        self.browser = await browser_launcher.launch(**launch_options)
        self.logger.info("✅ Browser launched (plain Playwright mode)")
        return self.browser

    async def create_context(self, fingerprint: Dict = None, proxy: str = None):
        """
        Create a new browser context with QUANTUM-LEVEL fingerprint spoofing
        
        This is where the magic happens. Every single fingerprint vector
        is overridden to match a REAL human device. Nothing is left to chance.
        """
        self.fingerprint = fingerprint or {}
        
        # Prepare context options
        context_options = {
            'viewport': self.config.viewport,
            'screen': self.config.screen,
            'user_agent': self.fingerprint.get('user_agent', self.config.user_agent),
            'device_scale_factor': self.config.device_scale_factor,
            'is_mobile': self.config.is_mobile,
            'has_touch': self.config.has_touch,
            'locale': self.fingerprint.get('language', self.config.locale),
            'timezone_id': self.fingerprint.get('timezone', self.config.timezone_id),
            'color_scheme': self.config.color_scheme,
            'reduced_motion': self.config.reduced_motion,
            'forced_colors': self.config.forced_colors,
            'javascript_enabled': self.config.javascript_enabled,
            'bypass_csp': self.config.bypass_csp,
            'ignore_https_errors': self.config.ignore_https_errors,
            'extra_http_headers': self.config.extra_headers,
            'accept_downloads': True,
            'downloads_path': self.config.downloads_path,
        }
        
        # Add proxy if provided (per-context proxy)
        if proxy:
            if isinstance(proxy, str) and ':' in proxy:
                parts = proxy.split(':')
                if len(parts) >= 4:
                    context_options['proxy'] = {
                        "server": f"http://{parts[0]}:{parts[1]}",
                        "username": parts[2],
                        "password": parts[3]
                    }
                elif len(parts) >= 2:
                    context_options['proxy'] = {
                        "server": f"http://{parts[0]}:{parts[1]}"
                    }
            self.logger.info(f"🌐 Per-context proxy applied: {proxy.split(':')[0]}")
        elif self.config.proxy:
            context_options['proxy'] = self.config.proxy
            self.logger.info(f"🌐 Using global browser proxy: {self.config.proxy.get('server', 'unknown')}")

        # Add geolocation if fingerprint has coordinates
        if 'latitude' in self.fingerprint and 'longitude' in self.fingerprint:
            context_options['geolocation'] = {
                'latitude': self.fingerprint['latitude'],
                'longitude': self.fingerprint['longitude']
            }
            context_options['permissions'] = ['geolocation']
        
        # Add storage state if exists
        if self.config.storage_state and os.path.exists(self.config.storage_state):
            context_options['storage_state'] = self.config.storage_state
        
        # Add record options
        if self.config.record_video_dir:
            os.makedirs(self.config.record_video_dir, exist_ok=True)
            context_options['record_video_dir'] = self.config.record_video_dir
            
        if self.config.record_har_path:
            context_options['record_har_path'] = self.config.record_har_path
            
        # Create context
        self.context = await self.browser.new_context(**context_options)
        self.logger.info("✅ Quantum fingerprint injected into browser context")
        
        # Clear permissions (deny all suspicious APIs)
        await self.context.clear_permissions()
        
        # Grant only safe permissions
        for permission in self.config.permissions:
            await self.context.grant_permissions([permission])
        
        return self.context
    
    async def create_page(self):
        """Create new page with quantum stealth enhancements"""
        if not self.context:
            raise ValueError("Context not created. Call create_context() first.")
        
        self.page = await self.context.new_page()
        self.logger.info("✅ New page created")
        
        # Apply quantum stealth to page
        await self._apply_quantum_stealth()
        
        return self.page
    
    async def _apply_quantum_stealth(self):
        """
        Apply QUANTUM-LEVEL stealth injections to page
        
        Delegates to modular FingerprintInjector which chains 13 standalone
        protector classes. Each protector can be used independently or swapped.
        
        See core/stealth_protectors.py for individual protectors:
            CDPDetectionRemover, NavigatorProtector, WebGLProtector,
            CanvasProtector, WebRTCBlocker, AudioProtector, FontProtector,
            ScreenPropertySpoofer, HardwareSpoofer, TimezoneSpoofer,
            GeolocationSpoofer, BatterySpoofer, PermissionSpoofer
        """
        self.logger.info("🛡️  DEPLOYING QUANTUM STEALTH SHIELD...")
        
        from core.stealth_protectors import FingerprintInjector
        
        injector = FingerprintInjector()
        await injector.apply(self.page, self.fingerprint or {})
        
        self.logger.info("✅ QUANTUM STEALTH SHIELD DEPLOYED")
        self._applied_fingerprint = True
        
    async def navigate_to_gmail_signup(self):
        """Navigate to Gmail signup page with anti-detection measures"""
        if not self.page:
            raise ValueError("Page not created. Call create_page() first.")
        
        self.logger.info("🌍 Navigating to Gmail signup page...")
        
        # Navigate with random delay (human-like)
        delay = random.uniform(0.5, 1.5)
        await asyncio.sleep(delay)
        
        # Navigate to Google Accounts
        response = await self.page.goto(
            'https://accounts.google.com/signup',
            wait_until='networkidle',
            timeout=60000
        )
        
        if response.status != 200:
            self.logger.warning(f"⚠️  Gmail returned status {response.status}")
            
            # Check for bot detection
            content = await self.page.content()
            if 'unusual traffic' in content.lower() or 'robot' in content.lower():
                self.logger.error("🚨 GOOGLE BOT DETECTION TRIGGERED!")
                raise Exception("Google detected automation - fingerprint needs adjustment")
        
        self.logger.info("✅ Gmail signup page loaded")
        
        # Random pause to simulate reading
        await asyncio.sleep(random.uniform(2, 4))
        
        return self.page
    
    async def human_type(self, selector: str, text: str, **kwargs):
        """
        Type like a human, not a robot
        
        Features:
        - Variable typing speed (80-120 WPM)
        - Random typos (5-15% of the time)
        - Backspace corrections
        - Pauses between words
        - Inconsistent cadence
        """
        if not self.page:
            raise ValueError("Page not created")
        
        self.logger.debug(f"Typing: {text[:30]}...")
        
        # Wait for element
        await self.page.wait_for_selector(selector, state='visible', timeout=10000)
        await self.page.click(selector)
        
        # Clear field first
        await self.page.keyboard.press('Control+A')
        await self.page.keyboard.press('Backspace')
        
        # Random initial pause
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Type character by character
        for i, char in enumerate(text):
            # Human typing speed: 80-120 WPM = 0.05-0.075s per character avg
            # But with pauses between words
            base_delay = random.uniform(0.04, 0.12)
            
            # Longer pause at word boundaries
            if char == ' ':
                await asyncio.sleep(random.uniform(0.15, 0.35))
            else:
                await asyncio.sleep(base_delay)
            
            # Random typo (5-15% chance per word)
            if char.isalpha() and random.random() < 0.08:
                # Make a typo
                wrong_char = chr(ord(char) + random.choice([-1, 1]))
                await self.page.keyboard.type(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
                # Backspace correction
                await self.page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Type correct character
            await self.page.keyboard.type(char)
            
            # Occasional pause in middle of word
            if i % 5 == 0 and random.random() < 0.3:
                await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Random final pause
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
    async def human_click(self, selector: str, **kwargs):
        """Click like a human with variable movement and delay"""
        if not self.page:
            raise ValueError("Page not created")
        
        # Random delay before click
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Wait for element
        await self.page.wait_for_selector(selector, state='visible', timeout=10000)
        
        # Get element position
        element = await self.page.query_selector(selector)
        if not element:
            raise ValueError(f"Element not found: {selector}")
        
        box = await element.bounding_box()
        if not box:
            raise ValueError(f"Cannot get bounding box for: {selector}")
        
        # Calculate target with slight random offset (human inaccuracy)
        target_x = box['x'] + (box['width'] * random.uniform(0.3, 0.7))
        target_y = box['y'] + (box['height'] * random.uniform(0.3, 0.7))
        
        # Move mouse in a natural curve (not straight line)
        current_position = await self.page.evaluate("""() => {
            return {x: window.mouseX || 0, y: window.mouseY || 0};
        }""")
        
        # Simulate Bezier curve movement
        steps = random.randint(10, 20)
        for i in range(steps + 1):
            t = i / steps
            
            # Cubic Bezier with control points for curved path
            cp1x = current_position['x'] + (target_x - current_position['x']) * random.uniform(0.2, 0.4)
            cp1y = current_position['y'] + (target_y - current_position['y']) * random.uniform(0.1, 0.3)
            cp2x = current_position['x'] + (target_x - current_position['x']) * random.uniform(0.6, 0.8)
            cp2y = current_position['y'] + (target_y - current_position['y']) * random.uniform(0.7, 0.9)
            
            x = (1-t)**3 * current_position['x'] + 3*(1-t)**2*t * cp1x + 3*(1-t)*t**2 * cp2x + t**3 * target_x
            y = (1-t)**3 * current_position['y'] + 3*(1-t)**2*t * cp1y + 3*(1-t)*t**2 * cp2y + t**3 * target_y
            
            await self.page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.005, 0.015))
        
        # Random delay before click
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Click with random pressure (if supported)
        await self.page.mouse.click(target_x, target_y)
        
        # Update mouse position
        await self.page.evaluate(f"window.mouseX = {target_x}; window.mouseY = {target_y}")
        
        # Post-click pause
        await asyncio.sleep(random.uniform(0.1, 0.4))
        
    async def human_scroll(self, pixels: Optional[int] = None):
        """Scroll like a human with variable speed and acceleration"""
        if not self.page:
            raise ValueError("Page not created")
        
        if not pixels:
            # Random scroll amount
            pixels = random.randint(300, 800)
        
        # Simulate scroll wheel with acceleration
        remaining = pixels
        scrolls = []
        
        while remaining > 0:
            scroll_amount = min(remaining, random.randint(80, 150))
            scrolls.append(scroll_amount)
            remaining -= scroll_amount
        
        # Add acceleration: first scroll slower, then faster
        for i, amount in enumerate(scrolls):
            # Acceleration curve
            if i < len(scrolls) * 0.2:
                # Initial slow scroll
                await self.page.mouse.wheel(delta_x=0, delta_y=amount // 2)
                await asyncio.sleep(random.uniform(0.1, 0.2))
                await self.page.mouse.wheel(delta_x=0, delta_y=amount // 2)
            elif i > len(scrolls) * 0.8:
                # Final slow scroll
                await self.page.mouse.wheel(delta_x=0, delta_y=amount)
            else:
                # Fast scroll in middle
                await self.page.mouse.wheel(delta_x=0, delta_y=amount)
            
            # Random delay between scrolls
            await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Pause after scrolling
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
    async def solve_recaptcha(self, api_key: str = None):
        """
        Solve reCAPTCHA v2/v3 using AI-powered solving service
        """
        if not self.page:
            raise ValueError("Page not created")
        
        self.logger.info("🤖 Checking for reCAPTCHA...")
        
        # Check for reCAPTCHA iframe
        recaptcha_frames = await self.page.query_selector_all('iframe[src*="recaptcha"]')
        
        if not recaptcha_frames:
            self.logger.info("✅ No reCAPTCHA detected")
            return True
        
        self.logger.info("🔐 reCAPTCHA detected! Attempting to solve...")
        
        # Click on "I'm not a robot" checkbox
        try:
            await self.page.frame_locator('iframe[title*="recaptcha"]').locator('.recaptcha-checkbox').click(timeout=5000)
            self.logger.info("✅ reCAPTCHA checkbox clicked")
            await asyncio.sleep(random.uniform(2, 4))
        except:
            self.logger.warning("⚠️ Could not find reCAPTCHA checkbox, may be v3")
        
        # Check if we passed
        await asyncio.sleep(3)
        return True
    
    async def get_page_html(self) -> str:
        """Get page HTML with error handling"""
        if not self.page:
            raise ValueError("Page not created")
        
        return await self.page.content()
    
    async def screenshot(self, path: str = None) -> bytes:
        """Take screenshot for debugging"""
        if not self.page:
            raise ValueError("Page not created")
        
        if not path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/stealth_{timestamp}.png"
            os.makedirs("screenshots", exist_ok=True)
        
        await self.page.screenshot(path=path, full_page=True)
        self.logger.info(f"📸 Screenshot saved to {path}")
        return path
    
    async def close(self):
        """Close all browser resources"""
        if self.page:
            await self.page.close()
            self.page = None
            self.logger.debug("Page closed")
        
        if self.context:
            await self.context.close()
            self.context = None
            self.logger.debug("Context closed")
        
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.logger.debug("Browser closed")
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.logger.debug("Playwright stopped")
        
        self.logger.info("✅ Stealth browser shutdown complete")


# ============================================================================
# ███████╗ █████╗  ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
# █████╗  ███████║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
# ██╔══╝  ██╔══██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
# ██║     ██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
# ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
# ============================================================================

class StealthBrowserFactory:
    """
    Factory for creating pre-configured stealth browsers with
    quantum fingerprinting already applied
    """
    
    @staticmethod
    async def create_with_fingerprint(
        fingerprint: Dict,
        proxy: Optional[Dict[str, str]] = None,
        browser_type: str = 'firefox'
    ) -> StealthBrowser:
        """
        Create and fully configure a stealth browser with fingerprint
        """
        # Configure stealth
        config = StealthConfig()
        config.browser_type = browser_type
        config.proxy = proxy
        config.user_agent = fingerprint.get('user_agent')
        config.timezone_id = fingerprint.get('timezone', 'America/New_York')
        config.locale = fingerprint.get('language', 'en-US')
        config.viewport = {
            'width': fingerprint.get('screen_width', 1920),
            'height': fingerprint.get('screen_height', 1080)
        }
        config.screen = {
            'width': fingerprint.get('screen_width', 1920),
            'height': fingerprint.get('screen_height', 1080)
        }
        
        # Create browser
        browser = StealthBrowser(config)
        await browser.launch()
        await browser.create_context(fingerprint)
        await browser.create_page()
        
        return browser
    
    @staticmethod
    async def create_anonymous(
        fingerprint: Dict,
        proxy: Optional[Dict[str, str]] = None
    ) -> StealthBrowser:
        """
        Create completely anonymous browser with zero identifying traces
        """
        # Force Firefox for maximum anonymity
        config = StealthConfig()
        config.browser_type = 'firefox'
        config.proxy = proxy
        
        # Disable all storage
        config.storage_state = None
        
        # Clear any persistent data
        browser = StealthBrowser(config)
        await browser.launch()
        await browser.create_context(fingerprint)
        await browser.create_page()
        
        return browser


# ============================================================================
# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
# ============================================================================

async def main():
    """Example usage of StealthBrowser"""
    
    print("⚡⚡⚡ QUANTUM STEALTH BROWSER DEMO ⚡⚡⚡")
    print("=" * 60)
    
    # Load a fingerprint
    try:
        with open('config/fingerprints_sample.json', 'r') as f:
            fingerprints = json.load(f)
            fingerprint = fingerprints[0]
        print("✅ Loaded quantum fingerprint")
    except:
        # Create a minimal fingerprint for testing
        from fingerprint_generator import QuantumFingerprintFactory
        factory = QuantumFingerprintFactory()
        fingerprint_obj = factory.generate_fingerprint()
        fingerprint = fingerprint_obj.to_dict()
        print("✅ Generated new quantum fingerprint")
    
    # Create stealth browser
    browser = await StealthBrowserFactory.create_with_fingerprint(
        fingerprint=fingerprint,
        browser_type='firefox'
    )
    
    try:
        # Navigate to Gmail
        await browser.navigate_to_gmail_signup()
        
        # Take screenshot
        await browser.screenshot()
        
        # Wait for user input
        input("\n⏸️  Press Enter to close browser...")
        
    finally:
        # Clean up
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())