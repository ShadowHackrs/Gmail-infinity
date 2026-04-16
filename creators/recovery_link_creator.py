#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RECOVERY_LINK_CREATOR.PY - v2026.∞                       ║
║              Child Account Creator via Google Family Link                   ║
║              Bypasses Phone Verification (COPPA)                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path

from playwright.async_api import async_playwright
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity.persona_generator import PersonaGenerator, HumanPersona
from creators.web_creator import GmailAccount


class FamilyLinkCreator:
    """
    Create child Gmail accounts via Google Family Link
    No phone verification required (COPPA compliance)
    Requires one verified "parent" Gmail account
    """
    
    def __init__(
        self,
        parent_email: str,
        parent_password: str,
        headless: bool = False,
        output_dir: str = "./family_accounts",
        verbose: bool = True
    ):
        """
        Initialize Family Link Creator with parent account
        """
        self.parent_email = parent_email
        self.parent_password = parent_password
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        self.persona_generator = PersonaGenerator()
        self.created_accounts = []
    
    async def login_parent_account(self, page) -> bool:
        """
        Login to parent Gmail account
        """
        if self.verbose:
            print(f"🔐 Logging in as parent: {self.parent_email}")
        
        # Navigate to Gmail
        await page.goto('https://mail.google.com')
        await asyncio.sleep(2)
        
        # Enter email
        await page.fill('input[type="email"]', self.parent_email)
        await page.click('#identifierNext')
        await asyncio.sleep(3)
        
        # Enter password
        await page.fill('input[type="password"]', self.parent_password)
        await page.click('#passwordNext')
        await asyncio.sleep(5)
        
        # Check for successful login
        try:
            await page.wait_for_selector('div[role="main"]', timeout=10000)
            if self.verbose:
                print("✅ Parent login successful")
            return True
        except:
            if self.verbose:
                print("❌ Parent login failed")
            return False
    
    async def navigate_to_family_link(self, page) -> bool:
        """
        Navigate to Google Family Link
        """
        await page.goto('https://families.google.com/familylink/')
        await asyncio.sleep(3)
        
        # Click "Get started" or "Sign in"
        try:
            get_started = await page.query_selector('text="Get started", text="Sign in"')
            if get_started:
                await get_started.click()
                await asyncio.sleep(3)
        except:
            pass
        
        return True
    
    async def create_child_account(
        self,
        page,
        child_persona: HumanPersona
    ) -> Optional[GmailAccount]:
        """
        Create a child account under Family Link
        """
        if self.verbose:
            print(f"🧒 Creating child account for {child_persona.first_name}")
        
        # Click "Create account for child"
        try:
            create_child = await page.wait_for_selector(
                'text="Create account", text="Add child", [aria-label*="child"]',
                timeout=10000
            )
            await create_child.click()
            await asyncio.sleep(2)
        except:
            # Alternative: Find "Add" button
            add_btn = await page.query_selector('button:has-text("Add"), a:has-text("Add")')
            if add_btn:
                await add_btn.click()
                await asyncio.sleep(2)
        
        # Enter child's first name
        await page.fill('input[name="firstName"]', child_persona.first_name)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Enter child's last name
        await page.fill('input[name="lastName"]', child_persona.last_name)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Enter birthday (child must be under 13)
        # Set age between 7-12
        child_birth_year = datetime.now().year - random.randint(7, 12)
        
        # Select month
        await page.select_option('select[id="month"], select[aria-label*="Month"]', 
                                value=str(child_persona.birth_month))
        await asyncio.sleep(0.5)
        
        # Enter day
        await page.fill('input[id="day"], input[aria-label*="Day"]', 
                       str(child_persona.birth_day))
        await asyncio.sleep(0.5)
        
        # Enter year
        await page.fill('input[id="year"], input[aria-label*="Year"]', 
                       str(child_birth_year))
        await asyncio.sleep(0.5)
        
        # Select gender
        gender_value = '1' if child_persona.gender == 'male' else '2'
        await page.select_option('select[id="gender"], select[aria-label*="Gender"]', 
                                value=gender_value)
        await asyncio.sleep(0.5)
        
        # Click Next
        next_button = await page.wait_for_selector('button:has-text("Next"), button[jsname="LgbsSe"]')
        await next_button.click()
        await asyncio.sleep(3)
        
        # Choose Gmail address
        # Generate username from name
        base_username = f"{child_persona.first_name.lower()}.{child_persona.last_name.lower()}"
        base_username = re.sub(r'[^a-z0-9.]', '', base_username)
        
        username = base_username
        try:
            username_input = await page.wait_for_selector('input[type="email"], input[name="Username"]', 
                                                          timeout=5000)
            await username_input.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await page.fill('input[type="email"], input[name="Username"]', username)
            await asyncio.sleep(2)
            
            # Check if available
            try:
                await page.wait_for_selector('span:has-text("is available")', timeout=2000)
            except:
                # Try with random suffix
                username = f"{base_username}{random.randint(100, 999)}"
                await page.fill('input[type="email"], input[name="Username"]', username)
                await asyncio.sleep(2)
        except:
            pass
        
        email = f"{username}@gmail.com"
        
        # Click Next
        await next_button.click()
        await asyncio.sleep(3)
        
        # Create password
        # Generate secure password for child account
        password = child_persona.password
        
        await page.fill('input[name="Passwd"]', password)
        await asyncio.sleep(0.5)
        await page.fill('input[name="ConfirmPasswd"]', password)
        await asyncio.sleep(0.5)
        
        # Click Next
        await next_button.click()
        await asyncio.sleep(3)
        
        # Review and consent screen
        try:
            # Check "I agree" or consent box
            agree_checkbox = await page.query_selector('input[type="checkbox"]')
            if agree_checkbox:
                await agree_checkbox.check()
                await asyncio.sleep(0.5)
            
            # Click "I agree" or "Accept"
            accept_btn = await page.wait_for_selector(
                'button:has-text("I agree"), button:has-text("Accept"), button:has-text("Create account")',
                timeout=5000
            )
            await accept_btn.click()
            await asyncio.sleep(5)
        except:
            pass
        
        # Parental consent
        try:
            # For COPPA, Google requires parental consent
            # This is usually just clicking "I'm the parent" or similar
            parent_consent = await page.wait_for_selector(
                'button:has-text("I am the parent"), button:has-text("Confirm")',
                timeout=5000
            )
            if parent_consent:
                await parent_consent.click()
                await asyncio.sleep(3)
        except:
            pass
        
        # Account created successfully
        account = GmailAccount(
            email=email,
            password=password,
            first_name=child_persona.first_name,
            last_name=child_persona.last_name,
            birthday=f"{child_birth_year}-{child_persona.birth_month:02d}-{child_persona.birth_day:02d}",
            gender=child_persona.gender,
            phone_number=None,  # No phone verification for children
            recovery_email=self.parent_email,  # Parent email as recovery
            status="child_account",
            created_at=datetime.utcnow().isoformat()
        )
        
        if self.verbose:
            print(f"✅ Child account created: {email}")
        
        return account
    
    async def create_accounts(
        self,
        count: int = 5,
        age_range: Tuple[int, int] = (7, 12)
    ) -> List[GmailAccount]:
        """
        Create multiple child accounts via Family Link
        """
        if self.verbose:
            print(f"\n👪 Google Family Link Account Creation")
            print(f"   Parent: {self.parent_email}")
            print(f"   Child accounts: {count}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Login to parent account
                if not await self.login_parent_account(page):
                    raise Exception("Parent login failed")
                
                # Navigate to Family Link
                await self.navigate_to_family_link(page)
                
                accounts = []
                
                for i in range(count):
                    if self.verbose:
                        print(f"\n📋 Creating account {i+1}/{count}")
                    
                    # Generate child persona
                    child_age = random.randint(age_range[0], age_range[1])
                    birth_year = datetime.now().year - child_age
                    birth_month = random.randint(1, 12)
                    birth_day = random.randint(1, 28)
                    
                    child_persona = HumanPersona(
                        first_name=await self._generate_child_name(),
                        last_name=await self._generate_child_name(last=True),
                        birth_year=birth_year,
                        birth_month=birth_month,
                        birth_day=birth_day,
                        gender=random.choice(['male', 'female']),
                        password=self._generate_child_password()
                    )
                    
                    # Create account
                    account = await self.create_child_account(page, child_persona)
                    
                    if account:
                        accounts.append(account)
                        self.created_accounts.append(account)
                        
                        # Save after each success
                        await self.save_accounts()
                    
                    # Wait between creations
                    if i < count - 1:
                        await asyncio.sleep(random.uniform(3, 7))
                
                return accounts
                
            finally:
                await browser.close()
    
    async def _generate_child_name(self, last: bool = False) -> str:
        """Generate realistic child name"""
        first_names_male = [
            'Liam', 'Noah', 'Oliver', 'Elijah', 'James', 'William', 'Benjamin',
            'Lucas', 'Henry', 'Alexander', 'Mason', 'Michael', 'Ethan', 'Daniel',
            'Jacob', 'Logan', 'Jackson', 'Levi', 'Sebastian', 'Mateo', 'Jack',
            'Owen', 'Theodore', 'Aiden', 'Samuel', 'Joseph', 'John', 'David',
            'Wyatt', 'Matthew', 'Luke', 'Asher', 'Carter', 'Julian', 'Grayson'
        ]
        
        first_names_female = [
            'Olivia', 'Emma', 'Charlotte', 'Amelia', 'Sophia', 'Isabella', 'Mia',
            'Evelyn', 'Harper', 'Camila', 'Gianna', 'Abigail', 'Luna', 'Ella',
            'Elizabeth', 'Sofia', 'Emily', 'Avery', 'Mila', 'Aria', 'Scarlett',
            'Penelope', 'Layla', 'Chloe', 'Victoria', 'Madison', 'Eleanor', 'Grace',
            'Nora', 'Riley', 'Zoey', 'Hannah', 'Hazel', 'Lily', 'Ellie', 'Violet'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green'
        ]
        
        if last:
            return random.choice(last_names)
        else:
            return random.choice(first_names_male + first_names_female)
    
    def _generate_child_password(self) -> str:
        """Generate secure password for child account"""
        words = ['Sun', 'Moon', 'Star', 'Sky', 'Blue', 'Red', 'Happy', 'Fun', 
                 'Play', 'Game', 'Cool', 'Nice', 'Brave', 'Smart', 'Kind']
        
        word = random.choice(words)
        number = random.randint(10, 999)
        symbol = random.choice(['!', '@', '#', '$', '%'])
        
        password = f"{word}{number}{symbol}"
        
        # Ensure it meets Google's requirements
        if len(password) < 8:
            password += random.choice(words)
        
        return password
    
    async def save_accounts(self):
        """Save created child accounts"""
        accounts_file = self.output_dir / f"family_link_{self.parent_email}.json"
        
        with open(accounts_file, 'w') as f:
            json.dump([acc.to_dict() for acc in self.created_accounts], f, indent=2)


# ============================================================================
# MAIN EXPORTS
# ============================================================================

__all__ = [
    'WebGmailCreator',
    'AndroidEmulatorCreator',
    'GoogleWorkspaceCreator',
    'FamilyLinkCreator'
]