#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STEALTH_PROTECTORS.PY - v2026.∞                          ║
║              Standalone Modular Anti-Detection Protector Classes             ║
║                    Composable across any browser backend                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Each protector implements .apply(page, fingerprint) and can be used
independently or chained via FingerprintInjector.
"""

import logging
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

try:
    from playwright.async_api import Page
except ImportError:
    Page = None

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BaseProtector(ABC):
    """Abstract protector — all protectors implement .apply(page, fingerprint)"""
    
    @abstractmethod
    async def apply(self, page, fingerprint: Dict) -> None:
        raise NotImplementedError
    
    def _get(self, fp: Dict, key: str, default=None):
        """Safe fingerprint key access"""
        return fp.get(key, default)


# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATOR PROTECTOR — webdriver, plugins, mimeTypes, languages, platform
# ═══════════════════════════════════════════════════════════════════════════════

class NavigatorProtector(BaseProtector):
    """Remove all automation traces from navigator object"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        platform = self._get(fingerprint, 'platform', 'Win32')
        language = self._get(fingerprint, 'language', 'en-US')
        lang_short = language.split('-')[0] if '-' in language else language
        hw_concurrency = self._get(fingerprint, 'hardware_concurrency', 8)
        device_memory = self._get(fingerprint, 'device_memory', 16)
        
        await page.add_init_script(f"""
        // === NAVIGATOR PROTECTOR ===
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined, configurable: true
        }});
        
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;
        
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {{
                const p = {{
                    0: {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
                    1: {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' }},
                    2: {{ name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }},
                    length: 3,
                    item: function(i) {{ return this[i]; }},
                    namedItem: function(name) {{ for(let i=0;i<this.length;i++) if(this[i]&&this[i].name===name) return this[i]; return null; }},
                    refresh: function() {{}},
                }};
                p[Symbol.iterator] = function*() {{ for(let i=0;i<this.length;i++) yield this[i]; }};
                return p;
            }},
            configurable: true
        }});
        
        Object.defineProperty(navigator, 'mimeTypes', {{
            get: () => {{
                const m = {{
                    0: {{ type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: navigator.plugins[0] }},
                    1: {{ type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: navigator.plugins[0] }},
                    2: {{ type: 'application/x-nacl', suffixes: '', description: 'Native Client Executable', enabledPlugin: navigator.plugins[2] }},
                    3: {{ type: 'application/x-pnacl', suffixes: '', description: 'Portable Native Client Executable', enabledPlugin: navigator.plugins[2] }},
                    length: 4,
                    item: function(i) {{ return this[i]; }},
                    namedItem: function(name) {{ for(let i=0;i<this.length;i++) if(this[i]&&this[i].type===name) return this[i]; return null; }},
                }};
                m[Symbol.iterator] = function*() {{ for(let i=0;i<this.length;i++) yield this[i]; }};
                return m;
            }},
            configurable: true
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{language}', '{lang_short}'], configurable: true
        }});
        Object.defineProperty(navigator, 'language', {{
            get: () => '{language}', configurable: true
        }});
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{platform}', configurable: true
        }});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hw_concurrency}, configurable: true
        }});
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {device_memory}, configurable: true
        }});
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                effectiveType: '4g', rtt: 50, downlink: 10,
                saveData: false, type: 'wifi'
            }}),
            configurable: true
        }});
        
        // Override Notification permission
        if (window.Notification) {{
            window.Notification.permission = 'default';
            window.Notification.requestPermission = () => Promise.resolve('default');
        }}
        """)
        logger.debug("NavigatorProtector applied")


# ═══════════════════════════════════════════════════════════════════════════════
# WEBGL PROTECTOR — GPU vendor/renderer, WEBGL_debug_renderer_info
# ═══════════════════════════════════════════════════════════════════════════════

