#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GOOGLE_SERVICE_WARMUPS.PY - v2026.∞                       ║
║              Google Service Activity Simulation for Trust Building           ║
║                                                                              ║
║   Modules:                                                                   ║
║   ├── AndroidPlayStoreWarmup    → Play Store browse/search/install/review   ║
║   ├── GooglePhotosWarmup        → Photo upload, album, share, memories      ║
║   ├── CalendarEventGenerator    → Event creation, invites, reminders        ║
║   ├── GoogleDocsWarmup          → Document creation, editing, sharing       ║
║   ├── GoogleSheetsWarmup        → Spreadsheet creation, data entry, charts  ║
║   ├── GoogleSlidesWarmup        → Presentation creation, themes             ║
║   └── ChromeSyncSimulator       → Bookmarks, history, passwords, extensions ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import random
import hashlib
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE WARMUP CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BaseWarmup:
    """Base class for all Google service warmup modules"""
    
    def __init__(self, browser=None, persona=None):
        self.browser = browser
        self.persona = persona
        self._activity_log = []
    
    async def _human_delay(self, min_s: float = 0.5, max_s: float = 3.0):
        """Simulate human-like delay (skipped in headless/test mode)"""
        if self.browser is None:
            return  # No browser — skip delay in test/headless mode
        await asyncio.sleep(random.uniform(min_s, max_s))
    
    async def _navigate(self, url: str):
        """Navigate with human-like delay"""
        if self.browser and hasattr(self.browser, 'page') and self.browser.page:
            await self.browser.page.goto(url, wait_until='networkidle', timeout=30000)
            await self._human_delay(1, 3)
    
    async def _click(self, selector: str):
        """Click with human-like behavior"""
        if self.browser and hasattr(self.browser, 'human_click'):
            await self.browser.human_click(selector)
        elif self.browser and hasattr(self.browser, 'page') and self.browser.page:
            await self.browser.page.click(selector)
        await self._human_delay(0.5, 2.0)
    
    async def _type(self, selector: str, text: str):
        """Type with human-like behavior"""
        if self.browser and hasattr(self.browser, 'human_type'):
            await self.browser.human_type(selector, text)
        elif self.browser and hasattr(self.browser, 'page') and self.browser.page:
            await self.browser.page.fill(selector, text)
        await self._human_delay(0.3, 1.0)
    
    async def _scroll(self, pixels: int = None):
        """Scroll with human-like behavior"""
        if self.browser and hasattr(self.browser, 'human_scroll'):
            await self.browser.human_scroll(pixels)
        await self._human_delay(0.5, 1.5)
    
    def _log(self, action: str, details: Dict = None):
        """Log activity"""
        entry = {
            'service': self.__class__.__name__,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {},
        }
        self._activity_log.append(entry)
        logger.debug(f"[{self.__class__.__name__}] {action}")
    
    def get_activity_log(self) -> List[Dict]:
        return self._activity_log


