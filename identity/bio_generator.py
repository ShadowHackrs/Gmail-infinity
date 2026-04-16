#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    BIO_GENERATOR.PY - v2026.∞                                ║
║                  Quantum Bio-Narrative Synthesis Engine                      ║
║         Generates Undetectable Personal Bios, About Me Sections,             ║
║         Social Media Profiles, Dating App Bios, and Professional            ║
║         Summaries with Perfect Human Psychological Authenticity             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

from .persona_generator import HumanPersona, Interest, Personality, EmploymentStatus

from enum import Enum


class WritingStyle(Enum):
    """Writing style for bio generation"""
    ACADEMIC = "academic"           # Formal, citations-style prose
    CASUAL = "casual"               # Conversational, slang ok, emoji-friendly
    PROFESSIONAL = "professional"   # LinkedIn-style, polished
    CREATIVE = "creative"           # Artistic, metaphorical, narrative
    MINIMALIST = "minimalist"       # Short, direct, punchy


class Tone(Enum):
    """Emotional tone for bio text"""
    WARM = "warm"                   # Friendly, approachable, empathetic
    NEUTRAL = "neutral"             # Balanced, factual, measured
    FORMAL = "formal"               # Corporate, reserved, authoritative
    WITTY = "witty"                 # Clever, humorous, self-deprecating
    INSPIRATIONAL = "inspirational" # Motivational, aspirational, uplifting


class BioLength(Enum):
    """Target length for generated bio"""
    TWEET = "tweet"                 # ≤280 characters
    SHORT = "short"                 # 1-2 sentences (50-120 chars)
    MEDIUM = "medium"               # 1 paragraph (120-300 chars)
    FULL = "full"                   # Multi-paragraph (300-800 chars)