class WebGLProtector(BaseProtector):
    """Spoof WebGL vendor, renderer, and debug info extension"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        vendor = self._get(fingerprint, 'gpu_vendor', 'Intel Inc.')
        renderer = self._get(fingerprint, 'gpu_renderer', 'Intel Iris OpenGL Engine')
        
        await page.add_init_script(f"""
        // === WEBGL PROTECTOR ===
        const _wglParamProxy = {{
            apply: function(target, thisArg, args) {{
                const p = args[0];
                if (p === 37445) return '{vendor}';
                if (p === 37446) return '{renderer}';
                if (p === 7936) return 'WebKit';
                if (p === 7937) return 'WebKit WebGL';
                if (p === 3379) return 'WebGL 2.0 (OpenGL ES 3.0 Chromium)';
                return Reflect.apply(target, thisArg, args);
            }}
        }};
        
        const _debugInfoProxy = {{
            get: function(target, prop) {{
                if (prop === 'UNMASKED_VENDOR_WEBGL') return 37445;
                if (prop === 'UNMASKED_RENDERER_WEBGL') return 37446;
                return Reflect.get(target, prop);
            }}
        }};
        
        ['WebGLRenderingContext', 'WebGL2RenderingContext'].forEach(ctxName => {{
            if (!window[ctxName]) return;
            const proto = window[ctxName].prototype;
            proto.getParameter = new Proxy(proto.getParameter, _wglParamProxy);
            const origGetExt = proto.getExtension;
            proto.getExtension = new Proxy(origGetExt, {{
                apply: function(target, thisArg, args) {{
                    if (args[0] === 'WEBGL_debug_renderer_info')
                        return new Proxy({{}}, _debugInfoProxy);
                    return Reflect.apply(target, thisArg, args);
                }}
            }});
        }});
        """)
        logger.debug("WebGLProtector applied")


# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS PROTECTOR — toDataURL / getImageData noise injection
# ═══════════════════════════════════════════════════════════════════════════════

class CanvasProtector(BaseProtector):
    """Inject deterministic per-session noise into canvas operations"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        # Use fingerprint_id as seed for deterministic canvas noise
        seed = hash(self._get(fingerprint, 'fingerprint_id', '')) % 10000
        
        await page.add_init_script(f"""
        // === CANVAS PROTECTOR ===
        const _canvasSeed = {seed};
        const _noisify = function(r, g, b, a, x, y) {{
            const n = ((x * 0.001 + y * 0.002 + _canvasSeed * 0.0001) % 1);
            return {{
                r: Math.min(255, Math.max(0, r + Math.floor(n * 5 - 2))),
                g: Math.min(255, Math.max(0, g + Math.floor(n * 5 - 2))),
                b: Math.min(255, Math.max(0, b + Math.floor(n * 5 - 2))),
                a: a
            }};
        }};
        
        const _origGetCtx = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attrs) {{
            const ctx = _origGetCtx.call(this, type, attrs);
            if (ctx && type.includes('2d')) {{
                const _origGetImageData = ctx.getImageData;
                ctx.getImageData = function(sx, sy, sw, sh) {{
                    const data = _origGetImageData.call(this, sx, sy, sw, sh);
                    for (let i = 0; i < data.data.length; i += 4) {{
                        const px = _noisify(data.data[i], data.data[i+1], data.data[i+2], data.data[i+3],
                            sx + (i/4 % sw), sy + Math.floor((i/4) / sw));
                        data.data[i] = px.r; data.data[i+1] = px.g;
                        data.data[i+2] = px.b; data.data[i+3] = px.a;
                    }}
                    return data;
                }};
            }}
            return ctx;
        }};
        
        const _origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
            try {{
                const ctx = this.getContext('2d');
                if (ctx) {{
                    const imgData = ctx.getImageData(0, 0, this.width, this.height);
                    ctx.putImageData(imgData, 0, 0);
                }}
            }} catch(e) {{}}
            return _origToDataURL.call(this, type, quality);
        }};
        """)
        logger.debug("CanvasProtector applied")