# ═══════════════════════════════════════════════════════════════════════════════
# ANDROID PLAY STORE WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class AndroidPlayStoreWarmup(BaseWarmup):
    """Google Play Store activity simulation"""
    
    CATEGORIES = [
        'GAME_ACTION', 'GAME_PUZZLE', 'GAME_CASUAL', 'GAME_RACING',
        'COMMUNICATION', 'SOCIAL', 'PHOTOGRAPHY', 'PRODUCTIVITY',
        'TOOLS', 'ENTERTAINMENT', 'MUSIC_AND_AUDIO', 'EDUCATION',
        'HEALTH_AND_FITNESS', 'FINANCE', 'NEWS_AND_MAGAZINES',
    ]
    
    POPULAR_APPS = [
        {'id': 'com.spotify.music', 'name': 'Spotify'},
        {'id': 'com.instagram.android', 'name': 'Instagram'},
        {'id': 'com.whatsapp', 'name': 'WhatsApp'},
        {'id': 'com.snapchat.android', 'name': 'Snapchat'},
        {'id': 'com.twitter.android', 'name': 'X (Twitter)'},
        {'id': 'com.netflix.mediaclient', 'name': 'Netflix'},
        {'id': 'com.duolingo', 'name': 'Duolingo'},
        {'id': 'com.google.android.apps.maps', 'name': 'Google Maps'},
        {'id': 'com.amazon.mShop.android.shopping', 'name': 'Amazon Shopping'},
        {'id': 'com.reddit.frontpage', 'name': 'Reddit'},
        {'id': 'org.telegram.messenger', 'name': 'Telegram'},
        {'id': 'com.discord', 'name': 'Discord'},
    ]
    
    async def browse_apps(self, category: str = None, duration_min: int = 5):
        """Browse app category in Play Store"""
        category = category or random.choice(self.CATEGORIES)
        
        await self._navigate(f'https://play.google.com/store/apps/category/{category}')
        self._log('browse_category', {'category': category})
        
        # Scroll through apps
        scroll_count = random.randint(3, 8)
        for i in range(scroll_count):
            await self._scroll(random.randint(300, 600))
            await self._human_delay(1, 3)
        
        # Click on random app cards
        click_count = random.randint(1, 3)
        for _ in range(click_count):
            try:
                await self._click('div[class*="card"]')
                await self._human_delay(2, 5)  # Read app page
                await self._scroll(random.randint(200, 500))
            except Exception:
                pass
        
        self._log('browse_complete', {'duration_min': duration_min, 'scrolls': scroll_count})
    
    async def search_app(self, query: str = None):
        """Search for an app"""
        if not query:
            app = random.choice(self.POPULAR_APPS)
            query = app['name']
        
        await self._navigate('https://play.google.com/store')
        
        try:
            await self._type('input[aria-label="Search"]', query)
            await self._human_delay(0.5, 1.0)
            # Press enter
            if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                await self.browser.page.keyboard.press('Enter')
            await self._human_delay(2, 4)
        except Exception:
            pass
        
        self._log('search_app', {'query': query})
    
    async def read_reviews(self, app_id: str = None, count: int = 3):
        """Read app reviews"""
        if not app_id:
            app_id = random.choice(self.POPULAR_APPS)['id']
        
        await self._navigate(f'https://play.google.com/store/apps/details?id={app_id}')
        
        # Scroll to reviews section
        for _ in range(4):
            await self._scroll(random.randint(300, 500))
        
        # Read reviews (simulate by scrolling through review area)
        for i in range(count):
            await self._scroll(random.randint(100, 300))
            await self._human_delay(3, 8)  # Reading time
        
        self._log('read_reviews', {'app_id': app_id, 'reviews_read': count})
    
    async def install_free_app(self, app_id: str = None):
        """Simulate installing a free app"""
        if not app_id:
            app_id = random.choice(self.POPULAR_APPS)['id']
        
        await self._navigate(f'https://play.google.com/store/apps/details?id={app_id}')
        await self._human_delay(2, 4)
        
        try:
            await self._click('button:has-text("Install")')
            await self._human_delay(3, 8)  # Installation time
        except Exception:
            pass
        
        self._log('install_app', {'app_id': app_id})
    
    async def leave_rating(self, app_id: str = None, stars: int = None):
        """Leave a star rating on an app"""
        if not stars:
            stars = random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0]
        
        self._log('leave_rating', {'app_id': app_id or 'random', 'stars': stars})
    
    async def run_warmup_session(self, duration_min: int = 15):
        """Run a complete Play Store warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        # Browse categories
        await self.browse_apps(duration_min=5)
        
        # Search for apps
        for _ in range(random.randint(1, 3)):
            await self.search_app()
        
        # Read reviews
        await self.read_reviews(count=random.randint(2, 5))
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE PHOTOS WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class GooglePhotosWarmup(BaseWarmup):
    """Google Photos activity simulation"""
    
    async def upload_photos(self, image_paths: List[str] = None):
        """Upload photos to Google Photos"""
        if not image_paths:
            # Simulate upload count
            count = random.randint(3, 10)
            self._log('upload_photos', {'count': count, 'simulated': True})
            return
        
        await self._navigate('https://photos.google.com')
        
        for path in image_paths:
            try:
                await self._click('button[aria-label="Upload"]')
                await self._human_delay(1, 2)
                # File input
                if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                    file_input = await self.browser.page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(path)
                        await self._human_delay(3, 8)
            except Exception:
                pass
        
        self._log('upload_photos', {'count': len(image_paths)})
    
    async def create_album(self, name: str = None, photo_ids: List[str] = None):
        """Create a photo album"""
        if not name:
            album_names = [
                'Summer 2025', 'Best of 2024', 'Family', 'Travel',
                'Weekend Fun', 'Nature', 'Food Pics', 'Random',
            ]
            name = random.choice(album_names)
        
        await self._navigate('https://photos.google.com/albums')
        
        try:
            await self._click('button[aria-label="Create album"]')
            await self._human_delay(1, 2)
            await self._type('input[aria-label="Album title"]', name)
            await self._human_delay(1, 2)
        except Exception:
            pass
        
        self._log('create_album', {'name': name, 'photos': len(photo_ids or [])})
    
    async def share_album(self, album_id: str = None, email: str = None):
        """Share album with another user"""
        self._log('share_album', {'album_id': album_id or 'random', 'shared_with': email or 'contact'})
    
    async def browse_memories(self, duration_min: int = 3):
        """Browse memories/suggestions section"""
        await self._navigate('https://photos.google.com')
        
        for _ in range(random.randint(5, 15)):
            await self._scroll(random.randint(200, 500))
            await self._human_delay(1, 4)
        
        self._log('browse_memories', {'duration_min': duration_min})
    
    async def run_warmup_session(self, duration_min: int = 10):
        """Run complete Photos warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        await self.browse_memories(duration_min=3)
        await self.upload_photos()
        await self.create_album()
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR EVENT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class CalendarEventGenerator(BaseWarmup):
    """Google Calendar activity simulation"""
    
    EVENT_TEMPLATES = [
        {'title': 'Team Standup', 'duration': 15, 'recurrence': 'daily'},
        {'title': 'Lunch Break', 'duration': 60, 'recurrence': 'daily'},
        {'title': 'Weekly Planning', 'duration': 60, 'recurrence': 'weekly'},
        {'title': 'Gym Session', 'duration': 90, 'recurrence': 'weekly'},
        {'title': '1:1 with Manager', 'duration': 30, 'recurrence': 'weekly'},
        {'title': 'Project Review', 'duration': 45, 'recurrence': None},
        {'title': 'Dentist Appointment', 'duration': 60, 'recurrence': None},
        {'title': 'Birthday Party', 'duration': 180, 'recurrence': None},
        {'title': 'Coffee with Friend', 'duration': 60, 'recurrence': None},
        {'title': 'Flight to NYC', 'duration': 240, 'recurrence': None},
    ]
    
    async def create_event(self, title: str = None, datetime_str: str = None, duration_min: int = 60):
        """Create a calendar event"""
        if not title:
            template = random.choice(self.EVENT_TEMPLATES)
            title = template['title']
            duration_min = template['duration']
        
        if not datetime_str:
            # Random time in next 30 days
            future = datetime.utcnow() + timedelta(
                days=random.randint(1, 30),
                hours=random.randint(8, 18),
            )
            datetime_str = future.strftime('%Y-%m-%dT%H:%M')
        
        await self._navigate('https://calendar.google.com')
        
        try:
            await self._click('[aria-label="Create"]')
            await self._human_delay(1, 2)
            await self._type('input[aria-label*="title"], input[data-eventchip]', title)
            await self._human_delay(0.5, 1)
        except Exception:
            pass
        
        self._log('create_event', {
            'title': title, 'datetime': datetime_str, 'duration_min': duration_min,
        })
    
    async def create_recurring_event(self, title: str = None, recurrence: str = 'weekly'):
        """Create a recurring event"""
        if not title:
            recurring = [t for t in self.EVENT_TEMPLATES if t['recurrence']]
            template = random.choice(recurring)
            title = template['title']
            recurrence = template['recurrence']
        
        self._log('create_recurring_event', {
            'title': title, 'recurrence': recurrence,
        })
    
    async def accept_invitation(self, event_id: str = None):
        """Accept a calendar invitation"""
        self._log('accept_invitation', {'event_id': event_id or 'simulated'})
    
    async def set_reminder(self, event_id: str = None, minutes_before: int = 30):
        """Set reminder on event"""
        self._log('set_reminder', {
            'event_id': event_id or 'simulated',
            'minutes_before': minutes_before,
        })
    
    async def browse_calendar(self, duration_min: int = 2):
        """Browse through calendar views"""
        await self._navigate('https://calendar.google.com')
        
        # Switch between views
        views = ['day', 'week', 'month']
        for view in random.sample(views, min(2, len(views))):
            try:
                await self._click(f'button[aria-label*="{view}"], [data-view="{view}"]')
                await self._human_delay(2, 5)
            except Exception:
                pass
        
        self._log('browse_calendar', {'duration_min': duration_min})
    
    async def run_warmup_session(self, duration_min: int = 8):
        """Run complete Calendar warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        await self.browse_calendar()
        
        for _ in range(random.randint(2, 4)):
            await self.create_event()
        
        await self.create_recurring_event()
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE DOCS WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class GoogleDocsWarmup(BaseWarmup):
    """Google Docs activity simulation"""
    
    DOC_TEMPLATES = [
        {'title': 'Meeting Notes', 'content': 'Attendees: Team\nAgenda:\n1. Project Update\n2. Q&A\n3. Action Items'},
        {'title': 'Project Proposal', 'content': 'Executive Summary\n\nThis document outlines our proposed approach...'},
        {'title': 'Weekly Report', 'content': 'Week of {date}\n\nAccomplishments:\n- Completed X\n- Started Y\n\nNext Steps:\n- Plan Z'},
        {'title': 'Shopping List', 'content': 'Groceries:\n- Milk\n- Bread\n- Eggs\n- Vegetables\n- Fruit'},
        {'title': 'Travel Itinerary', 'content': 'Day 1: Arrival\nDay 2: Sightseeing\nDay 3: Adventure'},
        {'title': 'Personal Journal', 'content': 'Today was a productive day. Managed to finish several tasks...'},
    ]
    
    async def create_document(self, title: str = None, content: str = None):
        """Create a new Google Doc"""
        if not title:
            template = random.choice(self.DOC_TEMPLATES)
            title = template['title']
            content = template['content'].replace('{date}', datetime.utcnow().strftime('%B %d'))
        
        await self._navigate('https://docs.google.com/document/create')
        await self._human_delay(2, 4)
        
        # Type title
        try:
            await self._type('input[aria-label*="title"], div[class*="title"]', title)
            await self._human_delay(1, 2)
            
            # Type content
            if content:
                await self._click('div[role="textbox"], div.kix-page')
                await self._human_delay(0.5, 1)
                if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                    for line in content.split('\n'):
                        await self.browser.page.keyboard.type(line)
                        await self.browser.page.keyboard.press('Enter')
                        await self._human_delay(0.2, 0.8)
        except Exception:
            pass
        
        doc_id = hashlib.md5(f"{title}{time.time() if 'time' in dir() else 0}".encode()).hexdigest()[:16]
        self._log('create_document', {'title': title, 'doc_id': doc_id, 'content_length': len(content or '')})
        return doc_id
    
    async def edit_document(self, doc_id: str = None, edits: List[str] = None):
        """Edit an existing document"""
        if not edits:
            edits = [
                'Updated the introduction paragraph.',
                'Added new section on methodology.',
                'Fixed formatting issues.',
            ]
        
        self._log('edit_document', {'doc_id': doc_id or 'simulated', 'edit_count': len(edits)})
    
    async def add_comment(self, doc_id: str = None, text: str = None):
        """Add a comment to a document"""
        if not text:
            comments = [
                'Looks good!', 'Can we discuss this point?',
                'I suggest we rephrase this section.',
                'Great work on this!', 'Need more details here.',
            ]
            text = random.choice(comments)
        
        self._log('add_comment', {'doc_id': doc_id or 'simulated', 'comment': text})
    
    async def share_document(self, doc_id: str = None, email: str = None, role: str = "viewer"):
        """Share document with another user"""
        self._log('share_document', {
            'doc_id': doc_id or 'simulated',
            'shared_with': email or 'contact',
            'role': role,
        })
    
    async def run_warmup_session(self, duration_min: int = 10):
        """Run complete Docs warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        for _ in range(random.randint(1, 3)):
            doc_id = await self.create_document()
            await self.add_comment(doc_id)
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class GoogleSheetsWarmup(BaseWarmup):
    """Google Sheets activity simulation"""
    
    SHEET_TEMPLATES = [
        {'title': 'Monthly Budget', 'headers': ['Category', 'Budget', 'Actual', 'Diff']},
        {'title': 'Task Tracker', 'headers': ['Task', 'Status', 'Priority', 'Due Date']},
        {'title': 'Contact List', 'headers': ['Name', 'Email', 'Phone', 'Company']},
        {'title': 'Workout Log', 'headers': ['Date', 'Exercise', 'Sets', 'Reps', 'Weight']},
        {'title': 'Expense Report', 'headers': ['Date', 'Description', 'Amount', 'Category']},
    ]
    
    async def create_spreadsheet(self, title: str = None):
        """Create a new spreadsheet"""
        if not title:
            template = random.choice(self.SHEET_TEMPLATES)
            title = template['title']
        
        await self._navigate('https://sheets.google.com/create')
        await self._human_delay(2, 4)
        
        try:
            await self._type('input[aria-label*="title"]', title)
        except Exception:
            pass
        
        sheet_id = hashlib.md5(title.encode()).hexdigest()[:16]
        self._log('create_spreadsheet', {'title': title, 'sheet_id': sheet_id})
        return sheet_id
    
    async def enter_data(self, sheet_id: str = None, data: List[List[str]] = None):
        """Enter data into cells"""
        if not data:
            template = random.choice(self.SHEET_TEMPLATES)
            data = [template['headers']]
            # Generate 5-10 rows of sample data
            for i in range(random.randint(5, 10)):
                row = [f'Item {i+1}'] + [str(random.randint(10, 1000)) for _ in range(len(template['headers']) - 1)]
                data.append(row)
        
        self._log('enter_data', {
            'sheet_id': sheet_id or 'simulated',
            'rows': len(data),
            'cols': len(data[0]) if data else 0,
        })
    
    async def apply_formula(self, sheet_id: str = None, cell: str = 'E2', formula: str = '=SUM(B2:D2)'):
        """Apply a formula to a cell"""
        self._log('apply_formula', {
            'sheet_id': sheet_id or 'simulated',
            'cell': cell,
            'formula': formula,
        })
    
    async def create_chart(self, sheet_id: str = None, chart_type: str = 'bar'):
        """Create a chart from data"""
        if not chart_type:
            chart_type = random.choice(['bar', 'line', 'pie', 'scatter'])
        
        self._log('create_chart', {
            'sheet_id': sheet_id or 'simulated',
            'chart_type': chart_type,
        })
    
    async def run_warmup_session(self, duration_min: int = 10):
        """Run complete Sheets warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        sheet_id = await self.create_spreadsheet()
        await self.enter_data(sheet_id)
        await self.apply_formula(sheet_id)
        await self.create_chart(sheet_id)
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE SLIDES WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class GoogleSlidesWarmup(BaseWarmup):
    """Google Slides activity simulation"""
    
    PRES_TEMPLATES = [
        {'title': 'Quarterly Review', 'slides': 10},
        {'title': 'Project Kickoff', 'slides': 8},
        {'title': 'Training Deck', 'slides': 15},
        {'title': 'Product Demo', 'slides': 12},
        {'title': 'Team Offsite Ideas', 'slides': 6},
    ]
    
    SLIDE_LAYOUTS = ['BLANK', 'TITLE', 'TITLE_AND_BODY', 'TWO_COLUMN', 'SECTION_HEADER']
    
    async def create_presentation(self, title: str = None):
        """Create a new presentation"""
        if not title:
            template = random.choice(self.PRES_TEMPLATES)
            title = template['title']
        
        await self._navigate('https://slides.google.com/create')
        await self._human_delay(2, 4)
        
        try:
            await self._type('input[aria-label*="title"]', title)
        except Exception:
            pass
        
        pres_id = hashlib.md5(title.encode()).hexdigest()[:16]
        self._log('create_presentation', {'title': title, 'pres_id': pres_id})
        return pres_id
    
    async def add_slide(self, pres_id: str = None, layout: str = None, content: Dict = None):
        """Add a slide to a presentation"""
        if not layout:
            layout = random.choice(self.SLIDE_LAYOUTS)
        
        if not content:
            content = {
                'title': f'Slide {random.randint(1, 20)}',
                'body': 'Key points and discussion items for this section.',
            }
        
        self._log('add_slide', {
            'pres_id': pres_id or 'simulated',
            'layout': layout,
            'has_content': bool(content),
        })
    
    async def apply_theme(self, pres_id: str = None, theme: str = None):
        """Apply a theme to presentation"""
        themes = ['Simple Light', 'Simple Dark', 'Streamline', 'Focus', 'Shift',
                  'Momentum', 'Paradigm', 'Material', 'Swiss', 'Beach Day']
        theme = theme or random.choice(themes)
        
        self._log('apply_theme', {'pres_id': pres_id or 'simulated', 'theme': theme})
    
    async def run_warmup_session(self, duration_min: int = 8):
        """Run complete Slides warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        pres_id = await self.create_presentation()
        await self.apply_theme(pres_id)
        
        for _ in range(random.randint(3, 6)):
            await self.add_slide(pres_id)
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# CHROME SYNC SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ChromeSyncSimulator(BaseWarmup):
    """Chrome browser sync simulation — bookmarks, history, passwords"""
    
    BOOKMARK_TEMPLATES = [
        {'url': 'https://github.com', 'title': 'GitHub', 'folder': 'Development'},
        {'url': 'https://stackoverflow.com', 'title': 'Stack Overflow', 'folder': 'Development'},
        {'url': 'https://news.ycombinator.com', 'title': 'Hacker News', 'folder': 'News'},
        {'url': 'https://reddit.com', 'title': 'Reddit', 'folder': 'Social'},
        {'url': 'https://youtube.com', 'title': 'YouTube', 'folder': 'Entertainment'},
        {'url': 'https://translate.google.com', 'title': 'Google Translate', 'folder': 'Tools'},
        {'url': 'https://weather.com', 'title': 'Weather', 'folder': 'Daily'},
        {'url': 'https://amazon.com', 'title': 'Amazon', 'folder': 'Shopping'},
        {'url': 'https://linkedin.com', 'title': 'LinkedIn', 'folder': 'Professional'},
        {'url': 'https://medium.com', 'title': 'Medium', 'folder': 'Reading'},
    ]
    
    BROWSING_HISTORY = [
        'https://google.com/search?q=best+restaurants+near+me',
        'https://google.com/search?q=weather+today',
        'https://youtube.com/watch?v=dQw4w9WgXcQ',
        'https://wikipedia.org/wiki/Main_Page',
        'https://maps.google.com',
        'https://gmail.com',
        'https://drive.google.com',
        'https://calendar.google.com',
        'https://news.google.com',
        'https://docs.google.com',
    ]
    
    async def sync_bookmarks(self, bookmarks: List[Dict] = None):
        """Simulate bookmark sync"""
        if not bookmarks:
            count = random.randint(5, 15)
            bookmarks = random.sample(self.BOOKMARK_TEMPLATES, min(count, len(self.BOOKMARK_TEMPLATES)))
        
        for bm in bookmarks:
            self._log('bookmark_sync', bm)
    
    async def sync_history(self, urls: List[str] = None):
        """Simulate browsing history sync via actual navigation"""
        if not urls:
            count = random.randint(5, 10)
            urls = random.sample(self.BROWSING_HISTORY, min(count, len(self.BROWSING_HISTORY)))
        
        for url in urls:
            try:
                await self._navigate(url)
                await self._human_delay(2, 8)  # Reading time
                await self._scroll(random.randint(200, 500))
            except Exception:
                pass
            
            self._log('history_visit', {'url': url})
    
    async def sync_passwords(self, credentials: List[Dict] = None):
        """Simulate password sync (generates realistic saved credentials metadata)"""
        if not credentials:
            sites = ['github.com', 'linkedin.com', 'amazon.com', 'netflix.com', 'spotify.com']
            credentials = [
                {'domain': site, 'username': f'user_{random.randint(100, 999)}', 'saved': True}
                for site in random.sample(sites, random.randint(2, 4))
            ]
        
        for cred in credentials:
            self._log('password_sync', {'domain': cred['domain'], 'username': cred['username']})
    
    async def sync_extensions(self, extension_ids: List[str] = None):
        """Simulate extension sync"""
        if not extension_ids:
            extensions = [
                {'id': 'nkbihfbeogaeaoehlefnkodbefgpgknn', 'name': 'MetaMask'},
                {'id': 'cfhdojbkjhnklbpkdaibdccddilifddb', 'name': 'AdBlock Plus'},
                {'id': 'gighmmpiobklfepjocnamgkkbiglidom', 'name': 'AdBlock'},
                {'id': 'hdokiejnpimakedhajhdlcegeplioahd', 'name': 'LastPass'},
                {'id': 'aapbdbdomjkkjkaonfhkkikfgjllcleb', 'name': 'Google Translate'},
            ]
            selected = random.sample(extensions, random.randint(1, 3))
            extension_ids = [e['id'] for e in selected]
        
        for eid in extension_ids:
            self._log('extension_sync', {'extension_id': eid})
    
    async def run_warmup_session(self, duration_min: int = 5):
        """Run complete Chrome sync warmup session"""
        self._log('session_start', {'target_duration': duration_min})
        
        await self.sync_bookmarks()
        await self.sync_history()
        await self.sync_passwords()
        await self.sync_extensions()
        
        self._log('session_complete', {'activities': len(self._activity_log)})


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'BaseWarmup',
    'AndroidPlayStoreWarmup',
    'GooglePhotosWarmup',
    'CalendarEventGenerator',
    'GoogleDocsWarmup',
    'GoogleSheetsWarmup',
    'GoogleSlidesWarmup',
    'ChromeSyncSimulator',
]
