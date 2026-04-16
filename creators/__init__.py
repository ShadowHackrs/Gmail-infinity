#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GMAIL CREATORS MODULE - v2026.∞                          ║
║                  Quantum Account Factory - All Methods                       ║
║                                                                              ║
║    Modules:                                                                  ║
║    ├── web_creator.py           → Playwright + stealth web signup           ║
║    ├── android_creator.py       → ADB-based Android emulator signup         ║
║    ├── workspace_creator.py     → Google Workspace Admin SDK signup          ║
║    └── recovery_link_creator.py → Family Link child account creation        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# Lazy imports — each creator has heavy optional dependencies
def _import_web_creator():
    from .web_creator import WebGmailCreator, GmailAccount
    return WebGmailCreator, GmailAccount

def _import_android_creator():
    from .android_creator import AndroidEmulatorCreator
    return AndroidEmulatorCreator

def _import_workspace_creator():
    from .workspace_creator import GoogleWorkspaceCreator
    return GoogleWorkspaceCreator

def _import_family_link_creator():
    from .recovery_link_creator import FamilyLinkCreator
    return FamilyLinkCreator

# Try importing — gracefully skip if deps missing
try:
    from .web_creator import WebGmailCreator, GmailAccount
except ImportError as e:
    WebGmailCreator = None
    GmailAccount = None

try:
    from .android_creator import AndroidEmulatorCreator
except ImportError as e:
    AndroidEmulatorCreator = None

try:
    from .workspace_creator import GoogleWorkspaceCreator
except ImportError as e:
    GoogleWorkspaceCreator = None

try:
    from .recovery_link_creator import FamilyLinkCreator
except ImportError as e:
    FamilyLinkCreator = None

__all__ = [
    'WebGmailCreator',
    'GmailAccount',
    'AndroidEmulatorCreator',
    'GoogleWorkspaceCreator',
    'FamilyLinkCreator',
]

__version__ = '2026.∞-quantum'
__author__ = 'ARCHITECT-GMAIL'
__status__ = 'Production'