# ═══════════════════════════════════════════════════════════════════════════════
# WEBRTC BLOCKER — prevent IP leak via RTCPeerConnection
# ═══════════════════════════════════════════════════════════════════════════════

class WebRTCBlocker(BaseProtector):
    """Block WebRTC IP leak by overriding RTCPeerConnection"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        await page.add_init_script("""
        // === WEBRTC BLOCKER ===
        const _fakeRTC = function() {
            return {
                createDataChannel: () => null,
                setLocalDescription: () => Promise.resolve(),
                setRemoteDescription: () => Promise.resolve(),
                createOffer: () => Promise.resolve({sdp: '', type: 'offer'}),
                createAnswer: () => Promise.resolve({sdp: '', type: 'answer'}),
                addIceCandidate: () => Promise.resolve(),
                close: () => {},
                addEventListener: () => {},
                removeEventListener: () => {},
                onicecandidate: null,
                onicegatheringstatechange: null,
                onsignalingstatechange: null,
                onconnectionstatechange: null,
                localDescription: null,
                remoteDescription: null,
                signalingState: 'closed',
                iceGatheringState: 'complete',
                connectionState: 'closed',
                iceConnectionState: 'closed',
            };
        };
        
        Object.defineProperty(window, 'RTCPeerConnection', {
            get: () => _fakeRTC, configurable: true, enumerable: true
        });
        if (window.webkitRTCPeerConnection)
            window.webkitRTCPeerConnection = _fakeRTC;
        if (window.mozRTCPeerConnection)
            window.mozRTCPeerConnection = _fakeRTC;
        
        if (navigator.mediaDevices) {
            navigator.mediaDevices.enumerateDevices = () => Promise.resolve([
                {deviceId: '', kind: 'audioinput', label: '', groupId: ''},
                {deviceId: '', kind: 'videoinput', label: '', groupId: ''},
                {deviceId: '', kind: 'audiooutput', label: '', groupId: ''},
            ]);
        }
        """)
        logger.debug("WebRTCBlocker applied")


# ═══════════════════════════════════════════════════════════════════════════════
# TIMEZONE SPOOFER — Intl.DateTimeFormat, Date.getTimezoneOffset
# ═══════════════════════════════════════════════════════════════════════════════

class TimezoneSpoofer(BaseProtector):
    """Override timezone detection to match fingerprint/proxy"""
    
    # IANA timezone → UTC offset in minutes (west-positive as per JS spec)
    TZ_OFFSETS = {
        'America/New_York': 300, 'America/Chicago': 360, 'America/Denver': 420,
        'America/Los_Angeles': 480, 'America/Anchorage': 540, 'Pacific/Honolulu': 600,
        'America/Toronto': 300, 'America/Winnipeg': 360, 'America/Vancouver': 480,
        'America/Sao_Paulo': 180, 'America/Argentina/Buenos_Aires': 180,
        'America/Mexico_City': 360, 'America/Bogota': 300, 'America/Lima': 300,
        'Europe/London': 0, 'Europe/Dublin': 0, 'Europe/Paris': -60,
        'Europe/Berlin': -60, 'Europe/Madrid': -60, 'Europe/Rome': -60,
        'Europe/Amsterdam': -60, 'Europe/Brussels': -60, 'Europe/Vienna': -60,
        'Europe/Zurich': -60, 'Europe/Stockholm': -60, 'Europe/Oslo': -60,
        'Europe/Copenhagen': -60, 'Europe/Helsinki': -120, 'Europe/Warsaw': -60,
        'Europe/Prague': -60, 'Europe/Bucharest': -120, 'Europe/Athens': -120,
        'Europe/Istanbul': -180, 'Europe/Moscow': -180, 'Europe/Kiev': -120,
        'Asia/Dubai': -240, 'Asia/Riyadh': -180, 'Asia/Tehran': -210,
        'Asia/Kolkata': -330, 'Asia/Colombo': -330, 'Asia/Dhaka': -360,
        'Asia/Bangkok': -420, 'Asia/Jakarta': -420, 'Asia/Singapore': -480,
        'Asia/Hong_Kong': -480, 'Asia/Taipei': -480, 'Asia/Shanghai': -480,
        'Asia/Seoul': -540, 'Asia/Tokyo': -540,
        'Australia/Perth': -480, 'Australia/Adelaide': -570,
        'Australia/Sydney': -600, 'Australia/Melbourne': -600,
        'Pacific/Auckland': -720, 'Pacific/Fiji': -720,
        'Africa/Cairo': -120, 'Africa/Lagos': -60, 'Africa/Nairobi': -180,
        'Africa/Johannesburg': -120, 'Africa/Casablanca': -60,
    }
    
    async def apply(self, page, fingerprint: Dict) -> None:
        tz = self._get(fingerprint, 'timezone', 'America/New_York')
        offset = self.TZ_OFFSETS.get(tz, 300)
        
        await page.add_init_script(f"""
        // === TIMEZONE SPOOFER ===
        const _origDTF = Intl.DateTimeFormat;
        Object.defineProperty(Intl, 'DateTimeFormat', {{
            value: function(locales, options) {{
                options = Object.assign({{}}, options || {{}});
                options.timeZone = '{tz}';
                return new _origDTF(locales, options);
            }},
            writable: true, configurable: true
        }});
        Intl.DateTimeFormat.supportedLocalesOf = _origDTF.supportedLocalesOf;
        
        Date.prototype.getTimezoneOffset = function() {{ return {offset}; }};
        
        // Spoof Intl.DateTimeFormat.resolvedOptions
        const _origResolved = _origDTF.prototype.resolvedOptions;
        _origDTF.prototype.resolvedOptions = function() {{
            const opts = _origResolved.call(this);
            opts.timeZone = '{tz}';
            return opts;
        }};
        """)
        logger.debug(f"TimezoneSpoofer applied: {tz} (offset={offset})")


# ═══════════════════════════════════════════════════════════════════════════════
# GEOLOCATION SPOOFER — navigator.geolocation override
# ═══════════════════════════════════════════════════════════════════════════════

class GeolocationSpoofer(BaseProtector):
    """Override navigator.geolocation to return proxy-matched coordinates"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        lat = self._get(fingerprint, 'latitude', 40.7128)
        lon = self._get(fingerprint, 'longitude', -74.0060)
        accuracy = self._get(fingerprint, 'geo_accuracy', 50)
        
        await page.add_init_script(f"""
        // === GEOLOCATION SPOOFER ===
        const _geoPos = {{
            coords: {{
                latitude: {lat}, longitude: {lon}, accuracy: {accuracy},
                altitude: null, altitudeAccuracy: null,
                heading: null, speed: null
            }},
            timestamp: Date.now()
        }};
        
        navigator.geolocation.getCurrentPosition = function(success, error, options) {{
            setTimeout(() => success(_geoPos), Math.random() * 500 + 100);
        }};
        navigator.geolocation.watchPosition = function(success, error, options) {{
            setTimeout(() => success(_geoPos), Math.random() * 500 + 100);
            return Math.floor(Math.random() * 1000);
        }};
        navigator.geolocation.clearWatch = function(id) {{}};
        """)
        logger.debug(f"GeolocationSpoofer applied: ({lat}, {lon})")


