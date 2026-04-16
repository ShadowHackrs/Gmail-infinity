#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PERSONA_GENERATOR.PY - v2026.∞                            ║
║                  Quantum Human Profile Synthesis Engine                      ║
║              Generates Undetectable Digital Identities with                  ║
║              Full Life History, Cultural Context, and Psychological Depth    ║
╚══════════════════════════════════════════════════════════════════════════════╝

██╗██████╗ ███████╗███╗   ██╗████████╗██╗████████╗██╗   ██╗
██║██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██║╚══██╔══╝╚██╗ ██╔╝
██║██║  ██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║    ╚████╔╝ 
██║██║  ██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║     ╚██╔╝  
██║██████╔╝███████╗██║ ╚████║   ██║   ██║   ██║      ██║   
╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝   ╚═╝      ╚═╝   
"""

import random
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
from faker import Faker
from faker.providers import internet, person, date_time, phone_number, address, job, lorem, ssn, credit_card, company, profile
import pytz
import re

# Initialize Faker with multiple locales for global coverage
fake_en = Faker('en_US')
fake_gb = Faker('en_GB')
fake_ca = Faker('en_CA')
fake_au = Faker('en_AU')
fake_de = Faker('de_DE')
fake_fr = Faker('fr_FR')
fake_es = Faker('es_ES')
fake_it = Faker('it_IT')
fake_nl = Faker('nl_NL')
fake_jp = Faker('ja_JP')
fake_cn = Faker('zh_CN')
fake_ru = Faker('ru_RU')
fake_br = Faker('pt_BR')
fake_mx = Faker('es_MX')
fake_in = Faker('hi_IN')
fake_ar = Faker('ar_SA')
fake_il = Faker('he_IL')
fake_tr = Faker('tr_TR')
fake_pl = Faker('pl_PL')
fake_se = Faker('sv_SE')
fake_no = Faker('no_NO')
fake_dk = Faker('da_DK')
fake_fi = Faker('fi_FI')

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"

class AgeGroup(Enum):
    GEN_Z = (16, 25)      # 1999-2008
    MILLENNIAL = (26, 41) # 1983-1998
    GEN_X = (42, 57)      # 1965-1982
    BOOMER = (58, 76)     # 1946-1964

class EducationLevel(Enum):
    HIGH_SCHOOL = "high_school"
    SOME_COLLEGE = "some_college"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"

class MaritalStatus(Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    DOMESTIC_PARTNERSHIP = "domestic_partnership"

class EmploymentStatus(Enum):
    EMPLOYED_FULL_TIME = "employed_full_time"
    EMPLOYED_PART_TIME = "employed_part_time"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    RETIRED = "retired"
    HOMEMAKER = "homemaker"

class IncomeBracket(Enum):
    UNDER_25K = "under_25k"
    _25K_50K = "25k_50k"
    _50K_75K = "50k_75k"
    _75K_100K = "75k_100k"
    _100K_150K = "100k_150k"
    _150K_250K = "150k_250k"
    OVER_250K = "over_250k"

class PersonalityTrait(Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"
    # HEXACO model additions
    HONESTY_HUMILITY = "honesty_humility"
    EMOTIONALITY = "emotionality"
    EXTRAVERSION_HEXACO = "extraversion_hexaco"
    AGREEABLENESS_HEXACO = "agreeableness_hexaco"
    CONSCIENTIOUSNESS_HEXACO = "conscientiousness_hexaco"
    OPENNESS_HEXACO = "openness_hexaco"

class Interest(Enum):
    TECHNOLOGY = "technology"
    GAMING = "gaming"
    SPORTS = "sports"
    FITNESS = "fitness"
    MUSIC = "music"
    MOVIES = "movies"
    TV = "tv"
    BOOKS = "books"
    TRAVEL = "travel"
    FOOD = "food"
    COOKING = "cooking"
    FASHION = "fashion"
    ART = "art"
    PHOTOGRAPHY = "photography"
    DIY = "diy"
    GARDENING = "gardening"
    PETS = "pets"
    NATURE = "nature"
    SCIENCE = "science"
    HISTORY = "history"
    POLITICS = "politics"
    NEWS = "news"
    FINANCE = "finance"
    INVESTING = "investing"
    CRYPTO = "crypto"
    BUSINESS = "business"
    MARKETING = "marketing"
    DESIGN = "design"
    WRITING = "writing"
    LANGUAGES = "languages"
    VOLUNTEERING = "volunteering"
    RELIGION = "religion"
    SPIRITUALITY = "spirituality"
    PARENTING = "parenting"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    WELLNESS = "wellness"
    MENTAL_HEALTH = "mental_health"
    MEDICINE = "medicine"
    LAW = "law"
    ENGINEERING = "engineering"
    ARCHITECTURE = "architecture"
    EDUCATION = "education"
    CAREER = "career"

class Religion(Enum):
    CHRISTIANITY = "christianity"
    ISLAM = "islam"
    HINDUISM = "hinduism"
    BUDDHISM = "buddhism"
    JUDAISM = "judaism"
    SIKHISM = "sikhism"
    JAINISM = "jainism"
    BAHAI = "bahai"
    ATHEISM = "atheism"
    AGNOSTICISM = "agnosticism"
    SPIRITUAL_BUT_NOT_RELIGIOUS = "spiritual_but_not_religious"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class PoliticalLeaning(Enum):
    FAR_LEFT = "far_left"
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    FAR_RIGHT = "far_right"
    LIBERTARIAN = "libertarian"
    APOLITICAL = "apolitical"
    OTHER = "other"

# ============================================================================
# DATA CLASSES - QUANTUM HUMAN BLUEPRINTS
# ============================================================================

@dataclass
class GeoLocation:
    """Geographic location with cultural context"""
    country_code: str = ""
    country: str = ""
    city: str = ""
    state: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""
    region: str = ""
    metro_area: Optional[str] = None
    neighborhood: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class NameComponents:
    """Full name with cultural variations"""
    first_name: str = ""
    last_name: str = ""
    middle_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    nickname: Optional[str] = None
    display_name: str = ""
    full_name: str = ""
    
    def __post_init__(self):
        if not self.full_name:
            parts = []
            if self.prefix:
                parts.append(self.prefix)
            parts.append(self.first_name)
            if self.middle_name:
                parts.append(self.middle_name)
            parts.append(self.last_name)
            if self.suffix:
                parts.append(self.suffix)
            self.full_name = " ".join(parts)
        
        if not self.display_name:
            self.display_name = self.nickname or self.first_name

@dataclass
class DateComponents:
    """Temporal identity markers"""
    date_of_birth: str = ""
    age: int = 0
    birth_year: int = 0
    birth_month: int = 1
    birth_day: int = 1
    zodiac_sign: str = ""
    chinese_zodiac: Optional[str] = None
    generation: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ContactInfo:
    """Contact details with platform preferences"""
    email: str = ""
    phone: str = ""
    phone_country_code: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""
    address2: Optional[str] = None
    
    # Alternative contact methods
    secondary_email: Optional[str] = None
    work_email: Optional[str] = None
    work_phone: Optional[str] = None
    
    # Social media presence
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    tiktok: Optional[str] = None
    snapchat: Optional[str] = None
    discord: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    signal: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Education:
    """Educational background"""
    level: EducationLevel
    institution: str
    field: str
    start_year: int
    end_year: int
    graduated: bool = True
    gpa: Optional[float] = None
    degree: Optional[str] = None
    
    # Additional educational experiences
    high_school: Optional[str] = None
    high_school_year: Optional[int] = None
    certifications: List[str] = field(default_factory=list)
    online_courses: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['level'] = self.level.value
        return data

@dataclass
class Employment:
    """Employment history"""
    status: EmploymentStatus
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = True
    
    # Compensation
    salary: Optional[int] = None
    salary_bracket: Optional[IncomeBracket] = None
    
    # Remote/office
    remote_percentage: int = 0
    office_location: Optional[str] = None
    
    # Employment history
    previous_companies: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        if self.salary_bracket:
            data['salary_bracket'] = self.salary_bracket.value
        return data

@dataclass
class Family:
    """Family relationships"""
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    spouse_name: Optional[str] = None
    children: int = 0
    children_names: List[str] = field(default_factory=list)
    parents: Dict[str, str] = field(default_factory=dict)  # relation: name
    siblings: List[str] = field(default_factory=list)
    pets: List[Dict[str, str]] = field(default_factory=list)  # type, name
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['marital_status'] = self.marital_status.value
        return data

@dataclass
class Lifestyle:
    """Personal lifestyle preferences"""
    interests: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    sports: List[str] = field(default_factory=list)
    music_genres: List[str] = field(default_factory=list)
    movie_genres: List[str] = field(default_factory=list)
    tv_genres: List[str] = field(default_factory=list)
    book_genres: List[str] = field(default_factory=list)
    
    # Diet and health
    diet: str = "omnivore"
    smoker: bool = False
    drinker: bool = False
    exercise_frequency: str = "sometimes"
    
    # Digital life
    social_media_usage: str = "moderate"
    primary_device: str = "smartphone"
    preferred_browser: str = "chrome"
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Personality:
    """Psychological profile"""
    mbti: str = ""  # Myers-Briggs Type Indicator
    big_five: Dict[str, float] = field(default_factory=dict)  # OCEAN scores (0-100)
    hexaco: Dict[str, float] = field(default_factory=dict)  # HEXACO scores (0-100)
    enneagram: str = ""  # Enneagram type
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Beliefs:
    """Personal beliefs and worldview"""
    religion: str = ""
    religiosity: int = 0  # 0-100
    political_leaning: str = ""
    political_engagement: int = 0  # 0-100
    environmentalism: int = 0  # 0-100
    social_liberalism: int = 0  # 0-100
    economic_conservatism: int = 0  # 0-100
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['religion'] = self.religion.value if isinstance(self.religion, Enum) else self.religion
        data['political_leaning'] = self.political_leaning.value if isinstance(self.political_leaning, Enum) else self.political_leaning
        return data

@dataclass
class DigitalFootprint:
    """Simulated digital presence"""
    email_aliases: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    passwords_hash: str = ""  # Not actual passwords, just hash for consistency
    account_creation_date: str = ""
    last_active: str = ""
    
    # Platform presence
    google_services: List[str] = field(default_factory=list)  # Gmail, Drive, Photos, etc.
    social_media_accounts: List[str] = field(default_factory=list)
    
    # Behavioral patterns
    typical_login_hours: List[int] = field(default_factory=list)  # 0-23
    typical_login_days: List[int] = field(default_factory=list)  # 0-6, Monday=0
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class HumanPersona:
    """Complete quantum-human identity"""
    # Core identity
    persona_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Name components
    name: NameComponents = field(default_factory=NameComponents)
    
    # Demographics
    gender: str = ""
    date_info: DateComponents = field(default_factory=DateComponents)
    
    # Location
    location: GeoLocation = field(default_factory=GeoLocation)
    
    # Contact
    contact: ContactInfo = field(default_factory=ContactInfo)
    
    # Life stages
    education: List[Education] = field(default_factory=list)
    employment: List[Employment] = field(default_factory=list)
    current_employment: Optional[Employment] = None
    
    # Personal life
    family: Family = field(default_factory=Family)
    lifestyle: Lifestyle = field(default_factory=Lifestyle)
    
    # Psychology
    personality: Personality = field(default_factory=Personality)
    beliefs: Beliefs = field(default_factory=Beliefs)
    
    # Digital
    digital: DigitalFootprint = field(default_factory=DigitalFootprint)
    
    # Metadata
    profile_completeness: float = 1.0
    version: str = "2026.∞"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary for serialization"""
        data = {
            'persona_id': self.persona_id,
            'created_at': self.created_at,
            'gender': self.gender,
            'name': self.name.to_dict() if hasattr(self.name, 'to_dict') else asdict(self.name),
            'date_info': self.date_info.to_dict() if hasattr(self.date_info, 'to_dict') else asdict(self.date_info),
            'location': self.location.to_dict() if hasattr(self.location, 'to_dict') else asdict(self.location),
            'contact': self.contact.to_dict() if hasattr(self.contact, 'to_dict') else asdict(self.contact),
            'education': [e.to_dict() if hasattr(e, 'to_dict') else asdict(e) for e in self.education],
            'employment': [e.to_dict() if hasattr(e, 'to_dict') else asdict(e) for e in self.employment],
            'current_employment': self.current_employment.to_dict() if self.current_employment and hasattr(self.current_employment, 'to_dict') else (asdict(self.current_employment) if self.current_employment else None),
            'family': self.family.to_dict() if hasattr(self.family, 'to_dict') else asdict(self.family),
            'lifestyle': self.lifestyle.to_dict() if hasattr(self.lifestyle, 'to_dict') else asdict(self.lifestyle),
            'personality': self.personality.to_dict() if hasattr(self.personality, 'to_dict') else asdict(self.personality),
            'beliefs': self.beliefs.to_dict() if hasattr(self.beliefs, 'to_dict') else asdict(self.beliefs),
            'digital': self.digital.to_dict() if hasattr(self.digital, 'to_dict') else asdict(self.digital),
            'profile_completeness': self.profile_completeness,
            'version': self.version
        }
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HumanPersona':
        """Create persona from dictionary"""
        persona = cls()
        for key, value in data.items():
            if hasattr(persona, key):
                setattr(persona, key, value)
        return persona


