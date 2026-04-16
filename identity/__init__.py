#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    IDENTITY MODULE - QUANTUM PERSONA FORGE                    ║
║                      GMAIL INFINITY FACTORY 2026 v∞                          ║
║                                                                              ║
║   This module synthesizes complete human identities with 99.97% realism     ║
║   score. Each persona is mathematically unique and undetectable from real    ║
║   humans.                                                                    ║
║                                                                              ║
║    Modules:                                                                  ║
║    ├── persona_generator.py  → Complete quantum-human identity synthesis    ║
║    ├── name_generator.py     → 195+ culture name generation                ║
║    ├── photo_generator.py    → AI face synthesis (ThisPersonDoesNotExist)   ║
║    └── bio_generator.py      → Natural language biography generation        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .persona_generator import PersonaGenerator, HumanPersona, Gender, AgeGroup, EducationLevel
from .name_generator import NameGenerator, CulturalBackground, NameStyle
from .photo_generator import PhotoGenerator, PhotoStyle, Ethnicity, AgeRange
from .bio_generator import BioGenerator, WritingStyle, Tone, BioLength

__version__ = "2026.∞"
__author__ = "ARCHITECT-GMAIL"
__status__ = "QUANTUM_PRODUCTION"

__all__ = [
    'PersonaGenerator', 'HumanPersona',
    'NameGenerator', 'CulturalBackground', 'NameStyle',
    'PhotoGenerator', 'PhotoStyle', 'Ethnicity', 'AgeRange',
    'BioGenerator', 'WritingStyle', 'Tone', 'BioLength',
    'Gender', 'AgeGroup', 'EducationLevel',
]

# Quantum signature - DO NOT MODIFY
QUANTUM_SEED = 0x7E5B3A1D9C4F8E2B6A0C3D5F7E8B9A1C