# ═══════════════════════════════════════════════════════════════════════════════
# FONT PROTECTOR — document.fonts, measureText noise
# ═══════════════════════════════════════════════════════════════════════════════

class FontProtector(BaseProtector):
    """Spoof font enumeration and measureText metrics"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        seed = hash(self._get(fingerprint, 'font_hash', '')) % 100000
        
        await page.add_init_script(f"""
        // === FONT PROTECTOR ===
        Object.defineProperty(document, 'fonts', {{
            get: function() {{
                return {{
                    ready: Promise.resolve(),
                    status: 'loaded',
                    check: function(font) {{ return true; }},
                    load: function() {{ return Promise.resolve([]); }},
                    forEach: function() {{}},
                    entries: function*() {{}},
                    keys: function*() {{}},
                    values: function*() {{}},
                    [Symbol.iterator]: function*() {{}},
                    size: 0,
                }};
            }},
            configurable: true
        }});
        
        const _origMeasure = CanvasRenderingContext2D.prototype.measureText;
        CanvasRenderingContext2D.prototype.measureText = function(text) {{
            const m = _origMeasure.call(this, text);
            const noise = (({seed} + text.length) % 100) * 0.0000001;
            Object.defineProperty(m, 'width', {{ value: m.width + noise }});
            return m;
        }};
        """)
        logger.debug("FontProtector applied")


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO PROTECTOR — OfflineAudioContext, AudioContext noise
# ═══════════════════════════════════════════════════════════════════════════════

class AudioProtector(BaseProtector):
    """Inject noise into AudioContext fingerprinting"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        seed = hash(self._get(fingerprint, 'audio_context_hash', '')) % 100000
        
        await page.add_init_script(f"""
        // === AUDIO PROTECTOR ===
        const _audioSeed = {seed};
        
        if (window.OfflineAudioContext) {{
            const _origRender = OfflineAudioContext.prototype.startRendering;
            OfflineAudioContext.prototype.startRendering = function() {{
                return _origRender.call(this).then(function(buffer) {{
                    if (buffer && buffer.getChannelData) {{
                        for (let ch = 0; ch < buffer.numberOfChannels; ch++) {{
                            const data = buffer.getChannelData(ch);
                            for (let i = 0; i < data.length; i += 100) {{
                                data[i] = data[i] * (1 + (_audioSeed % 10) * 0.0000001);
                            }}
                        }}
                    }}
                    return buffer;
                }});
            }};
        }}
        
        if (window.AudioContext) {{
            const _origOsc = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {{
                const osc = _origOsc.call(this);
                osc.frequency.value = osc.frequency.value * (1 + _audioSeed * 0.0000001);
                return osc;
            }};
        }}
        """)
        logger.debug("AudioProtector applied")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN PROPERTY SPOOFER