# ============================================================================
# QUANTUM PERSONA GENERATOR ENGINE
# ============================================================================

class PersonaGenerator:
    """
    Quantum Human Synthesis Engine
    Generates statistically accurate, undetectable digital human identities
    with complete life history, cultural context, and psychological depth.
    
    Each persona is mathematically unique and passes all statistical tests
    for realistic human demographics.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the persona forge"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        self.generated_personas = set()
        self.persona_count = 0
        
        # Country-specific Faker instances
        self.fakers = {
            'US': fake_en,
            'GB': fake_gb,
            'CA': fake_ca,
            'AU': fake_au,
            'DE': fake_de,
            'FR': fake_fr,
            'ES': fake_es,
            'IT': fake_it,
            'NL': fake_nl,
            'JP': fake_jp,
            'CN': fake_cn,
            'RU': fake_ru,
            'BR': fake_br,
            'MX': fake_mx,
            'IN': fake_in,
            'SA': fake_ar,
            'AE': fake_ar,
            'IL': fake_il,
            'TR': fake_tr,
            'PL': fake_pl,
            'SE': fake_se,
            'NO': fake_no,
            'DK': fake_dk,
            'FI': fake_fi,
        }
        
        # Country demographics for weighted selection
        self.country_weights = {
            'US': 0.18,  # 18% of personas
            'CN': 0.14,  # 14%
            'IN': 0.12,  # 12%
            'BR': 0.06,  # 6%
            'GB': 0.05,  # 5%
            'DE': 0.05,  # 5%
            'FR': 0.04,  # 4%
            'JP': 0.04,  # 4%
            'RU': 0.04,  # 4%
            'MX': 0.03,  # 3%
            'IT': 0.03,  # 3%
            'CA': 0.03,  # 3%
            'ES': 0.02,  # 2%
            'AU': 0.02,  # 2%
            'NL': 0.02,  # 2%
            'TR': 0.02,  # 2%
            'PL': 0.02,  # 2%
            'SA': 0.01,  # 1%
            'AE': 0.01,  # 1%
            'SE': 0.01,  # 1%
            'NO': 0.01,  # 1%
            'DK': 0.01,  # 1%
            'FI': 0.01,  # 1%
            'IL': 0.01,  # 1%
        }
        
        # Zodiac signs
        self.zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Chinese zodiac
        self.chinese_zodiac = [
            'Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
            'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig'
        ]
        
        # MBTI distributions (approximate real-world percentages)
        self.mbti_distributions = [
            ('ISTJ', 11.6), ('ISFJ', 13.8), ('INFJ', 1.5), ('INTJ', 2.1),
            ('ISTP', 5.4), ('ISFP', 8.8), ('INFP', 4.4), ('INTP', 3.3),
            ('ESTP', 4.3), ('ESFP', 8.5), ('ENFP', 8.1), ('ENTP', 3.2),
            ('ESTJ', 8.7), ('ESFJ', 12.3), ('ENFJ', 2.5), ('ENTJ', 1.8)
        ]
        self.mbti_types = [m[0] for m in self.mbti_distributions]
        self.mbti_weights = [m[1] for m in self.mbti_distributions]
        
        # Enneagram distributions
        self.enneagram_types = [
            '1w2', '1w9', '2w1', '2w3', '3w2', '3w4', '4w3', '4w5',
            '5w4', '5w6', '6w5', '6w7', '7w6', '7w8', '8w7', '8w9',
            '9w1', '9w8'
        ]
        
        # Common first names by country (simplified, would be huge in production)
        self.popular_names = {
            'US': {'male': ['James', 'Robert', 'John', 'Michael', 'David', 'William', 'Richard', 'Joseph', 'Thomas', 'Christopher'],
                   'female': ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']},
            'GB': {'male': ['Oliver', 'George', 'Harry', 'Noah', 'Jack', 'Leo', 'Oscar', 'Charlie', 'Jacob', 'Freddie'],
                   'female': ['Olivia', 'Amelia', 'Isla', 'Ava', 'Emily', 'Mia', 'Isabella', 'Ella', 'Lily', 'Grace']},
            'DE': {'male': ['Maximilian', 'Alexander', 'Paul', 'Ben', 'Lukas', 'Jonas', 'Leon', 'Felix', 'Tim', 'David'],
                   'female': ['Mia', 'Emma', 'Hannah', 'Sophia', 'Anna', 'Lea', 'Lina', 'Marie', 'Lena', 'Emilia']},
            'FR': {'male': ['Gabriel', 'Raphaël', 'Louis', 'Léo', 'Jules', 'Hugo', 'Adam', 'Lucas', 'Ethan', 'Arthur'],
                   'female': ['Emma', 'Jade', 'Louise', 'Alice', 'Chloé', 'Lina', 'Rose', 'Anna', 'Mila', 'Léa']},
            'JP': {'male': ['Haruto', 'Sota', 'Yuito', 'Haruki', 'Minato', 'Riku', 'Yuma', 'Itsuki', 'Sora', 'Hinata'],
                   'female': ['Yui', 'Himari', 'Sakura', 'Rin', 'Akari', 'Mei', 'Hina', 'Miu', 'Ichika', 'Koharu']},
        }
        
        # Common last names by country
        self.popular_last_names = {
            'US': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'],
            'GB': ['Smith', 'Jones', 'Williams', 'Taylor', 'Brown', 'Davies', 'Evans', 'Wilson', 'Thomas', 'Roberts'],
            'DE': ['Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann'],
            'FR': ['Martin', 'Bernard', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Dubois', 'Moreau', 'Laurent'],
            'JP': ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi', 'Saito'],
        }
    
    @staticmethod
    def _normalize_weights(weights):
        """Normalize probability weights to sum to exactly 1.0 (fixes numpy precision issues)"""
        w = np.array(weights, dtype=np.float64)
        return w / w.sum()
    
    def _select_country(self) -> Tuple[str, Faker]:
        """Select random country based on real-world population weights"""
        countries = list(self.country_weights.keys())
        weights = self._normalize_weights(list(self.country_weights.values()))
        country = np.random.choice(countries, p=weights)
        return country, self.fakers.get(country, fake_en)
    
    def _generate_name(self, country: str, gender: str, faker: Faker) -> NameComponents:
        """Generate culturally appropriate name"""
        name = NameComponents()
        
        # First name
        if country in self.popular_names and gender in self.popular_names[country]:
            name.first_name = random.choice(self.popular_names[country][gender])
        else:
            if gender == 'male':
                name.first_name = faker.first_name_male()
            elif gender == 'female':
                name.first_name = faker.first_name_female()
            else:
                name.first_name = faker.first_name()
        
        # Last name
        if country in self.popular_last_names:
            name.last_name = random.choice(self.popular_last_names[country])
        else:
            name.last_name = faker.last_name()
        
        # Middle name (30% chance)
        if random.random() < 0.3:
            name.middle_name = faker.first_name()
        
        # Prefix (5% chance for titles)
        if random.random() < 0.05:
            prefixes = ['Dr.', 'Prof.', 'Rev.']
            name.prefix = random.choice(prefixes)
        
        # Suffix (3% chance for Jr., Sr., III, etc.)
        if random.random() < 0.03:
            suffixes = ['Jr.', 'Sr.', 'II', 'III', 'IV', 'PhD', 'MD', 'Esq.']
            name.suffix = random.choice(suffixes)
        
        # Nickname (40% chance)
        if random.random() < 0.4:
            name.nickname = name.first_name[:random.randint(3, 6)]
        
        # Generate display and full names
        name.display_name = name.nickname or name.first_name
        name.full_name = " ".join(filter(None, [
            name.prefix,
            name.first_name,
            name.middle_name,
            name.last_name,
            name.suffix
        ]))
        
        return name
    
    def _generate_date_of_birth(self, age_group: Optional[AgeGroup] = None) -> DateComponents:
        """Generate realistic date of birth"""
        if age_group:
            age_range = age_group.value
            age = random.randint(age_range[0], age_range[1])
        else:
            # Age 16-76 with realistic distribution
            age_weights = [0.08] * 10 + [0.12] * 15 + [0.15] * 15 + [0.12] * 15 + [0.08] * 11
            age = np.random.choice(range(16, 77), p=self._normalize_weights(age_weights[:61]))
        
        today = datetime.now()
        birth_year = today.year - age
        
        # Adjust for birthdays already passed this year
        birth_month = random.randint(1, 12)
        if birth_month > today.month:
            birth_year -= 1
            age -= 1
        
        # Generate valid day for month
        if birth_month == 2:
            birth_day = random.randint(1, 29 if (birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0)) else 28)
        elif birth_month in [4, 6, 9, 11]:
            birth_day = random.randint(1, 30)
        else:
            birth_day = random.randint(1, 31)
        
        date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Determine zodiac sign
        zodiac_index = 0
        if (birth_month == 3 and birth_day >= 21) or (birth_month == 4 and birth_day <= 19):
            zodiac_index = 0  # Aries
        elif (birth_month == 4 and birth_day >= 20) or (birth_month == 5 and birth_day <= 20):
            zodiac_index = 1  # Taurus
        elif (birth_month == 5 and birth_day >= 21) or (birth_month == 6 and birth_day <= 20):
            zodiac_index = 2  # Gemini
        elif (birth_month == 6 and birth_day >= 21) or (birth_month == 7 and birth_day <= 22):
            zodiac_index = 3  # Cancer
        elif (birth_month == 7 and birth_day >= 23) or (birth_month == 8 and birth_day <= 22):
            zodiac_index = 4  # Leo
        elif (birth_month == 8 and birth_day >= 23) or (birth_month == 9 and birth_day <= 22):
            zodiac_index = 5  # Virgo
        elif (birth_month == 9 and birth_day >= 23) or (birth_month == 10 and birth_day <= 22):
            zodiac_index = 6  # Libra
        elif (birth_month == 10 and birth_day >= 23) or (birth_month == 11 and birth_day <= 21):
            zodiac_index = 7  # Scorpio
        elif (birth_month == 11 and birth_day >= 22) or (birth_month == 12 and birth_day <= 21):
            zodiac_index = 8  # Sagittarius
        elif (birth_month == 12 and birth_day >= 22) or (birth_month == 1 and birth_day <= 19):
            zodiac_index = 9  # Capricorn
        elif (birth_month == 1 and birth_day >= 20) or (birth_month == 2 and birth_day <= 18):
            zodiac_index = 10  # Aquarius
        else:
            zodiac_index = 11  # Pisces
        
        zodiac_sign = self.zodiac_signs[zodiac_index]
        
        # Chinese zodiac
        chinese_zodiac = self.chinese_zodiac[birth_year % 12]
        
        # Generation
        if age <= 25:
            generation = "Gen Z"
        elif age <= 41:
            generation = "Millennial"
        elif age <= 57:
            generation = "Gen X"
        else:
            generation = "Boomer"
        
        return DateComponents(
            date_of_birth=date_of_birth,
            age=age,
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            zodiac_sign=zodiac_sign,
            chinese_zodiac=chinese_zodiac,
            generation=generation
        )
    
    def _generate_location(self, country: str, faker: Faker) -> GeoLocation:
        """Generate realistic location data"""
        # Get city and state from faker
        if country == 'US':
            state = faker.state()
            state_code = faker.state_abbr()
            city = faker.city()
            postal_code = faker.zipcode()
        else:
            state = None
            state_code = None
            city = faker.city()
            postal_code = faker.postcode()
        
        # Get country name
        country_name = {
            'US': 'United States', 'GB': 'United Kingdom', 'CA': 'Canada',
            'AU': 'Australia', 'DE': 'Germany', 'FR': 'France',
            'ES': 'Spain', 'IT': 'Italy', 'NL': 'Netherlands',
            'JP': 'Japan', 'CN': 'China', 'RU': 'Russia',
            'BR': 'Brazil', 'MX': 'Mexico', 'IN': 'India',
            'SA': 'Saudi Arabia', 'AE': 'United Arab Emirates',
            'IL': 'Israel', 'TR': 'Turkey', 'PL': 'Poland',
            'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark',
            'FI': 'Finland'
        }.get(country, country)
        
        # Get coordinates (simplified)
        latitude = float(faker.latitude())
        longitude = float(faker.longitude())
        
        # Determine timezone
        timezones = {
            'US': ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles', 'America/Phoenix'],
            'GB': ['Europe/London'],
            'DE': ['Europe/Berlin'],
            'FR': ['Europe/Paris'],
            'JP': ['Asia/Tokyo'],
            'CN': ['Asia/Shanghai'],
            'IN': ['Asia/Kolkata'],
            'AU': ['Australia/Sydney', 'Australia/Melbourne', 'Australia/Brisbane', 'Australia/Perth'],
            'BR': ['America/Sao_Paulo'],
            'CA': ['America/Toronto', 'America/Vancouver'],
            'RU': ['Europe/Moscow'],
        }
        
        timezone = random.choice(timezones.get(country, ['UTC']))
        
        # Region and metro area
        regions = {
            'US': ['Northeast', 'Midwest', 'South', 'West'],
            'CA': ['West Coast', 'Prairie', 'Central', 'Atlantic'],
            'GB': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
        }
        region = random.choice(regions.get(country, ['Unknown']))
        
        return GeoLocation(
            country_code=country,
            country=country_name,
            city=city,
            state=state,
            state_code=state_code,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            region=region
        )
    
    def _generate_contact_info(self, persona: HumanPersona, faker: Faker) -> ContactInfo:
        """Generate contact information"""
        name = persona.name
        location = persona.location
        
        # Generate email
        email_providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'protonmail.com']
        
        # Common email patterns
        email_patterns = [
            f"{name.first_name.lower()}.{name.last_name.lower()}",
            f"{name.first_name.lower()}{name.last_name.lower()[:1]}",
            f"{name.first_name.lower()[:1]}.{name.last_name.lower()}",
            f"{name.first_name.lower()}{name.last_name.lower()}",
            f"{name.first_name.lower()}{random.randint(10, 99)}",
            f"{name.nickname.lower() if name.nickname else name.first_name.lower()}.{name.last_name.lower()}",
        ]
        
        email_local = random.choice(email_patterns)
        email = f"{email_local}@{random.choice(email_providers)}"
        
        # Generate phone number
        phone_country_codes = {
            'US': '+1', 'CA': '+1', 'GB': '+44', 'DE': '+49', 'FR': '+33',
            'JP': '+81', 'CN': '+86', 'IN': '+91', 'AU': '+61', 'BR': '+55',
            'MX': '+52', 'IT': '+39', 'ES': '+34', 'NL': '+31', 'RU': '+7',
            'SA': '+966', 'AE': '+971', 'IL': '+972', 'TR': '+90', 'PL': '+48',
            'SE': '+46', 'NO': '+47', 'DK': '+45', 'FI': '+358'
        }
        country_code = phone_country_codes.get(location.country_code, '+1')
        phone = faker.phone_number()
        
        # Generate address
        if location.country_code == 'US':
            address = f"{faker.street_address()}"
            address2 = f"Apt {random.randint(1, 50)}" if random.random() < 0.3 else None
            city = location.city
            state = location.state_code or location.state
            zip_code = location.postal_code
        else:
            address = faker.street_address()
            address2 = None
            city = location.city
            state = location.state or ''
            zip_code = location.postal_code
        
        # Generate social media handles
        def generate_handle():
            base = name.first_name.lower()
            if random.random() < 0.3:
                base += f".{name.last_name.lower()}"
            if random.random() < 0.2:
                base += str(random.randint(1, 99))
            return base
        
        social_media = {}
        if random.random() < 0.7:
            social_media['facebook'] = generate_handle()
        if random.random() < 0.8:
            social_media['instagram'] = generate_handle()
        if random.random() < 0.4:
            social_media['twitter'] = f"@{generate_handle()}"
        if random.random() < 0.6 and persona.date_info.age > 22:
            social_media['linkedin'] = f"in/{name.first_name.lower()}-{name.last_name.lower()}-{random.randint(1000000, 9999999)}"
        if random.random() < 0.5 and persona.date_info.age < 35:
            social_media['tiktok'] = f"@{generate_handle()}"
        if random.random() < 0.3:
            social_media['discord'] = f"{name.first_name.lower()}#{random.randint(1000, 9999)}"
        
        return ContactInfo(
            email=email,
            phone=phone,
            phone_country_code=country_code,
            address=address,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            country=location.country,
            **social_media
        )
    
    def _generate_education(self, persona: HumanPersona, faker: Faker) -> List[Education]:
        """Generate educational background"""
        age = persona.date_info.age
        current_year = datetime.now().year
        birth_year = persona.date_info.birth_year
        
        education_list = []
        
        # High school (everyone)
        hs_graduation_year = birth_year + 18
        if hs_graduation_year <= current_year:
            hs_name = f"{random.choice(['Central', 'North', 'South', 'East', 'West', 'Lincoln', 'Washington', 'Jefferson'])} High School"
            education_list.append(Education(
                level=EducationLevel.HIGH_SCHOOL,
                institution=hs_name,
                field="General Studies",
                start_year=hs_graduation_year - 4,
                end_year=hs_graduation_year,
                graduated=True,
                degree="High School Diploma"
            ))
        
        # Higher education (age-dependent)
        if age >= 22:
            # Determine education level based on age and random chance
            if age >= 26 and random.random() < 0.3:
                # Postgraduate
                edu_level = random.choice([EducationLevel.MASTER, EducationLevel.DOCTORATE, EducationLevel.PROFESSIONAL])
                years = 6 if edu_level == EducationLevel.DOCTORATE else 2
                start_year = hs_graduation_year + 4
                end_year = start_year + years
                graduated = random.random() < 0.9
            elif random.random() < 0.7:
                # Bachelor's
                edu_level = EducationLevel.BACHELOR
                start_year = hs_graduation_year
                end_year = start_year + 4
                graduated = random.random() < 0.85
            else:
                # Associate or Some college
                edu_level = random.choice([EducationLevel.ASSOCIATE, EducationLevel.SOME_COLLEGE])
                if edu_level == EducationLevel.ASSOCIATE:
                    start_year = hs_graduation_year
                    end_year = start_year + 2
                    graduated = random.random() < 0.8
                else:
                    start_year = hs_graduation_year
                    end_year = start_year + random.randint(1, 3)
                    graduated = False
            
            # University names
            unis = {
                'US': ['State University', 'University', 'College'],
                'GB': ['University', 'College London', 'Institute'],
                'DE': ['Universität', 'Hochschule'],
                'FR': ['Université', 'École'],
                'JP': ['University', 'Institute of Technology'],
            }
            
            suffix = unis.get(persona.location.country_code, ['University'])[0]
            
            if persona.location.country_code == 'US':
                uni_name = f"{random.choice(['Stanford', 'Harvard', 'MIT', 'UC Berkeley', 'University of Michigan', 'NYU', 'Columbia', 'Yale', 'Princeton', 'UCLA'])}"
            elif persona.location.country_code == 'GB':
                uni_name = f"{random.choice(['Oxford', 'Cambridge', 'Imperial College', 'UCL', 'LSE', 'University of Edinburgh'])}"
            else:
                uni_name = f"{faker.city()} {suffix}"
            
            # Fields of study
            fields = {
                'technology': ['Computer Science', 'Information Technology', 'Software Engineering', 'Data Science', 'Cybersecurity'],
                'business': ['Business Administration', 'Finance', 'Marketing', 'Economics', 'Accounting'],
                'health': ['Medicine', 'Nursing', 'Pharmacy', 'Dentistry', 'Public Health'],
                'science': ['Biology', 'Chemistry', 'Physics', 'Mathematics', 'Statistics'],
                'engineering': ['Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering', 'Chemical Engineering'],
                'humanities': ['English', 'History', 'Philosophy', 'Psychology', 'Sociology'],
                'arts': ['Fine Arts', 'Graphic Design', 'Architecture', 'Music', 'Film'],
                'law': ['Law', 'Criminal Justice', 'Legal Studies'],
                'education': ['Education', 'Teaching'],
            }
            
            # Pick field based on personality? Simplified for now
            field_category = random.choice(list(fields.keys()))
            field = random.choice(fields[field_category])
            
            # GPA (only if graduated)
            gpa = None
            if graduated:
                gpa = round(random.uniform(2.0, 4.0), 2)
            
            education_list.append(Education(
                level=edu_level,
                institution=uni_name,
                field=field,
                start_year=start_year,
                end_year=end_year,
                graduated=graduated if 'graduated' in locals() else True,
                gpa=gpa,
                degree=f"{edu_level.value.title()} in {field}"
            ))
        
        return education_list
    
    def _generate_employment(self, persona: HumanPersona, faker: Faker) -> Tuple[List[Employment], Optional[Employment]]:
        """Generate employment history"""
        age = persona.date_info.age
        current_year = datetime.now().year
        education = persona.education
        
        employment_list = []
        current_employment = None
        
        # Determine if in school, retired, etc.
        if age < 18:
            # Too young to work
            return employment_list, None
        elif age < 22:
            # Student or part-time
            if random.random() < 0.5:
                status = EmploymentStatus.STUDENT
            else:
                status = EmploymentStatus.EMPLOYED_PART_TIME
        elif age > 65:
            # Retired
            if random.random() < 0.7:
                status = EmploymentStatus.RETIRED
            else:
                status = EmploymentStatus.EMPLOYED_PART_TIME
        else:
            # Working age
            status_weights = [0.6, 0.1, 0.15, 0.05, 0.05, 0.05]
            status = np.random.choice(
                [EmploymentStatus.EMPLOYED_FULL_TIME, EmploymentStatus.EMPLOYED_PART_TIME,
                 EmploymentStatus.SELF_EMPLOYED, EmploymentStatus.UNEMPLOYED,
                 EmploymentStatus.HOMEMAKER, EmploymentStatus.STUDENT],
                p=status_weights
            )
        
        # Industries and job titles
        industries = {
            'Technology': ['Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer', 'DevOps Engineer', 'IT Manager'],
            'Healthcare': ['Doctor', 'Nurse', 'Pharmacist', 'Medical Assistant', 'Physical Therapist', 'Dentist'],
            'Finance': ['Financial Analyst', 'Accountant', 'Investment Banker', 'Financial Advisor', 'Auditor'],
            'Education': ['Teacher', 'Professor', 'School Administrator', 'Librarian', 'Guidance Counselor'],
            'Retail': ['Store Manager', 'Sales Associate', 'Cashier', 'Merchandiser', 'Buyer'],
            'Manufacturing': ['Production Manager', 'Quality Control', 'Machine Operator', 'Supply Chain Coordinator'],
            'Construction': ['Project Manager', 'Architect', 'Electrician', 'Carpenter', 'Civil Engineer'],
            'Transportation': ['Truck Driver', 'Logistics Coordinator', 'Dispatcher', 'Fleet Manager'],
            'Hospitality': ['Hotel Manager', 'Chef', 'Restaurant Manager', 'Event Planner', 'Bartender'],
            'Media': ['Journalist', 'Editor', 'Content Creator', 'Social Media Manager', 'Video Producer'],
            'Legal': ['Lawyer', 'Paralegal', 'Legal Assistant', 'Judge', 'Mediator'],
            'Marketing': ['Marketing Manager', 'SEO Specialist', 'Brand Manager', 'Copywriter', 'PR Specialist'],
            'Real Estate': ['Real Estate Agent', 'Property Manager', 'Appraiser', 'Mortgage Broker'],
            'Consulting': ['Management Consultant', 'Business Analyst', 'Strategy Consultant'],
            'Government': ['Policy Analyst', 'Administrator', 'Inspector', 'Social Worker'],
            'Nonprofit': ['Program Director', 'Fundraiser', 'Grant Writer', 'Community Organizer'],
            'Arts': ['Artist', 'Musician', 'Actor', 'Writer', 'Photographer'],
        }
        
        # Determine if person has a career field based on education
        career_field = None
        job_title = None
        
        if education:
            # Try to match education to career
            edu_field = education[-1].field if education else None
            for industry, titles in industries.items():
                if edu_field and any(keyword in edu_field for keyword in ['Computer', 'Software', 'Data', 'IT']):
                    career_field = 'Technology'
                    break
                elif edu_field and any(keyword in edu_field for keyword in ['Business', 'Finance', 'Marketing', 'Economics']):
                    career_field = random.choice(['Finance', 'Marketing', 'Consulting'])
                    break
                elif edu_field and any(keyword in edu_field for keyword in ['Medicine', 'Nursing', 'Health', 'Pharmacy']):
                    career_field = 'Healthcare'
                    break
                # ... more matching logic
        
        if not career_field:
            career_field = random.choice(list(industries.keys()))
        
        if status in [EmploymentStatus.EMPLOYED_FULL_TIME, EmploymentStatus.EMPLOYED_PART_TIME, EmploymentStatus.SELF_EMPLOYED]:
            job_title = random.choice(industries[career_field])
            
            # Company names
            company_types = ['Inc', 'LLC', 'Corp', 'Ltd', 'Group', 'Solutions', 'Technologies', 'Consulting']
            
            if persona.location.country_code == 'US':
                company = f"{random.choice(['Tech', 'Global', 'American', 'United', 'First', 'National', 'Premier', 'Advanced'])} {random.choice(['Solutions', 'Group', 'Partners', 'Systems', 'Services', 'Industries'])} {random.choice(company_types)}"
            else:
                company = f"{faker.company()}"
            
            # Start date
            start_year = max(persona.date_info.birth_year + 22, current_year - random.randint(1, min(10, current_year - (persona.date_info.birth_year + 18))))
            start_month = random.randint(1, 12)
            start_date = f"{start_year}-{start_month:02d}-01"
            
            # Salary based on job and experience
            experience_years = current_year - start_year
            
            if career_field == 'Technology':
                base_salary = random.randint(65000, 150000)
            elif career_field in ['Finance', 'Legal', 'Consulting']:
                base_salary = random.randint(60000, 140000)
            elif career_field in ['Healthcare', 'Engineering']:
                base_salary = random.randint(55000, 130000)
            elif career_field in ['Education', 'Nonprofit']:
                base_salary = random.randint(40000, 80000)
            else:
                base_salary = random.randint(35000, 90000)
            
            salary = base_salary + (experience_years * random.randint(1000, 3000))
            
            # Salary bracket
            if salary < 25000:
                bracket = IncomeBracket.UNDER_25K
            elif salary < 50000:
                bracket = IncomeBracket._25K_50K
            elif salary < 75000:
                bracket = IncomeBracket._50K_75K
            elif salary < 100000:
                bracket = IncomeBracket._75K_100K
            elif salary < 150000:
                bracket = IncomeBracket._100K_150K
            elif salary < 250000:
                bracket = IncomeBracket._150K_250K
            else:
                bracket = IncomeBracket.OVER_250K
            
            # Remote percentage (post-2020 trends)
            remote_percentage = 0
            if career_field in ['Technology', 'Marketing', 'Consulting']:
                remote_weights = [0.3, 0.2, 0.2, 0.3]  # 30% full remote, 20% hybrid 2-3 days, etc.
                remote_percentage = np.random.choice([100, 60, 40, 0], p=self._normalize_weights(remote_weights))
            elif career_field in ['Finance', 'Legal']:
                remote_weights = [0.1, 0.2, 0.3, 0.4]
                remote_percentage = np.random.choice([100, 40, 20, 0], p=self._normalize_weights(remote_weights))
            
            current_employment = Employment(
                status=status,
                company=company,
                title=job_title,
                industry=career_field,
                start_date=start_date,
                current=True,
                salary=salary,
                salary_bracket=bracket,
                remote_percentage=remote_percentage,
                office_location=persona.location.city if remote_percentage < 100 else None
            )
            
            employment_list.append(current_employment)
            
            # Previous jobs (for older workers)
            if age > 30 and random.random() < 0.6:
                prev_jobs_count = random.randint(1, 3)
                for i in range(prev_jobs_count):
                    prev_start = start_year - random.randint(2, 5) * (i + 1)
                    prev_end = start_year - random.randint(1, 2)
                    
                    prev_company = f"{random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])} {random.choice(['& Co', 'Associates', 'Partners', 'Group'])}"
                    prev_title = random.choice(industries.get(career_field, ['Associate', 'Assistant', 'Coordinator']))
                    
                    employment_list.append(Employment(
                        status=EmploymentStatus.EMPLOYED_FULL_TIME,
                        company=prev_company,
                        title=prev_title,
                        industry=career_field,
                        start_date=f"{prev_start}-01-01",
                        end_date=f"{prev_end}-12-31",
                        current=False,
                        salary=salary - random.randint(10000, 30000)
                    ))
        
        elif status == EmploymentStatus.UNEMPLOYED:
            # Unemployed, but may have worked before
            if age > 22 and random.random() < 0.7:
                # Had a job before
                prev_job = Employment(
                    status=EmploymentStatus.EMPLOYED_FULL_TIME,
                    company=faker.company(),
                    title=random.choice(industries[random.choice(list(industries.keys()))]),
                    industry=random.choice(list(industries.keys())),
                    start_date=f"{current_year - random.randint(2, 5)}-01-01",
                    end_date=f"{current_year - 1}-12-31",
                    current=False
                )
                employment_list.append(prev_job)
        
        return employment_list, current_employment
    
    def _generate_family(self, persona: HumanPersona, faker: Faker) -> Family:
        """Generate family information"""
        age = persona.date_info.age
        
        # Marital status based on age
        if age < 25:
            status_weights = [0.8, 0.15, 0.03, 0.01, 0.01]
        elif age < 35:
            status_weights = [0.4, 0.5, 0.05, 0.03, 0.02]
        elif age < 50:
            status_weights = [0.2, 0.6, 0.1, 0.05, 0.05]
        elif age < 65:
            status_weights = [0.15, 0.6, 0.1, 0.1, 0.05]
        else:
            status_weights = [0.1, 0.5, 0.1, 0.25, 0.05]
        
        marital_status = np.random.choice(
            [MaritalStatus.SINGLE, MaritalStatus.MARRIED, MaritalStatus.DIVORCED,
             MaritalStatus.WIDOWED, MaritalStatus.DOMESTIC_PARTNERSHIP],
            p=status_weights
        )
        
        spouse_name = None
        if marital_status in [MaritalStatus.MARRIED, MaritalStatus.DOMESTIC_PARTNERSHIP]:
            # Generate spouse name (opposite gender usually, but not always)
            if persona.gender == 'male':
                spouse_gender = 'female'
            elif persona.gender == 'female':
                spouse_gender = 'male'
            else:
                spouse_gender = random.choice(['male', 'female'])
            
            # Get spouse first name
            country = persona.location.country_code
            if country in self.popular_names and spouse_gender in self.popular_names[country]:
                spouse_first = random.choice(self.popular_names[country][spouse_gender])
            else:
                if spouse_gender == 'male':
                    spouse_first = faker.first_name_male()
                else:
                    spouse_first = faker.first_name_female()
            
            spouse_name = f"{spouse_first} {persona.name.last_name}"
        
        # Children (based on age and marital status)
        children_count = 0
        children_names = []
        
        if age >= 25 and marital_status in [MaritalStatus.MARRIED, MaritalStatus.DOMESTIC_PARTNERSHIP]:
            # Probability of having children increases with age up to a point
            if age < 30:
                child_prob = 0.3
                max_children = 2
            elif age < 40:
                child_prob = 0.7
                max_children = 3
            elif age < 50:
                child_prob = 0.8
                max_children = 4
            else:
                child_prob = 0.9
                max_children = 5
            
            if random.random() < child_prob:
                children_count = random.randint(1, max_children)
                
                # Generate children names
                for _ in range(children_count):
                    child_gender = random.choice(['male', 'female'])
                    country = persona.location.country_code
                    
                    if country in self.popular_names and child_gender in self.popular_names[country]:
                        child_name = random.choice(self.popular_names[country][child_gender])
                    else:
                        child_name = faker.first_name()
                    
                    children_names.append(child_name)
        
        # Pets (50% chance)
        pets = []
        if random.random() < 0.5:
            pet_count = random.randint(1, 3)
            pet_types = ['Dog', 'Cat', 'Bird', 'Fish', 'Hamster', 'Rabbit', 'Guinea Pig']
            
            for _ in range(pet_count):
                pet_type = random.choice(pet_types)
                pet_name = faker.first_name()
                pets.append({'type': pet_type, 'name': pet_name})
        
        # Parents (basic info)
        parents = {}
        if random.random() < 0.8:  # 80% have mother info
            mother_first = random.choice(self.popular_names.get(persona.location.country_code, {}).get('female', ['Mary', 'Patricia']))
            parents['mother'] = f"{mother_first} {persona.name.last_name}"
        
        if random.random() < 0.7:  # 70% have father info
            father_first = random.choice(self.popular_names.get(persona.location.country_code, {}).get('male', ['John', 'James']))
            parents['father'] = f"{father_first} {persona.name.last_name}"
        
        return Family(
            marital_status=marital_status,
            spouse_name=spouse_name,
            children=children_count,
            children_names=children_names,
            parents=parents,
            pets=pets
        )
    
    def _generate_lifestyle(self, persona: HumanPersona) -> Lifestyle:
        """Generate lifestyle preferences"""
        age = persona.date_info.age
        gender = persona.gender
        
        lifestyle = Lifestyle()
        
        # Interests (6-12 interests)
        all_interests = [i.value for i in Interest]
        
        # Age-based interest weighting
        if age < 30:
            weights = {
                'gaming': 0.7, 'fitness': 0.6, 'technology': 0.7,
                'music': 0.8, 'movies': 0.7, 'fashion': 0.6,
                'travel': 0.5, 'food': 0.6
            }
        elif age < 50:
            weights = {
                'career': 0.7, 'fitness': 0.6, 'parenting': 0.5,
                'cooking': 0.6, 'travel': 0.6, 'finance': 0.5,
                'diy': 0.5, 'gardening': 0.4
            }
        else:
            weights = {
                'gardening': 0.7, 'cooking': 0.6, 'travel': 0.6,
                'books': 0.7, 'history': 0.6, 'politics': 0.5,
                'health': 0.6, 'wellness': 0.5
            }
        
        interest_count = random.randint(8, 15)
        selected_interests = []
        
        for _ in range(interest_count):
            interest = random.choice(all_interests)
            
            # Apply age weighting
            if interest in weights and random.random() < weights[interest]:
                selected_interests.append(interest)
            elif interest not in weights:
                selected_interests.append(interest)
            
            # Remove duplicates while preserving order
            selected_interests = list(dict.fromkeys(selected_interests))
            if len(selected_interests) >= interest_count:
                break
        
        lifestyle.interests = selected_interests[:interest_count]
        
        # Diet preferences
        diets = ['omnivore', 'vegetarian', 'vegan', 'pescatarian', 'keto', 'paleo']
        diet_weights = [0.65, 0.15, 0.05, 0.05, 0.05, 0.05]
        lifestyle.diet = np.random.choice(diets, p=self._normalize_weights(diet_weights))
        
        # Smoking (declining among younger generations)
        if age < 30:
            lifestyle.smoker = random.random() < 0.08
        elif age < 50:
            lifestyle.smoker = random.random() < 0.12
        else:
            lifestyle.smoker = random.random() < 0.15
        
        # Drinking
        lifestyle.drinker = random.random() < 0.65
        
        # Exercise
        exercise_freq = ['never', 'rarely', 'sometimes', 'regularly', 'daily']
        if age < 30:
            ex_weights = [0.1, 0.2, 0.3, 0.3, 0.1]
        elif age < 50:
            ex_weights = [0.1, 0.2, 0.35, 0.25, 0.1]
        else:
            ex_weights = [0.15, 0.25, 0.3, 0.2, 0.1]
        
        lifestyle.exercise_frequency = np.random.choice(exercise_freq, p=self._normalize_weights(ex_weights))
        
        # Digital life
        social_usage = ['minimal', 'light', 'moderate', 'heavy', 'addicted']
        if age < 25:
            social_weights = [0.05, 0.15, 0.3, 0.35, 0.15]
        elif age < 40:
            social_weights = [0.1, 0.2, 0.4, 0.25, 0.05]
        else:
            social_weights = [0.2, 0.3, 0.35, 0.15, 0.0]
        
        lifestyle.social_media_usage = np.random.choice(social_usage, p=self._normalize_weights(social_weights))
        
        # Primary device
        if age < 30:
            device_weights = [0.7, 0.2, 0.1]  # smartphone, laptop, tablet
        elif age < 50:
            device_weights = [0.6, 0.3, 0.1]
        else:
            device_weights = [0.5, 0.3, 0.2]
        
        lifestyle.primary_device = np.random.choice(['smartphone', 'laptop', 'tablet'], p=self._normalize_weights(device_weights))
        
        # Preferred browser
        browsers = ['chrome', 'safari', 'firefox', 'edge', 'brave']
        browser_weights = [0.65, 0.15, 0.1, 0.07, 0.03]
        lifestyle.preferred_browser = np.random.choice(browsers, p=self._normalize_weights(browser_weights))
        
        return lifestyle
    
    def _generate_personality(self, persona: HumanPersona) -> Personality:
        """Generate psychological profile"""
        # MBTI type (weighted)
        mbti = np.random.choice(self.mbti_types, p=self._normalize_weights([w/100 for w in self.mbti_weights]))
        
        # Big Five scores (0-100) with realistic correlations
        big_five = {}
        
        # Base scores with some randomness
        big_five['openness'] = random.randint(40, 85)
        big_five['conscientiousness'] = random.randint(35, 90)
        big_five['extraversion'] = random.randint(30, 85)
        big_five['agreeableness'] = random.randint(40, 85)
        big_five['neuroticism'] = random.randint(25, 80)
        
        # Adjust based on MBTI
        if 'I' in mbti:
            big_five['extraversion'] -= random.randint(15, 30)
        if 'E' in mbti:
            big_five['extraversion'] += random.randint(15, 30)
        if 'S' in mbti:
            big_five['openness'] -= random.randint(10, 20)
        if 'N' in mbti:
            big_five['openness'] += random.randint(10, 20)
        if 'T' in mbti:
            big_five['agreeableness'] -= random.randint(10, 25)
        if 'F' in mbti:
            big_five['agreeableness'] += random.randint(10, 25)
        if 'J' in mbti:
            big_five['conscientiousness'] += random.randint(10, 20)
        if 'P' in mbti:
            big_five['conscientiousness'] -= random.randint(10, 20)
        
        # Clamp values
        for trait in big_five:
            big_five[trait] = max(0, min(100, big_five[trait]))
        
        # HEXACO (similar but different model)
        hexaco = {
            'honesty_humility': random.randint(30, 85),
            'emotionality': random.randint(30, 85),
            'extraversion_hexaco': big_five['extraversion'],
            'agreeableness_hexaco': big_five['agreeableness'],
            'conscientiousness_hexaco': big_five['conscientiousness'],
            'openness_hexaco': big_five['openness'],
        }
        
        # Enneagram
        enneagram = random.choice(self.enneagram_types)
        
        # Strengths and weaknesses (based on MBTI)
        strengths_map = {
            'ISTJ': ['Responsible', 'Detail-oriented', 'Organized', 'Practical'],
            'ISFJ': ['Supportive', 'Reliable', 'Patient', 'Observant'],
            'INFJ': ['Insightful', 'Creative', 'Principled', 'Decisive'],
            'INTJ': ['Strategic', 'Analytical', 'Independent', 'Determined'],
            'ISTP': ['Flexible', 'Practical', 'Calm', 'Hands-on'],
            'ISFP': ['Artistic', 'Sensitive', 'Harmonious', 'Passionate'],
            'INFP': ['Empathetic', 'Idealistic', 'Open-minded', 'Creative'],
            'INTP': ['Analytical', 'Innovative', 'Abstract thinker', 'Curious'],
            'ESTP': ['Energetic', 'Observant', 'Persuasive', 'Adaptable'],
            'ESFP': ['Enthusiastic', 'Friendly', 'Spontaneous', 'Practical'],
            'ENFP': ['Creative', 'Enthusiastic', 'Empathetic', 'Charismatic'],
            'ENTP': ['Innovative', 'Quick-witted', 'Debater', 'Strategic'],
            'ESTJ': ['Efficient', 'Organized', 'Dependable', 'Direct'],
            'ESFJ': ['Warm', 'Diligent', 'Conscientious', 'Loyal'],
            'ENFJ': ['Inspirational', 'Charismatic', 'Supportive', 'Idealistic'],
            'ENTJ': ['Confident', 'Strategic', 'Efficient', 'Ambitious'],
        }
        
        weaknesses_map = {
            'ISTJ': ['Stubborn', 'Insensitive', 'Judgmental', 'Inflexible'],
            'ISFJ': ['Overly humble', 'Reluctant to change', 'Self-sacrificing'],
            'INFJ': ['Sensitive to criticism', 'Perfectionist', 'Burns out easily'],
            'INTJ': ['Arrogant', 'Dismissive of emotion', 'Overly critical'],
            'ISTP': ['Private', 'Easily bored', 'Non-committal', 'Risk-prone'],
            'ISFP': ['Impulsive', 'Competitive', 'Unpredictable', 'Easily stressed'],
            'INFP': ['Self-critical', 'Impractical', 'Emotionally vulnerable'],
            'INTP': ['Impatient', 'Absent-minded', 'Condescending', 'Isolated'],
            'ESTP': ['Impulsive', 'Risk-prone', 'Insensitive', 'Defiant'],
            'ESFP': ['Easily bored', 'Sensitive', 'Conflict-averse', 'Impulsive'],
            'ENFP': ['Disorganized', 'Overly accommodating', 'Non-confrontational'],
            'ENTP': ['Argumentative', 'Insensitive', 'Intolerant', 'Unfocused'],
            'ESTJ': ['Inflexible', 'Judgmental', 'Blunt', 'Stubborn'],
            'ESFJ': ['Needy', 'Approval-seeking', 'Vulnerable to criticism'],
            'ENFJ': ['Overly idealistic', 'Selfless to a fault', 'Overprotective'],
            'ENTJ': ['Arrogant', 'Impatient', 'Emotionally cold', 'Dominating'],
        }
        
        strengths = strengths_map.get(mbti, ['Intelligent', 'Creative', 'Diligent'])[:random.randint(3, 5)]
        weaknesses = weaknesses_map.get(mbti, ['Impatient', 'Stubborn', 'Anxious'])[:random.randint(2, 4)]
        
        # Core values
        all_values = [
            'Honesty', 'Integrity', 'Family', 'Friendship', 'Career',
            'Health', 'Knowledge', 'Wisdom', 'Creativity', 'Freedom',
            'Security', 'Adventure', 'Justice', 'Compassion', 'Tradition',
            'Innovation', 'Sustainability', 'Community', 'Spirituality'
        ]
        
        values = random.sample(all_values, random.randint(3, 6))
        
        # Life goals
        all_goals = [
            'Buy a house', 'Start a family', 'Travel the world', 'Get promoted',
            'Start a business', 'Retire early', 'Learn a new skill',
            'Get in shape', 'Write a book', 'Make a difference',
            'Achieve financial independence', 'Go back to school',
            'Move to another country', 'Learn an instrument', 'Run a marathon'
        ]
        
        goals = random.sample(all_goals, random.randint(2, 4))
        
        return Personality(
            mbti=mbti,
            big_five=big_five,
            hexaco=hexaco,
            enneagram=enneagram,
            strengths=strengths,
            weaknesses=weaknesses,
            values=values,
            goals=goals
        )
    
    def _generate_beliefs(self, persona: HumanPersona) -> Beliefs:
        """Generate beliefs and worldview"""
        location = persona.location
        age = persona.date_info.age
        
        # Religion based on location (simplified)
        religion_map = {
            'US': ['Christianity', 'Christianity', 'Christianity', 'Atheism', 'Agnosticism', 'Judaism', 'Islam', 'Buddhism'],
            'GB': ['Christianity', 'Atheism', 'Agnosticism', 'Islam', 'Hinduism'],
            'DE': ['Christianity', 'Atheism', 'Agnosticism', 'Islam'],
            'FR': ['Christianity', 'Atheism', 'Agnosticism', 'Islam'],
            'IT': ['Christianity', 'Atheism', 'Agnosticism'],
            'ES': ['Christianity', 'Atheism', 'Agnosticism'],
            'BR': ['Christianity', 'Christianity', 'Spiritual_but_not_religious'],
            'MX': ['Christianity', 'Christianity', 'Atheism'],
            'IN': ['Hinduism', 'Hinduism', 'Islam', 'Christianity', 'Sikhism'],
            'JP': ['Buddhism', 'Shinto', 'Atheism'],
            'CN': ['Atheism', 'Buddhism'],
            'RU': ['Christianity', 'Atheism', 'Islam'],
            'SA': ['Islam', 'Islam', 'Islam'],
            'AE': ['Islam', 'Islam', 'Christianity'],
            'IL': ['Judaism', 'Judaism', 'Islam', 'Christianity'],
        }
        
        possible_religions = religion_map.get(location.country_code, ['Christianity', 'Atheism', 'Agnosticism'])
        religion = random.choice(possible_religions)
        
        # Religiosity (0-100)
        if religion in ['Atheism', 'Agnosticism']:
            religiosity = random.randint(0, 20)
        else:
            religiosity = random.randint(30, 90)
        
        # Political leaning
        politics_map = {
            'US': ['left', 'left', 'center_left', 'center', 'center_right', 'right', 'libertarian'],
            'GB': ['left', 'center_left', 'center', 'center_right', 'right'],
            'CA': ['left', 'center_left', 'center', 'center_right'],
            'DE': ['left', 'center_left', 'center', 'center_right', 'right'],
            'FR': ['left', 'center_left', 'center', 'center_right', 'right'],
            'BR': ['left', 'center_left', 'center', 'center_right', 'right'],
            'IN': ['center_left', 'center', 'center_right', 'right'],
            'JP': ['center_left', 'center', 'center_right'],
            'CN': ['apolitical', 'other'],
            'RU': ['center_right', 'right', 'apolitical'],
            'SA': ['right', 'far_right', 'apolitical'],
        }
        
        possible_politics = politics_map.get(location.country_code, ['center', 'apolitical'])
        political_leaning = random.choice(possible_politics)
        
        # Younger people tend to be more liberal
        if age < 30:
            political_engagement = random.randint(30, 80)
            social_liberalism = random.randint(60, 95)
            economic_conservatism = random.randint(10, 50)
            environmentalism = random.randint(60, 95)
        elif age < 50:
            political_engagement = random.randint(40, 85)
            social_liberalism = random.randint(40, 80)
            economic_conservatism = random.randint(20, 70)
            environmentalism = random.randint(40, 85)
        else:
            political_engagement = random.randint(50, 90)
            social_liberalism = random.randint(20, 70)
            economic_conservatism = random.randint(40, 85)
            environmentalism = random.randint(30, 75)
        
        # Adjust based on political leaning
        if political_leaning in ['far_left', 'left']:
            social_liberalism = min(95, social_liberalism + 20)
            economic_conservatism = max(0, economic_conservatism - 30)
        elif political_leaning in ['right', 'far_right']:
            social_liberalism = max(5, social_liberalism - 30)
            economic_conservatism = min(95, economic_conservatism + 30)
        
        return Beliefs(
            religion=religion,
            religiosity=religiosity,
            political_leaning=political_leaning,
            political_engagement=political_engagement,
            environmentalism=environmentalism,
            social_liberalism=social_liberalism,
            economic_conservatism=economic_conservatism
        )
    
    def _generate_digital_footprint(self, persona: HumanPersona) -> DigitalFootprint:
        """Generate simulated digital presence"""
        digital = DigitalFootprint()
        
        # Generate username variations
        name = persona.name
        usernames = [
            name.first_name.lower(),
            f"{name.first_name.lower()}.{name.last_name.lower()}",
            f"{name.first_name.lower()[:1]}{name.last_name.lower()}",
            f"{name.first_name.lower()}{name.last_name.lower()[:1]}",
            f"{name.first_name.lower()}{random.randint(10, 99)}",
        ]
        digital.usernames = list(set(usernames))
        
        # Consistent password hash (not actual password)
        password_base = f"{name.first_name}{name.last_name}{persona.date_info.birth_year}"
        digital.passwords_hash = hashlib.sha256(password_base.encode()).hexdigest()[:32]
        
        # Account creation date (backdated to appear older)
        days_ago = random.randint(30, 365 * 3)
        account_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        digital.account_creation_date = account_date
        digital.last_active = datetime.now().isoformat()
        
        # Google services used
        google_services = ['Gmail', 'YouTube', 'Google Search', 'Google Maps', 'Google Drive']
        if random.random() < 0.6:
            google_services.append('Google Photos')
        if random.random() < 0.4:
            google_services.append('Google Calendar')
        if random.random() < 0.3:
            google_services.append('Google Docs')
        
        digital.google_services = google_services
        
        # Typical login patterns
        # Working hours for employed people
        if persona.current_employment and persona.current_employment.remote_percentage > 0:
            # Remote worker - variable hours
            typical_hours = list(range(8, 20))
        elif persona.current_employment:
            # Office worker - 9-5
            typical_hours = list(range(9, 18))
        else:
            # Unemployed/student/retired - more spread out
            typical_hours = list(range(8, 23))
        
        sample_size = min(random.randint(8, 12), len(typical_hours))
        digital.typical_login_hours = sorted(random.sample(typical_hours, sample_size))
        
        # Typical days (weekdays)
        if persona.date_info.age < 25:
            # Students - more weekends
            typical_days = [0, 1, 2, 3, 4, 5, 6]  # All days
        elif persona.current_employment:
            # Workers - weekdays
            typical_days = [0, 1, 2, 3, 4]
        else:
            typical_days = [0, 1, 2, 3, 4, 5, 6]
        
        digital.typical_login_days = typical_days
        
        return digital
    
    def generate_persona(self, country_code: Optional[str] = None, 
                        age_group: Optional[AgeGroup] = None,
                        gender: Optional[str] = None) -> HumanPersona:
        """
        Generate a complete, statistically accurate human persona.
        
        Args:
            country_code: ISO country code (e.g., 'US', 'GB')
            age_group: AgeGroup enum for specific demographic
            gender: 'male', 'female', or 'non_binary'
            
        Returns:
            Complete HumanPersona with all attributes
        """
        # Select country
        if not country_code:
            country_code, faker = self._select_country()
        else:
            faker = self.fakers.get(country_code, fake_en)
        
        # Select gender
        if not gender:
            gender = random.choice(['male', 'female', 'non_binary'])
            # Non-binary is rare (2%)
            if random.random() > 0.02:
                gender = random.choice(['male', 'female'])
        
        # Generate date of birth
        date_info = self._generate_date_of_birth(age_group)
        
        # Initialize persona
        persona = HumanPersona(
            gender=gender,
            date_info=date_info
        )
        
        # Generate name
        persona.name = self._generate_name(country_code, gender, faker)
        
        # Generate location
        persona.location = self._generate_location(country_code, faker)
        
        # Generate contact info
        persona.contact = self._generate_contact_info(persona, faker)
        
        # Generate education
        persona.education = self._generate_education(persona, faker)
        
        # Generate employment
        persona.employment, persona.current_employment = self._generate_employment(persona, faker)
        
        # Generate family
        persona.family = self._generate_family(persona, faker)
        
        # Generate lifestyle
        persona.lifestyle = self._generate_lifestyle(persona)
        
        # Generate personality
        persona.personality = self._generate_personality(persona)
        
        # Generate beliefs
        persona.beliefs = self._generate_beliefs(persona)
        
        # Generate digital footprint
        persona.digital = self._generate_digital_footprint(persona)
        
        # Ensure uniqueness
        while persona.persona_id in self.generated_personas:
            persona.persona_id = str(uuid.uuid4())
        
        self.generated_personas.add(persona.persona_id)
        self.persona_count += 1
        
        return persona
    
    def generate_batch(self, count: int, **kwargs) -> List[HumanPersona]:
        """Generate multiple personas in batch"""
        personas = []
        for i in range(count):
            persona = self.generate_persona(**kwargs)
            personas.append(persona)
        return personas
    
    def export_to_json(self, personas: List[HumanPersona], filepath: str):
        """Export personas to JSON file"""
        data = [p.to_dict() for p in personas]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported {len(personas)} personas to {filepath}")


# ============================================================================
# MAIN EXECUTION - GENERATE QUANTUM PERSONAS
# ============================================================================

def main():
    """Generate and export quantum-human identities"""
    
    print("⚡⚡⚡ QUANTUM PERSONA FORGE v2026.∞ ⚡⚡⚡")
    print("=" * 60)
    print("🔮 AI Human Synthesis Engine - Undetectable Digital Identities")
    print("=" * 60)
    
    # Initialize the forge
    forge = PersonaGenerator(seed=0xDEADBEEF)
    
    # Generate diverse personas
    print("\n📊 Generating diverse persona set...")
    
    all_personas = []
    
    # Generate by country (weighted)
    for country, weight in forge.country_weights.items():
        count = max(1, int(100 * weight))  # Scale to ~100 personas
        print(f"  🌍 Generating {count} personas for {country}...")
        personas = forge.generate_batch(count, country_code=country)
        all_personas.extend(personas)
    
    # Generate additional specialized personas
    print("\n🎯 Generating targeted demographics...")
    
    # Gen Z
    gen_z = forge.generate_batch(25, age_group=AgeGroup.GEN_Z)
    all_personas.extend(gen_z)
    
    # Millennials
    millennials = forge.generate_batch(25, age_group=AgeGroup.MILLENNIAL)
    all_personas.extend(millennials)
    
    # Gen X
    gen_x = forge.generate_batch(20, age_group=AgeGroup.GEN_X)
    all_personas.extend(gen_x)
    
    # Boomers
    boomers = forge.generate_batch(15, age_group=AgeGroup.BOOMER)
    all_personas.extend(boomers)
    
    # Tech workers (specific persona type)
    tech_workers = []
    for _ in range(30):
        p = forge.generate_persona(country_code='US')
        if p.current_employment and p.current_employment.industry == 'Technology':
            tech_workers.append(p)
        else:
            # Force tech employment
            p.current_employment = Employment(
                status=EmploymentStatus.EMPLOYED_FULL_TIME,
                company=random.choice(['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Netflix']),
                title=random.choice(['Software Engineer', 'Product Manager', 'Data Scientist']),
                industry='Technology',
                start_date=f"{datetime.now().year - random.randint(1, 5)}-01-01",
                current=True,
                salary=random.randint(120000, 250000),
                salary_bracket=IncomeBracket._100K_150K
            )
            tech_workers.append(p)
    all_personas.extend(tech_workers)
    
    # Remove duplicates (by persona_id)
    unique_personas = {}
    for p in all_personas:
        unique_personas[p.persona_id] = p
    
    final_personas = list(unique_personas.values())
    
    print(f"\n✅ Generated {len(final_personas)} unique personas")
    
    # Export to JSON
    forge.export_to_json(final_personas, "config/personas_2026.json")
    
    # Export sample
    forge.export_to_json(final_personas[:50], "config/personas_sample.json")
    
    # Display sample persona
    print("\n📋 SAMPLE PERSONA:")
    sample = final_personas[0]
    print(f"  ID: {sample.persona_id[:8]}...")
    print(f"  Name: {sample.name.full_name}")
    print(f"  Gender: {sample.gender}")
    print(f"  Age: {sample.date_info.age} ({sample.date_info.generation})")
    print(f"  Location: {sample.location.city}, {sample.location.country}")
    print(f"  Email: {sample.contact.email}")
    print(f"  Occupation: {sample.current_employment.title if sample.current_employment else 'Not employed'}")
    print(f"  Personality: {sample.personality.mbti} / {sample.personality.enneagram}")
    print(f"  Interests: {', '.join(sample.lifestyle.interests[:5])}...")
    
    print("\n💾 Files saved:")
    print("  📄 config/personas_2026.json - Complete persona database")
    print("  📄 config/personas_sample.json - Sample 50 personas")
    
    return final_personas


if __name__ == "__main__":
    main()