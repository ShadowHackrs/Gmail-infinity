#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 VERIFICATION MODULE - QUANTUM BYPASS ENGINE                  ║
║                    GMAIL INFINITY FACTORY 2026 - v∞                          ║
║                                                                              ║
║    Modules:                                                                  ║
║    ├── sms_providers.py     → Real SIM card rental (5sim, sms-activate)     ║
║    ├── email_recovery.py    → Temp mail automation with domain rotation     ║
║    ├── captcha_solver.py    → reCAPTCHA v2/v3/Audio solving                 ║
║    └── voice_verification.py → AI voice call handling (ElevenLabs/GPT-4o)   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .sms_providers import (
    FiveSimClient,
    SmsActivateClient,
    TextVerifiedClient,
    OnlineSimClient,
    SMSProviderFactory,
    PhoneNumber,
    SMSMessage,
)

from .email_recovery import (
    TempMailClient,
    MailTmClient,
    GuerrillaMailClient,
    TempMailFactory,
    EmailAccount,
    EmailMessage,
)

from .captcha_solver import (
    TwoCaptchaClient,
    AntiCaptchaClient,
    CapSolverClient,
    CaptchaSolverFactory,
    CaptchaType,
    CaptchaSolution,
)

# Voice verification has heavy dependencies (ElevenLabs, Twilio) — lazy import
try:
    from .voice_verification import *
except ImportError:
    pass

__all__ = [
    # SMS Providers
    'FiveSimClient', 'SmsActivateClient', 'TextVerifiedClient',
    'OnlineSimClient', 'SMSProviderFactory', 'PhoneNumber', 'SMSMessage',
    
    # Email Recovery
    'TempMailClient', 'MailTmClient', 'GuerrillaMailClient',
    'TempMailFactory', 'EmailAccount', 'EmailMessage',
    
    # Captcha Solvers
    'TwoCaptchaClient', 'AntiCaptchaClient', 'CapSolverClient',
    'CaptchaSolverFactory', 'CaptchaType', 'CaptchaSolution',
]

__version__ = '2026.∞.1'
__author__ = 'ARCHITECT-GMAIL'
__status__ = 'QUANTUM_PRODUCTION'