# ═══════════════════════════════════════════════════════════════════════════════

class ScreenPropertySpoofer(BaseProtector):
    """Spoof window.screen, devicePixelRatio"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        w = self._get(fingerprint, 'screen_width', 1920)
        h = self._get(fingerprint, 'screen_height', 1080)
        depth = self._get(fingerprint, 'screen_depth', 24)
        ratio = self._get(fingerprint, 'screen_pixel_ratio', 1.0)
        
        await page.add_init_script(f"""
        // === SCREEN PROPERTY SPOOFER ===
        Object.defineProperty(window, 'screen', {{
            get: () => ({{
                width: {w}, height: {h}, availWidth: {w}, availHeight: {h - 40},
                colorDepth: {depth}, pixelDepth: {depth}, availLeft: 0, availTop: 0,
                orientation: {{ type: 'landscape-primary', angle: 0 }}
            }}),
            configurable: true
        }});
        Object.defineProperty(window, 'devicePixelRatio', {{
            get: () => {ratio}, configurable: true
        }});
        Object.defineProperty(window, 'innerWidth', {{
            get: () => {w}, configurable: true
        }});
        Object.defineProperty(window, 'outerWidth', {{
            get: () => {w}, configurable: true
        }});
        Object.defineProperty(window, 'innerHeight', {{
            get: () => {h - 80}, configurable: true
        }});
        Object.defineProperty(window, 'outerHeight', {{
            get: () => {h}, configurable: true
        }});
        """)
        logger.debug(f"ScreenPropertySpoofer applied: {w}x{h}")


# ═══════════════════════════════════════════════════════════════════════════════
# CDP DETECTION REMOVER — webdriver flags, selenium, phantom, etc.
# ═══════════════════════════════════════════════════════════════════════════════

class CDPDetectionRemover(BaseProtector):
    """Remove Chrome DevTools Protocol and automation framework detection markers"""
    
    MARKERS = [
        'cdc', '__webdriver_evaluate', '__selenium_evaluate',
        '__webdriver_script_function', '__webdriver_script_func',
        '__webdriver_script_fn', '__fxdriver_evaluate',
        '__driver_unwrapped', '__webdriver_unwrapped',
        'callPhantom', '_phantom', 'phantom', '__phantomas',
        '_selenium', 'calledSelenium', '_Selenium_IDE_Recorder',
        '__webdriverFunc', '__lastWatirAlert', '__lastWatirConfirm',
        '__lastWatirPrompt', '__nightmareError', 'domAutomation',
        'domAutomationController',
    ]
    
    async def apply(self, page, fingerprint: Dict) -> None:
        script_lines = ["// === CDP DETECTION REMOVER ==="]
        for marker in self.MARKERS:
            script_lines.append(f"try {{ delete window.{marker}; }} catch(e) {{}}")
            script_lines.append(f"try {{ window.{marker} = undefined; }} catch(e) {{}}")
        
        # Chrome runtime injection
        script_lines.append("""
        if (window.chrome) {
            window.chrome.runtime = undefined;
            window.chrome.loadTimes = function(){};
            window.chrome.csi = function(){};
            window.chrome.app = undefined;
            window.chrome.webstore = undefined;
        }
        """)
        
        await page.add_init_script("\n".join(script_lines))
        logger.debug("CDPDetectionRemover applied")


# ═══════════════════════════════════════════════════════════════════════════════
# BATTERY SPOOFER
# ═══════════════════════════════════════════════════════════════════════════════

class BatterySpoofer(BaseProtector):
    """Spoof navigator.getBattery with realistic values"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        import random
        level = round(random.uniform(0.45, 0.98), 2)
        charging = random.choice(['true', 'false'])
        
        await page.add_init_script(f"""
        // === BATTERY SPOOFER ===
        if (navigator.getBattery) {{
            navigator.getBattery = () => Promise.resolve({{
                charging: {charging}, chargingTime: {charging} ? 0 : Infinity,
                dischargingTime: {charging} ? Infinity : {random.randint(3600, 18000)},
                level: {level},
                onchargingchange: null, onchargingtimechange: null,
                ondischargingtimechange: null, onlevelchange: null
            }});
        }}
        """)
        logger.debug(f"BatterySpoofer applied: level={level}")