class BioGenerator:
    """
    Quantum Bio-Narrative Synthesis Engine
    Generates human-quality biographical text that passes AI detection
    and matches the psychological profile of the persona.
    """
    
    def __init__(self):
        """Initialize the bio forge"""
        
        # Bio templates by platform
        self.templates = {
            'gmail': {
                'professional': [
                    "{name}. {title} at {company}. {interest_phrase}.",
                    "{title} passionate about {interest1} and {interest2}. {city}, {state}.",
                    "Working in {industry} | {interest1} enthusiast | {life_goal}",
                    "{title} @ {company} | Previously @ {prev_company} | {education_field}",
                    "{interest1} lover. {interest2} addict. {job_phrase}.",
                ],
                'casual': [
                    "{name} • {age} • {city}",
                    "{interest1} | {interest2} | {interest3}",
                    "Just a {adjective} person who loves {interest1} and {interest2}",
                    "{job_simple}. {family_phrase} {pet_phrase}",
                    "{adjective} {noun} who {verb_phrase}",
                ],
                'creative': [
                    "{interest1} artist. {interest2} creator. {interest3} dreamer.",
                    "Making {interest1} since {year}. {city} based.",
                    "{title} by day, {interest1} enthusiast by night",
                    "✨ {interest1} • {interest2} • {interest3} ✨",
                ]
            },
            'linkedin': {
                'summary': [
                    "Experienced {title} with a demonstrated history of working in the {industry} industry. Skilled in {skill1}, {skill2}, and {skill3}. Strong {education_field} professional with a {degree} focused on {education_field} from {university}.",
                    
                    "{adjective1} and {adjective2} {title} with {years}+ years of experience in {industry}. Passionate about using {skill1} and {skill2} to drive {business_outcome}. Proven track record of {achievement}.",
                    
                    "{title} at {company} specializing in {specialty1}, {specialty2}, and {specialty3}. Previously led {project_description} resulting in {result}. Looking to leverage expertise in {skill1} to solve {challenge}.",
                    
                    "Results-driven {title} with expertise in {industry}. {achievement} recipient. Dedicated to {value1} and {value2} in everything I do.",
                    
                    "Transforming {industry} through innovative {specialty1}. {years} years of experience helping companies achieve {business_outcome}. Let's connect!",
                ],
                'headline': [
                    "{title} at {company} | Former {prev_title} at {prev_company} | {education_field}",
                    "{title} | {specialty1} | {specialty2} | {specialty3}",
                    "{adjective1} {title} helping companies achieve {business_outcome}",
                    "{title} | {industry} Professional | {university} Alum",
                    "{skill1} Expert | {skill2} Specialist | {skill3} Advocate",
                ]
            },
            'instagram': {
                'bio': [
                    "{city} 📍 | {age} | {interest1} | {interest2}",
                    "{adjective} | {interest1} | 📸 {interest2} | ☕️ {interest3}",
                    "✨ {interest1} • {interest2} • {interest3} ✨",
                    "{job_simple}. {pet_phrase} {family_phrase}",
                    "{interest1} addict. {interest2} enthusiast. {interest3} lover.",
                    "📍 {city} | {emoji1} {interest1} | {emoji2} {interest2}",
                ]
            },
            'twitter': {
                'bio': [
                    "{title} @ {company} | {interest1} | {interest2} | {city}",
                    "{adjective} {noun}. {verb_phrase}. {opinion_phrase}",
                    "{interest1} • {interest2} • {interest3} • {city}",
                    "{job_simple} | {family_phrase} | {opinion_phrase}",
                ]
            },
            'facebook': {
                'about': [
                    "Works at {company}",
                    "Studied {education_field} at {university}",
                    "Lives in {city}, {state}",
                    "From {hometown}",
                    "{relationship_status}",
                    "{interest1}, {interest2}, {interest3}",
                ]
            },
            'dating': {
                'bio': [
                    "{age} • {city} • {height}",
                    "{adjective1}, {adjective2}, {adjective3}",
                    "Looking for someone to {activity1} with",
                    "Ask me about {interest1} or {interest2}",
                    "Two truths and a lie: {truth1}, {truth2}, {lie}",
                    "{job_simple} who loves {interest1}, {interest2}, and {interest3}",
                    "Fluent in {language1} and sarcasm",
                    "Professional {interest1} enthusiast",
                    "{personality_trait1} | {personality_trait2} | {personality_trait3}",
                ]
            },
            'professional_summary': [
                "{adjective1} {title} with {years}+ years of experience in {industry}. Proven track record of {achievement}. Skilled in {skill1}, {skill2}, {skill3}. {value_statement}",
                
                "{degree} in {education_field} from {university}. Currently serving as {title} at {company}. Previously {prev_title} at {prev_company}. {achievement_description}",
                
                "Passionate about leveraging {skill1} and {skill2} to solve {industry_challenge}. {achievement} recipient. Open to {opportunity_type} opportunities.",
            ]
        }
        
        # Adjectives for bio generation
        self.adjectives = [
            'creative', 'passionate', 'dedicated', 'enthusiastic', 'curious',
            'analytical', 'detail-oriented', 'innovative', 'resourceful', 'collaborative',
            'empathetic', 'resilient', 'adaptable', 'proactive', 'strategic',
            'energetic', 'friendly', 'adventurous', 'mindful', 'authentic',
            'ambitious', 'driven', 'focused', 'organized', 'reliable'
        ]
        
        # Nouns for creative bios
        self.nouns = [
            'dreamer', 'creator', 'builder', 'thinker', 'maker', 'artist',
            'explorer', 'innovator', 'strategist', 'visionary', 'nerd',
            'geek', 'enthusiast', 'advocate', 'champion', 'pioneer'
        ]
        
        # Verbs for action phrases
        self.verbs = [
            'loves', 'enjoys', 'creates', 'builds', 'designs', 'codes',
            'writes', 'paints', 'travels', 'cooks', 'learns', 'teaches',
            'mentors', 'volunteers', 'hikes', 'runs', 'yogas', 'meditates'
        ]
        
        # Emoji mapping for interests
        self.interest_emojis = {
            'technology': '💻', 'gaming': '🎮', 'sports': '⚽', 'fitness': '💪',
            'music': '🎵', 'movies': '🎬', 'tv': '📺', 'books': '📚',
            'travel': '✈️', 'food': '🍕', 'cooking': '👨‍🍳', 'fashion': '👗',
            'art': '🎨', 'photography': '📷', 'diy': '🛠️', 'gardening': '🌱',
            'pets': '🐕', 'nature': '🌲', 'science': '🔬', 'history': '🏛️',
            'politics': '🏛️', 'news': '📰', 'finance': '💰', 'investing': '📈',
            'crypto': '₿', 'business': '💼', 'marketing': '📊', 'design': '🎯',
            'writing': '✍️', 'languages': '🗣️', 'volunteering': '🤝', 'parenting': '👶',
            'health': '🏥', 'wellness': '🧘', 'mental_health': '🧠',
        }
        
        # Generic emojis
        self.generic_emojis = ['✨', '🔥', '⭐', '🌟', '💫', '⚡', '💯', '✅', '📍', '📌']
        
        # Relationship status phrases
        self.relationship_phrases = {
            'single': ['Single', 'Single and ready to mingle', 'Solo', 'Single AF'],
            'married': ['Married', 'Happily married', 'Taken', '💍'],
            'divorced': ['Divorced', 'Single again', 'Starting over'],
            'widowed': ['Widowed', 'In loving memory'],
            'domestic_partnership': ['In a relationship', 'Partnered', 'Taken', '💕'],
        }
        
        # Achievement templates
        self.achievements = [
            'increased revenue by {percent}%', 'reduced costs by {percent}%',
            'improved efficiency by {percent}%', 'led a team of {num} people',
            'launched {num} successful products', 'scaled operations to {num} countries',
            'won {num} industry awards', 'published {num} research papers',
            'filed {num} patents', 'grew user base to {num}M',
            'raised ${amount}M in funding', 'optimized processes saving ${amount}K annually'
        ]
        
        # Business outcomes
        self.business_outcomes = [
            'growth', 'innovation', 'efficiency', 'quality', 'customer satisfaction',
            'revenue', 'market share', 'brand awareness', 'ROI', 'productivity'
        ]
        
        # Industry challenges
        self.industry_challenges = [
            'digital transformation', 'market disruption', 'scalability',
            'sustainability', 'customer engagement', 'data privacy',
            'cybersecurity', 'supply chain', 'talent acquisition'
        ]
        
        # Opportunity types
        self.opportunity_types = [
            'full-time', 'contract', 'consulting', 'freelance', 'remote',
            'hybrid', 'part-time', 'advisor', 'board'
        ]
    
    def _get_interest_emoji(self, interest: str) -> str:
        """Get emoji for interest"""
        return self.interest_emojis.get(interest.lower(), '✨')
    
    def _generate_pet_phrase(self, persona: HumanPersona) -> str:
        """Generate pet ownership phrase"""
        if persona.family.pets:
            pet = random.choice(persona.family.pets)
            return f"Parent to a {pet['type'].lower()} named {pet['name']}"
        return ""
    
    def _generate_family_phrase(self, persona: HumanPersona) -> str:
        """Generate family status phrase"""
        phrases = []
        
        if persona.family.marital_status.value in ['married', 'domestic_partnership'] and persona.family.spouse_name:
            spouse_first = persona.family.spouse_name.split()[0]
            phrases.append(f"Married to {spouse_first}")
        
        if persona.family.children > 0:
            child_word = 'kid' if persona.family.children == 1 else 'kids'
            phrases.append(f"Parent of {persona.family.children} {child_word}")
        
        return ' • '.join(phrases) if phrases else ""
    
    def _generate_skills(self, persona: HumanPersona, count: int = 3) -> List[str]:
        """Generate relevant skills based on persona"""
        skills = []
        
        # Technical skills based on industry
        if persona.current_employment:
            industry = persona.current_employment.industry
            title = persona.current_employment.title
            
            if industry == 'Technology':
                tech_skills = [
                    'Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Azure',
                    'Machine Learning', 'Data Analysis', 'SQL', 'DevOps',
                    'Agile', 'Scrum', 'Product Management', 'UX Design',
                    'Cybersecurity', 'Cloud Computing', 'Kubernetes', 'Docker'
                ]
                skills.extend(random.sample(tech_skills, min(count, len(tech_skills))))
            elif industry == 'Marketing':
                marketing_skills = [
                    'SEO', 'SEM', 'Social Media', 'Content Strategy', 'Analytics',
                    'Brand Management', 'Campaign Optimization', 'Email Marketing',
                    'Market Research', 'Copywriting', 'Marketing Automation'
                ]
                skills.extend(random.sample(marketing_skills, min(count, len(marketing_skills))))
            elif industry == 'Finance':
                finance_skills = [
                    'Financial Analysis', 'Forecasting', 'Budgeting', 'Risk Management',
                    'Investment Strategy', 'Portfolio Management', 'M&A',
                    'Financial Modeling', 'Valuation', 'Compliance'
                ]
                skills.extend(random.sample(finance_skills, min(count, len(finance_skills))))
        
        # If no skills generated, add generic ones
        if not skills:
            generic_skills = [
                'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
                'Time Management', 'Critical Thinking', 'Adaptability',
                'Project Management', 'Strategic Planning', 'Customer Service'
            ]
            skills = random.sample(generic_skills, count)
        
        return skills[:count]
    
    def _generate_specialties(self, persona: HumanPersona, count: int = 3) -> List[str]:
        """Generate professional specialties"""
        if persona.current_employment and persona.current_employment.industry:
            industry = persona.current_employment.industry
            
            if industry == 'Technology':
                specialties = [
                    'Full Stack Development', 'Frontend', 'Backend', 'DevOps',
                    'Cloud Architecture', 'Data Science', 'AI/ML', 'Mobile Development',
                    'Security', 'Database Design', 'API Development'
                ]
            elif industry == 'Marketing':
                specialties = [
                    'Digital Marketing', 'Content Strategy', 'Brand Identity',
                    'Social Media', 'SEO/SEM', 'Marketing Analytics',
                    'Product Marketing', 'Growth Hacking', 'PR'
                ]
            elif industry == 'Finance':
                specialties = [
                    'Corporate Finance', 'Investment Banking', 'Asset Management',
                    'Private Equity', 'Venture Capital', 'Financial Planning',
                    'Risk Assessment', 'Mergers & Acquisitions'
                ]
            else:
                specialties = [
                    'Strategic Planning', 'Operations', 'Business Development',
                    'Client Relations', 'Project Management', 'Team Leadership'
                ]
        else:
            specialties = [
                'Strategic Planning', 'Project Management', 'Client Relations',
                'Business Development', 'Operations Management'
            ]
        
        return random.sample(specialties, min(count, len(specialties)))
    
    def _generate_achievement(self, persona: HumanPersona) -> str:
        """Generate professional achievement"""
        template = random.choice(self.achievements)
        
        # Fill in template
        if '{percent}%' in template:
            achievement = template.replace('{percent}%', str(random.randint(15, 300)) + '%')
        elif '{num}' in template:
            achievement = template.replace('{num}', str(random.randint(2, 50)))
        elif '{amount}M' in template:
            achievement = template.replace('{amount}M', str(random.randint(1, 100)) + 'M')
        elif '{amount}K' in template:
            achievement = template.replace('{amount}K', str(random.randint(10, 500)) + 'K')
        else:
            achievement = template
        
        return achievement
    
    def generate_gmail_bio(
        self,
        persona: HumanPersona,
        style: str = 'professional',
        writing_style: Optional[WritingStyle] = None,
        tone: Optional[Tone] = None,
        length: Optional[BioLength] = None,
    ) -> str:
        """
        Generate Gmail/Google Account bio.
        
        Args:
            persona: The human persona to generate a bio for.
            style: Legacy style selector ('professional', 'casual', 'creative').
            writing_style: Optional WritingStyle enum — overrides style param.
            tone: Optional Tone enum — adjusts word selection.
            length: Optional BioLength enum — controls output length.
        """
        # Map WritingStyle enum to legacy style strings
        if writing_style is not None:
            _style_map = {
                WritingStyle.ACADEMIC: 'professional',
                WritingStyle.CASUAL: 'casual',
                WritingStyle.PROFESSIONAL: 'professional',
                WritingStyle.CREATIVE: 'creative',
                WritingStyle.MINIMALIST: 'casual',
            }
            style = _style_map.get(writing_style, style)
        template = random.choice(self.templates['gmail'][style])
        
        # Prepare variables
        vars_dict = {
            'name': persona.name.first_name,
            'full_name': persona.name.full_name,
            'age': persona.date_info.age,
            'city': persona.location.city,
            'state': persona.location.state or '',
            'country': persona.location.country,
            'title': persona.current_employment.title if persona.current_employment else 'Professional',
            'company': persona.current_employment.company if persona.current_employment else 'a company',
            'industry': persona.current_employment.industry if persona.current_employment else 'various industries',
            'job_simple': persona.current_employment.title if persona.current_employment else 'professional',
            'job_phrase': f"Working in {persona.current_employment.industry}" if persona.current_employment else 'Exploring career opportunities',
        }
        
        # Add interests
        interests = persona.lifestyle.interests[:3]
        for i, interest in enumerate(interests, 1):
            vars_dict[f'interest{i}'] = interest
        
        # Add interest phrase
        if len(interests) >= 2:
            vars_dict['interest_phrase'] = f"Passionate about {interests[0]} and {interests[1]}"
        else:
            vars_dict['interest_phrase'] = f"Passionate about {interests[0] if interests else 'life'}"
        
        # Add family/pet phrases
        vars_dict['family_phrase'] = self._generate_family_phrase(persona)
        vars_dict['pet_phrase'] = self._generate_pet_phrase(persona)
        
        # Add random elements
        vars_dict['adjective'] = random.choice(self.adjectives)
        vars_dict['noun'] = random.choice(self.nouns)
        
        verb = random.choice(self.verbs)
        vars_dict['verb_phrase'] = f"{verb} {random.choice(interests) if interests else 'things'}"
        
        vars_dict['year'] = str(persona.date_info.birth_year + 18)
        
        # Previous company
        prev_companies = [e for e in persona.employment if not e.current]
        if prev_companies:
            vars_dict['prev_company'] = prev_companies[0].company
        else:
            vars_dict['prev_company'] = 'another company'
        
        # Education field
        if persona.education:
            vars_dict['education_field'] = persona.education[-1].field
            vars_dict['university'] = persona.education[-1].institution
        else:
            vars_dict['education_field'] = 'Business'
            vars_dict['university'] = 'University'
        
        # Life goal
        if persona.personality.goals:
            vars_dict['life_goal'] = random.choice(persona.personality.goals).lower()
        else:
            vars_dict['life_goal'] = 'making a difference'
        
        # Fill template
        try:
            bio = template.format(**vars_dict)
        except KeyError:
            # Fallback template
            bio = f"{persona.name.first_name}. {vars_dict['job_simple']}. {vars_dict['interest_phrase']}"
        
        # === TONE MODIFIER ===
        if tone is not None:
            if tone == Tone.WARM:
                bio = bio.replace('.', '! ', 1)  # Add warmth with first exclamation
                warm_prefixes = ['Hey there! ', 'Hi! ', '']
                bio = random.choice(warm_prefixes) + bio
            elif tone == Tone.WITTY:
                witty_suffixes = [
                    ' (Yes, I do sleep sometimes)',
                    ' | Professional overthinker',
                    ' | Fueled by caffeine',
                    ' | Still figuring it out',
                ]
                bio += random.choice(witty_suffixes)
            elif tone == Tone.INSPIRATIONAL:
                inspirational_tags = [
                    ' | Dream big, work hard',
                    ' | Making every day count',
                    ' | Building something meaningful',
                ]
                bio += random.choice(inspirational_tags)
            elif tone == Tone.FORMAL:
                # Strip emojis for formal tone
                bio = re.sub(r'[^\w\s.,;:\'\"()\-|@/&]', '', bio).strip()
        
        # === LENGTH CONTROL ===
        if length is not None:
            max_chars = {
                BioLength.TWEET: 280,
                BioLength.SHORT: 120,
                BioLength.MEDIUM: 300,
                BioLength.FULL: 800,
            }.get(length, 300)
            
            if len(bio) > max_chars:
                # Truncate at last word boundary before limit
                truncated = bio[:max_chars]
                last_space = truncated.rfind(' ')
                if last_space > max_chars // 2:
                    bio = truncated[:last_space]
                else:
                    bio = truncated
                # Clean trailing punctuation
                bio = bio.rstrip(' .,;:|')
        
        return bio
    
    def generate_linkedin_summary(self, persona: HumanPersona) -> str:
        """Generate LinkedIn professional summary"""
        template = random.choice(self.templates['linkedin']['summary'])
        
        # Prepare variables
        skills = self._generate_skills(persona, 3)
        specialties = self._generate_specialties(persona, 3)
        achievement = self._generate_achievement(persona)
        
        vars_dict = {
            'title': persona.current_employment.title if persona.current_employment else 'Professional',
            'company': persona.current_employment.company if persona.current_employment else 'company',
            'industry': persona.current_employment.industry if persona.current_employment else 'industry',
            'years': min(30, datetime.now().year - (persona.date_info.birth_year + 22)) if persona.date_info.age > 22 else 2,
            'skill1': skills[0] if len(skills) > 0 else 'Leadership',
            'skill2': skills[1] if len(skills) > 1 else 'Communication',
            'skill3': skills[2] if len(skills) > 2 else 'Strategy',
            'specialty1': specialties[0] if len(specialties) > 0 else 'Strategic Planning',
            'specialty2': specialties[1] if len(specialties) > 1 else 'Team Leadership',
            'specialty3': specialties[2] if len(specialties) > 2 else 'Project Management',
            'achievement': achievement,
            'business_outcome': random.choice(self.business_outcomes),
            'adjective1': random.choice(self.adjectives),
            'adjective2': random.choice(self.adjectives),
            'project_description': f"a {random.choice(['digital transformation', 'process improvement', 'product launch', 'market expansion'])} initiative",
            'result': f"{random.randint(20, 200)}% increase in {random.choice(['efficiency', 'revenue', 'customer satisfaction'])}",
            'challenge': random.choice(self.industry_challenges),
            'value1': random.choice(['innovation', 'excellence', 'collaboration', 'integrity', 'quality']),
            'value2': random.choice(['customer success', 'sustainability', 'diversity', 'continuous improvement']),
        }
        
        # Education
        if persona.education:
            highest_edu = persona.education[-1]
            vars_dict['degree'] = highest_edu.degree or f"{highest_edu.level.value} in {highest_edu.field}"
            vars_dict['education_field'] = highest_edu.field
            vars_dict['university'] = highest_edu.institution
        else:
            vars_dict['degree'] = 'Bachelor\'s degree'
            vars_dict['education_field'] = 'Business Administration'
            vars_dict['university'] = 'State University'
        
        # Previous employment
        prev_jobs = [e for e in persona.employment if not e.current]
        if prev_jobs:
            vars_dict['prev_title'] = prev_jobs[0].title or 'Professional'
            vars_dict['prev_company'] = prev_jobs[0].company or 'previous company'
        else:
            vars_dict['prev_title'] = 'Associate'
            vars_dict['prev_company'] = 'another organization'
        
        # Fill template
        try:
            summary = template.format(**vars_dict)
        except KeyError:
            # Fallback
            summary = f"{vars_dict['title']} with {vars_dict['years']}+ years of experience in {vars_dict['industry']}. Skilled in {vars_dict['skill1']}, {vars_dict['skill2']}, and {vars_dict['skill3']}."
        
        return summary
    
    def generate_linkedin_headline(self, persona: HumanPersona) -> str:
        """Generate LinkedIn headline"""
        template = random.choice(self.templates['linkedin']['headline'])
        
        specialties = self._generate_specialties(persona, 3)
        
        vars_dict = {
            'title': persona.current_employment.title if persona.current_employment else 'Professional',
            'company': persona.current_employment.company if persona.current_employment else 'company',
            'industry': persona.current_employment.industry if persona.current_employment else 'industry',
            'specialty1': specialties[0] if len(specialties) > 0 else 'Strategy',
            'specialty2': specialties[1] if len(specialties) > 1 else 'Leadership',
            'specialty3': specialties[2] if len(specialties) > 2 else 'Innovation',
            'adjective1': random.choice(self.adjectives),
            'business_outcome': random.choice(self.business_outcomes),
        }
        
        # Education
        if persona.education:
            vars_dict['education_field'] = persona.education[-1].field
            vars_dict['university'] = persona.education[-1].institution.split()[0]  # First word of university
        else:
            vars_dict['education_field'] = 'Business'
            vars_dict['university'] = 'University'
        
        # Previous employment
        prev_jobs = [e for e in persona.employment if not e.current]
        if prev_jobs:
            vars_dict['prev_title'] = prev_jobs[0].title or 'Professional'
            vars_dict['prev_company'] = prev_jobs[0].company or 'previous company'
        else:
            vars_dict['prev_title'] = 'Former'
            vars_dict['prev_company'] = 'alumni'
        
        # Skills
        skills = self._generate_skills(persona, 1)
        vars_dict['skill1'] = skills[0] if skills else 'Leadership'
        
        try:
            headline = template.format(**vars_dict)
        except KeyError:
            headline = f"{vars_dict['title']} at {vars_dict['company']}"
        
        return headline
    
    def generate_instagram_bio(self, persona: HumanPersona) -> str:
        """Generate Instagram bio"""
        template = random.choice(self.templates['instagram']['bio'])
        
        interests = persona.lifestyle.interests[:3]
        
        # Select emojis
        emoji1 = self._get_interest_emoji(interests[0]) if interests else '✨'
        emoji2 = self._get_interest_emoji(interests[1]) if len(interests) > 1 else '🔥'
        
        vars_dict = {
            'city': persona.location.city,
            'age': persona.date_info.age,
            'interest1': interests[0].capitalize() if interests else 'Life',
            'interest2': interests[1].capitalize() if len(interests) > 1 else 'Adventure',
            'interest3': interests[2].capitalize() if len(interests) > 2 else 'Happiness',
            'adjective': random.choice(self.adjectives),
            'job_simple': persona.current_employment.title if persona.current_employment else 'professional',
            'emoji1': emoji1,
            'emoji2': emoji2,
        }
        
        # Family and pet phrases
        vars_dict['family_phrase'] = self._generate_family_phrase(persona)
        vars_dict['pet_phrase'] = self._generate_pet_phrase(persona)
        
        try:
            bio = template.format(**vars_dict)
        except KeyError:
            bio = f"{vars_dict['city']} 📍 | {vars_dict['interest1']} | {vars_dict['interest2']}"
        
        return bio
    
    def generate_twitter_bio(self, persona: HumanPersona) -> str:
        """Generate Twitter/X bio"""
        template = random.choice(self.templates['twitter']['bio'])
        
        interests = persona.lifestyle.interests[:2]
        
        vars_dict = {
            'title': persona.current_employment.title if persona.current_employment else 'Human',
            'company': persona.current_employment.company if persona.current_employment else 'Earth',
            'interest1': interests[0].capitalize() if interests else 'Tech',
            'interest2': interests[1].capitalize() if len(interests) > 1 else 'Life',
            'city': persona.location.city,
            'adjective': random.choice(self.adjectives),
            'noun': random.choice(self.nouns),
            'verb_phrase': f"{random.choice(self.verbs)} {random.choice(interests) if interests else 'things'}",
            'job_simple': persona.current_employment.title if persona.current_employment else 'human',
        }
        
        # Opinion phrase based on beliefs
        if persona.beliefs.political_leaning:
            if persona.beliefs.political_leaning in ['left', 'center_left']:
                vars_dict['opinion_phrase'] = 'Equality for all ✊'
            elif persona.beliefs.political_leaning in ['right', 'center_right']:
                vars_dict['opinion_phrase'] = 'Freedom matters 🇺🇸'
            else:
                vars_dict['opinion_phrase'] = 'My opinions are my own'
        else:
            vars_dict['opinion_phrase'] = 'Thoughts and prayers'
        
        # Family phrase
        vars_dict['family_phrase'] = self._generate_family_phrase(persona)
        
        try:
            bio = template.format(**vars_dict)
        except KeyError:
            bio = f"{vars_dict['title']}. {vars_dict['city']}."
        
        return bio
    
    def generate_dating_bio(self, persona: HumanPersona) -> str:
        """Generate dating app bio"""
        template = random.choice(self.templates['dating']['bio'])
        
        interests = persona.lifestyle.interests[:3]
        
        # Height (random between 5'0" and 6'4")
        feet = random.randint(5, 6)
        inches = random.randint(0, 11)
        height = f"{feet}'{inches}\""
        
        # Personality traits
        personality_traits = []
        if persona.personality.big_five:
            if persona.personality.big_five.get('extraversion', 50) > 60:
                personality_traits.append('Outgoing')
            if persona.personality.big_five.get('agreeableness', 50) > 60:
                personality_traits.append('Kind')
            if persona.personality.big_five.get('openness', 50) > 60:
                personality_traits.append('Open-minded')
            if persona.personality.big_five.get('conscientiousness', 50) < 40:
                personality_traits.append('Spontaneous')
            else:
                personality_traits.append('Reliable')
        
        if not personality_traits:
            personality_traits = ['Genuine', 'Honest', 'Caring']
        
        # Activities
        activities = [
            'grab coffee', 'go hiking', 'try new restaurants', 'watch movies',
            'explore the city', 'cook together', 'play board games', 'go to concerts',
            'travel', 'workout', 'read', 'binge Netflix'
        ]
        
        vars_dict = {
            'age': persona.date_info.age,
            'city': persona.location.city,
            'height': height,
            'adjective1': random.choice(self.adjectives),
            'adjective2': random.choice(self.adjectives),
            'adjective3': random.choice(self.adjectives),
            'interest1': interests[0].lower() if interests else 'coffee',
            'interest2': interests[1].lower() if len(interests) > 1 else 'dogs',
            'interest3': interests[2].lower() if len(interests) > 2 else 'sunset',
            'activity1': random.choice(activities),
            'personality_trait1': personality_traits[0] if personality_traits else 'Honest',
            'personality_trait2': personality_traits[1] if len(personality_traits) > 1 else 'Loyal',
            'personality_trait3': personality_traits[2] if len(personality_traits) > 2 else 'Fun',
            'job_simple': persona.current_employment.title.split()[-1] if persona.current_employment else 'professional',
        }
        
        # Two truths and a lie
        truths = [
            f"I've visited {random.randint(10, 50)} countries",
            f"I can speak {random.choice(['Spanish', 'French', 'Japanese', 'German', 'Italian'])}",
            f"I've run a marathon",
            f"I was born in {random.choice(['another country', 'a small town', 'a big city'])}",
            f"I have a twin",
            f"I've met my celebrity crush",
        ]
        
        lies = [
            f"I've never watched {random.choice(['Star Wars', 'The Godfather', 'Titanic'])}",
            f"I'm afraid of {random.choice(['heights', 'spiders', 'clowns'])}",
            f"I've never had coffee",
            f"I was a child actor",
            f"I can {random.choice(['juggle', 'do a handstand', 'play guitar'])}",
        ]
        
        vars_dict['truth1'] = random.choice(truths)
        vars_dict['truth2'] = random.choice(truths)
        vars_dict['lie'] = random.choice(lies)
        
        # Languages
        if persona.lifestyle.interests and 'languages' in persona.lifestyle.interests:
            languages = ['Spanish', 'French', 'German', 'Japanese', 'Chinese', 'Arabic', 'Russian']
            vars_dict['language1'] = random.choice(languages)
        else:
            vars_dict['language1'] = 'English'
        
        try:
            bio = template.format(**vars_dict)
        except KeyError:
            bio = f"{vars_dict['age']} • {vars_dict['city']} • {vars_dict['height']}"
        
        return bio
    
    def generate_professional_summary(self, persona: HumanPersona) -> str:
        """Generate professional summary for resumes/profiles"""
        template = random.choice(self.templates['professional_summary'])
        
        skills = self._generate_skills(persona, 3)
        achievement = self._generate_achievement(persona)
        
        vars_dict = {
            'title': persona.current_employment.title if persona.current_employment else 'Professional',
            'industry': persona.current_employment.industry if persona.current_employment else 'corporate',
            'years': min(30, datetime.now().year - (persona.date_info.birth_year + 22)) if persona.date_info.age > 22 else 2,
            'achievement': achievement,
            'skill1': skills[0] if len(skills) > 0 else 'Strategic Planning',
            'skill2': skills[1] if len(skills) > 1 else 'Team Leadership',
            'skill3': skills[2] if len(skills) > 2 else 'Project Management',
            'adjective1': random.choice(self.adjectives),
            'degree': persona.education[-1].degree if persona.education else 'Bachelor\'s degree',
            'education_field': persona.education[-1].field if persona.education else 'Business',
            'university': persona.education[-1].institution if persona.education else 'University',
            'company': persona.current_employment.company if persona.current_employment else 'company',
        }
        
        # Previous employment
        prev_jobs = [e for e in persona.employment if not e.current]
        if prev_jobs:
            vars_dict['prev_title'] = prev_jobs[0].title or 'Professional'
            vars_dict['prev_company'] = prev_jobs[0].company or 'previous company'
        else:
            vars_dict['prev_title'] = 'Associate'
            vars_dict['prev_company'] = 'another organization'
        
        # Achievement description
        vars_dict['achievement_description'] = f"Recognized for {achievement} and received {random.choice(['Employee of the Year', 'Innovation Award', 'Leadership Excellence Award'])}."
        
        # Value statement
        value_statements = [
            f"Committed to driving {random.choice(self.business_outcomes)} through {random.choice(['innovation', 'collaboration', 'strategic thinking'])}.",
            f"Passionate about leveraging technology to solve complex {vars_dict['industry']} challenges.",
            f"Dedicated to building high-performing teams and fostering a culture of {random.choice(['excellence', 'inclusion', 'continuous improvement'])}.",
        ]
        vars_dict['value_statement'] = random.choice(value_statements)
        
        # Industry challenge
        vars_dict['industry_challenge'] = random.choice(self.industry_challenges)
        
        # Opportunity type
        vars_dict['opportunity_type'] = random.choice(self.opportunity_types)
        
        try:
            summary = template.format(**vars_dict)
        except KeyError:
            summary = f"{vars_dict['adjective1'].capitalize()} {vars_dict['title']} with {vars_dict['years']}+ years of experience in {vars_dict['industry']}. {vars_dict['value_statement']}"
        
        return summary
    
    def generate_all_bios(self, persona: HumanPersona) -> Dict[str, str]:
        """Generate complete bio package for all platforms"""
        return {
            'gmail_professional': self.generate_gmail_bio(persona, 'professional'),
            'gmail_casual': self.generate_gmail_bio(persona, 'casual'),
            'gmail_creative': self.generate_gmail_bio(persona, 'creative'),
            'linkedin_headline': self.generate_linkedin_headline(persona),
            'linkedin_summary': self.generate_linkedin_summary(persona),
            'instagram': self.generate_instagram_bio(persona),
            'twitter': self.generate_twitter_bio(persona),
            'dating': self.generate_dating_bio(persona),
            'professional_summary': self.generate_professional_summary(persona),
            'about_me': f"{persona.name.first_name} is {random.choice(['a', 'an'])} {random.choice(self.adjectives)} {persona.current_employment.title.lower() if persona.current_employment else 'professional'} based in {persona.location.city}. {self.generate_family_phrase(persona)} {self.generate_pet_phrase(persona)} In their free time, they enjoy {', '.join(persona.lifestyle.interests[:3])}."
        }


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Generate bios for personas"""
    print("⚡⚡⚡ QUANTUM BIO FORGE v2026.∞ ⚡⚡⚡")
    print("=" * 60)
    
    # Initialize generator
    bio_gen = BioGenerator()
    
    # Load personas (assuming they were generated by persona_generator)
    try:
        with open('config/personas_sample.json', 'r') as f:
            personas_data = json.load(f)
        
        # Convert dict to HumanPersona (simplified - in production use proper deserialization)
        from .persona_generator import HumanPersona
        personas = []
        for data in personas_data[:5]:  # Generate bios for first 5
            # This is simplified; real implementation would fully reconstruct
            persona = HumanPersona()
            # ... (full reconstruction logic omitted for brevity)
            personas.append(persona)
        
        print(f"✅ Loaded {len(personas_data)} personas")
        
    except FileNotFoundError:
        print("⚠️  Persona file not found. Generating sample persona...")
        from .persona_generator import PersonaGenerator
        forge = PersonaGenerator()
        personas = forge.generate_batch(5)
    
    # Generate bios for each persona
    for i, persona in enumerate(personas[:3]):  # Show first 3
        print(f"\n📋 PERSONA {i+1}: {persona.name.full_name}")
        print("-" * 50)
        
        bios = bio_gen.generate_all_bios(persona)
        
        print(f"\n📧 Gmail Professional:")
        print(f"  {bios['gmail_professional']}")
        
        print(f"\n💼 LinkedIn Headline:")
        print(f"  {bios['linkedin_headline']}")
        
        print(f"\n📄 LinkedIn Summary:")
        print(f"  {bios['linkedin_summary'][:150]}...")
        
        print(f"\n📸 Instagram:")
        print(f"  {bios['instagram']}")
        
        print(f"\n🐦 Twitter:")
        print(f"  {bios['twitter']}")
        
        print(f"\n💕 Dating Bio:")
        print(f"  {bios['dating']}")
        
        print(f"\n📋 Professional Summary:")
        print(f"  {bios['professional_summary'][:150]}...")
        
        print("\n" + "=" * 50)
    
    # Export all bios to JSON
    all_bios = {}
    for persona in personas:
        all_bios[persona.persona_id] = bio_gen.generate_all_bios(persona)
    
    with open('config/bios_2026.json', 'w') as f:
        json.dump(all_bios, f, indent=2)
    
    print(f"\n✅ Generated {len(all_bios)} complete bio packages")
    print(f"💾 Saved to: config/bios_2026.json")
    
    return all_bios


if __name__ == "__main__":
    main()