# ═══════════════════════════════════════════════════════════════════════════════
# PERMISSION SPOOFER
# ═══════════════════════════════════════════════════════════════════════════════

class PermissionSpoofer(BaseProtector):
    """Override navigator.permissions.query to return realistic states"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        await page.add_init_script("""
        // === PERMISSION SPOOFER ===
        if (navigator.permissions) {
            const _origQuery = navigator.permissions.query;
            navigator.permissions.query = function(descriptor) {
                const promptPerms = ['notifications', 'geolocation', 'camera', 
                    'microphone', 'midi', 'background-sync'];
                if (promptPerms.includes(descriptor.name)) {
                    return Promise.resolve({
                        state: 'prompt', 
                        onchange: null,
                        addEventListener: function(){},
                        removeEventListener: function(){},
                    });
                }
                return _origQuery.call(this, descriptor).catch(() => ({
                    state: 'prompt', onchange: null,
                    addEventListener: function(){},
                    removeEventListener: function(){},
                }));
            };
        }
        
        // Gamepad API
        if (navigator.getGamepads) {
            navigator.getGamepads = () => [null, null, null, null];
        }
        """)
        logger.debug("PermissionSpoofer applied")


# ═══════════════════════════════════════════════════════════════════════════════
# HARDWARE SPOOFER (standalone, mirrors NavigatorProtector but for hardware only)
# ═══════════════════════════════════════════════════════════════════════════════

class HardwareSpoofer(BaseProtector):
    """Spoof hardware-related navigator properties independently"""
    
    async def apply(self, page, fingerprint: Dict) -> None:
        hw = self._get(fingerprint, 'hardware_concurrency', 8)
        mem = self._get(fingerprint, 'device_memory', 16)
        max_touch = self._get(fingerprint, 'max_touch_points', 0)
        
        await page.add_init_script(f"""
        // === HARDWARE SPOOFER ===
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hw}, configurable: true
        }});
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {mem}, configurable: true
        }});
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: () => {max_touch}, configurable: true
        }});
        """)
        logger.debug(f"HardwareSpoofer applied: cores={hw}, ram={mem}GB")


# ═══════════════════════════════════════════════════════════════════════════════
# FINGERPRINT INJECTOR — Master orchestrator, chains all protectors
# ═══════════════════════════════════════════════════════════════════════════════

class FingerprintInjector:
    """
    Master orchestrator — chains all stealth protectors in correct order.
    
    Usage:
        injector = FingerprintInjector()
        await injector.apply(page, fingerprint_dict)
    
    Or selectively:
        injector = FingerprintInjector(protectors=[WebGLProtector(), CanvasProtector()])
        await injector.apply(page, fingerprint_dict)
    """
    
    # Default execution order — dependencies and overrides matter
    DEFAULT_PROTECTORS = [
        CDPDetectionRemover,      # 1. Remove automation flags FIRST
        NavigatorProtector,       # 2. Core navigator overrides
        WebGLProtector,           # 3. GPU fingerprint
        CanvasProtector,          # 4. Canvas fingerprint
        WebRTCBlocker,            # 5. Prevent IP leak
        AudioProtector,           # 6. Audio fingerprint
        FontProtector,            # 7. Font fingerprint
        ScreenPropertySpoofer,    # 8. Screen/viewport
        HardwareSpoofer,          # 9. Hardware properties
        TimezoneSpoofer,          # 10. Timezone
        GeolocationSpoofer,       # 11. Geolocation
        BatterySpoofer,           # 12. Battery API
        PermissionSpoofer,        # 13. Permissions (last)
    ]
    
    def __init__(self, protectors: Optional[List[BaseProtector]] = None):
        if protectors is not None:
            self._protectors = protectors
        else:
            self._protectors = [cls() for cls in self.DEFAULT_PROTECTORS]
    
    async def apply(self, page, fingerprint: Dict) -> None:
        """Apply all protectors in sequence"""
        logger.info(f"🛡️  FingerprintInjector: applying {len(self._protectors)} protectors...")
        
        for protector in self._protectors:
            try:
                await protector.apply(page, fingerprint)
            except Exception as e:
                logger.error(f"❌ {protector.__class__.__name__} failed: {e}")
        
        logger.info("✅ All stealth protectors deployed")
    
    def add_protector(self, protector: BaseProtector, index: int = -1):
        """Add a custom protector at a specific position"""
        if index == -1:
            self._protectors.append(protector)
        else:
            self._protectors.insert(index, protector)
    
    def remove_protector(self, protector_class: type):
        """Remove a protector by class type"""
        self._protectors = [p for p in self._protectors if not isinstance(p, protector_class)]


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'BaseProtector',
    'FingerprintInjector',
    'WebGLProtector',
    'CanvasProtector',
    'WebRTCBlocker',
    'TimezoneSpoofer',
    'GeolocationSpoofer',
    'FontProtector',
    'AudioProtector',
    'ScreenPropertySpoofer',
    'HardwareSpoofer',
    'NavigatorProtector',
    'CDPDetectionRemover',
    'BatterySpoofer',
    'PermissionSpoofer',
]
