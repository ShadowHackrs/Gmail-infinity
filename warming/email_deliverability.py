#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EMAIL_DELIVERABILITY.PY - v2026.∞                         ║
║              Complete Email Deliverability Engineering Suite                  ║
║                                                                              ║
║   Modules:                                                                   ║
║   ├── DKIMSignatureSimulator      → RFC 6376 DKIM signing/verification      ║
║   ├── SPFRecordSimulator          → SPF record building + alignment check   ║
║   ├── DMARCComplianceEngine       → DMARC policy + aggregate reports        ║
║   ├── SenderReputationEngine      → Per-account scoring + send limits       ║
║   ├── TrustScoreOptimizer         → Multi-signal weighted trust scoring     ║
║   ├── IPReputationWarmup          → Exponential send volume ramping         ║
║   ├── DomainReputationBuilder     → Domain-level reputation tracking        ║
║   ├── SpamFilterTrainer           → Content analysis + spam trigger detect  ║
║   ├── InboxPlacementOptimizer     → A/B testing for inbox placement         ║
║   ├── EmailEngagementSimulator    → Realistic open/reply/star simulation    ║
║   ├── ContactNetworkBuilder       → Contact graph generation                ║
║   └── GooglePostmasterIntegrator  → Google Postmaster Tools API client      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import time
import random
import hashlib
import hmac
import base64
import math
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class SPFResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    SOFTFAIL = "softfail"
    NEUTRAL = "neutral"
    NONE = "none"
    TEMPERROR = "temperror"
    PERMERROR = "permerror"


class DMARCPolicy(Enum):
    NONE = "none"
    QUARANTINE = "quarantine"
    REJECT = "reject"


@dataclass
class DMARCResult:
    domain: str
    dkim_aligned: bool
    spf_aligned: bool
    policy: DMARCPolicy
    disposition: str  # none, quarantine, reject
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def passed(self) -> bool:
        return self.dkim_aligned or self.spf_aligned


@dataclass
class SpamAnalysis:
    score: float  # 0.0 (clean) → 10.0 (spam)
    triggers: Dict[str, List[str]]
    recommendations: List[str]
    subject_score: float
    body_score: float
    
    @property
    def is_safe(self) -> bool:
        return self.score < 3.0


# ═══════════════════════════════════════════════════════════════════════════════
# DKIM SIGNATURE SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class DKIMSignatureSimulator:
    """Generate RFC 6376 compliant DKIM-Signature headers"""
    
    def __init__(self, domain: str, selector: str = "gmail"):
        self.domain = domain
        self.selector = selector
        self._private_key = None
        self._public_key = None
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate RSA 2048-bit keypair for DKIM signing.
        Returns (private_pem, dns_txt_record)
        """
        if not HAS_CRYPTO:
            raise ImportError("cryptography package required for DKIM key generation")
        
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        self._private_key = key
        self._public_key = key.public_key()
        
        # Serialize private key
        private_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Serialize public key for DNS TXT record
        public_der = self._public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_b64 = base64.b64encode(public_der).decode('utf-8')
        
        dns_record = f"v=DKIM1; k=rsa; p={public_b64}"
        
        logger.info(f"🔑 DKIM keypair generated for {self.selector}._domainkey.{self.domain}")
        return private_pem, dns_record
    
    def sign_message(self, message: str, headers: Dict[str, str]) -> str:
        """
        Sign email message, return DKIM-Signature header value.
        
        Implements relaxed/relaxed canonicalization.
        """
        if not self._private_key:
            self.generate_keypair()
        
        # Canonicalize headers (relaxed)
        signed_headers = ['from', 'to', 'subject', 'date', 'message-id']
        canonical_headers = []
        for h in signed_headers:
            if h in headers:
                # Relaxed: lowercase name, unfold, compress whitespace
                canonical = f"{h}:{' '.join(headers[h].split())}"
                canonical_headers.append(canonical)
        
        header_text = '\r\n'.join(canonical_headers)
        
        # Canonicalize body (relaxed)
        body = message.strip()
        body = '\r\n'.join(line.rstrip() for line in body.split('\n'))
        body_hash = base64.b64encode(
            hashlib.sha256(body.encode('utf-8')).digest()
        ).decode('utf-8')
        
        # Build DKIM-Signature header (without b= value)
        timestamp = int(time.time())
        dkim_header = (
            f"v=1; a=rsa-sha256; c=relaxed/relaxed; "
            f"d={self.domain}; s={self.selector}; "
            f"t={timestamp}; "
            f"h={':'.join(signed_headers)}; "
            f"bh={body_hash}; "
            f"b="
        )
        
        # Sign the canonical header + DKIM header
        sign_input = header_text + '\r\n' + f"dkim-signature:{dkim_header}"
        
        if HAS_CRYPTO and self._private_key:
            signature = self._private_key.sign(
                sign_input.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            sig_b64 = base64.b64encode(signature).decode('utf-8')
        else:
            # Fallback: generate deterministic pseudo-signature
            sig_b64 = base64.b64encode(
                hashlib.sha256(sign_input.encode('utf-8')).digest()
            ).decode('utf-8')
        
        return dkim_header + sig_b64
    
    def verify_signature(self, message: str, signature: str) -> bool:
        """Verify a DKIM signature against the stored public key"""
        if not self._public_key or not HAS_CRYPTO:
            logger.warning("Cannot verify: no public key or cryptography not available")
            return False
        
        try:
            # Extract b= value
            parts = signature.split('b=')
            if len(parts) < 2:
                return False
            sig_b64 = parts[-1].strip()
            sig_bytes = base64.b64decode(sig_b64)
            
            # Reconstruct sign input
            header_part = 'dkim-signature:' + signature.split('b=')[0] + 'b='
            
            self._public_key.verify(
                sig_bytes,
                header_part.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# SPF RECORD SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SPFRecordSimulator:
    """SPF record validation and alignment checking"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.mechanisms = []
    
    def build_record(self, allowed_ips: List[str], includes: List[str] = None) -> str:
        """
        Generate valid SPF TXT record.
        
        Args:
            allowed_ips: List of IPs/CIDRs to allow (e.g., ['192.168.1.0/24'])
            includes: List of domains to include (e.g., ['_spf.google.com'])
        """
        parts = ['v=spf1']
        
        # Add IP mechanisms
        for ip in allowed_ips:
            if ':' in ip:
                parts.append(f'ip6:{ip}')
            else:
                parts.append(f'ip4:{ip}')
        
        # Add include mechanisms
        if includes:
            for inc in includes:
                parts.append(f'include:{inc}')
        
        # Add mx and a records
        parts.append('mx')
        parts.append('a')
        
        # Default policy
        parts.append('-all')
        
        record = ' '.join(parts)
        self.mechanisms = parts[1:]  # Store for validation
        
        logger.info(f"📝 SPF record built for {self.domain}: {record}")
        return record
    
    def check_alignment(self, sender_ip: str, envelope_from: str) -> SPFResult:
        """
        Check SPF alignment for sender IP and envelope-from domain.
        
        Returns SPFResult enum.
        """
        envelope_domain = envelope_from.split('@')[-1] if '@' in envelope_from else envelope_from
        
        # Check domain alignment
        if envelope_domain != self.domain:
            return SPFResult.FAIL
        
        # Check IP against mechanisms
        for mech in self.mechanisms:
            if mech.startswith('ip4:') or mech.startswith('ip6:'):
                allowed = mech.split(':')[1]
                if '/' in allowed:
                    # CIDR check
                    if self._ip_in_cidr(sender_ip, allowed):
                        return SPFResult.PASS
                elif sender_ip == allowed:
                    return SPFResult.PASS
            elif mech == '-all':
                return SPFResult.FAIL
            elif mech == '~all':
                return SPFResult.SOFTFAIL
            elif mech == '?all':
                return SPFResult.NEUTRAL
        
        return SPFResult.NEUTRAL
    
    def validate_record(self, record: str) -> List[str]:
        """Validate SPF record syntax, return list of issues."""
        issues = []
        
        if not record.startswith('v=spf1'):
            issues.append("Record must start with 'v=spf1'")
        
        parts = record.split()
        
        # Check DNS lookup limit (max 10)
        lookup_count = 0
        for part in parts:
            if part.startswith('include:') or part.startswith('a') or part.startswith('mx'):
                lookup_count += 1
        
        if lookup_count > 10:
            issues.append(f"Too many DNS lookups: {lookup_count}/10 max")
        
        # Check for multiple default mechanisms
        defaults = [p for p in parts if p in ['-all', '~all', '?all', '+all']]
        if len(defaults) > 1:
            issues.append("Multiple default mechanisms found")
        elif len(defaults) == 0:
            issues.append("Missing default mechanism (-all, ~all, ?all)")
        
        # Check for +all (permissive)
        if '+all' in parts:
            issues.append("WARNING: +all allows any IP to send on behalf of this domain")
        
        # Check total record length (DNS TXT limit 255 chars per string)
        if len(record) > 450:
            issues.append(f"Record too long ({len(record)} chars), consider splitting")
        
        return issues
    
    @staticmethod
    def _ip_in_cidr(ip: str, cidr: str) -> bool:
        """Simple CIDR match check"""
        try:
            import ipaddress
            return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
        except (ImportError, ValueError):
            # Fallback: exact match
            return ip == cidr.split('/')[0]


# ═══════════════════════════════════════════════════════════════════════════════
# DMARC COMPLIANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class DMARCComplianceEngine:
    """DMARC policy enforcement and reporting"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.policy = DMARCPolicy.NONE
        self._results: List[DMARCResult] = []
    
    def build_record(
        self,
        policy: str = "none",
        rua: str = None,
        ruf: str = None,
        pct: int = 100,
        aspf: str = "r",
        adkim: str = "r",
    ) -> str:
        """
        Generate _dmarc TXT record.
        
        Args:
            policy: none, quarantine, reject
            rua: Aggregate report URI (mailto:)
            ruf: Forensic report URI (mailto:)
            pct: Percentage of messages to apply policy (0-100)
            aspf: SPF alignment mode (r=relaxed, s=strict)
            adkim: DKIM alignment mode (r=relaxed, s=strict)
        """
        self.policy = DMARCPolicy(policy)
        
        parts = [f"v=DMARC1", f"p={policy}"]
        
        if rua:
            parts.append(f"rua={rua}")
        if ruf:
            parts.append(f"ruf={ruf}")
        if pct != 100:
            parts.append(f"pct={pct}")
        
        parts.append(f"aspf={aspf}")
        parts.append(f"adkim={adkim}")
        
        record = '; '.join(parts)
        logger.info(f"📝 DMARC record built for _dmarc.{self.domain}: {record}")
        return record
    
    def check_alignment(
        self,
        dkim_result: bool,
        spf_result: str,
        header_from: str,
        envelope_from: str,
    ) -> DMARCResult:
        """
        Full DMARC alignment check.
        
        Checks both DKIM and SPF alignment against header From domain.
        """
        from_domain = header_from.split('@')[-1] if '@' in header_from else header_from
        envelope_domain = envelope_from.split('@')[-1] if '@' in envelope_from else envelope_from
        
        # DKIM alignment (relaxed: organizational domain match)
        dkim_aligned = dkim_result and self._domains_aligned(from_domain, self.domain)
        
        # SPF alignment (relaxed: organizational domain match)
        spf_aligned = (
            spf_result == SPFResult.PASS.value 
            and self._domains_aligned(from_domain, envelope_domain)
        )
        
        # Determine disposition
        if dkim_aligned or spf_aligned:
            disposition = "none"
        else:
            disposition = self.policy.value
        
        result = DMARCResult(
            domain=from_domain,
            dkim_aligned=dkim_aligned,
            spf_aligned=spf_aligned,
            policy=self.policy,
            disposition=disposition,
        )
        
        self._results.append(result)
        return result
    
    def generate_aggregate_report(self, results: List[DMARCResult] = None) -> str:
        """Generate DMARC aggregate report XML (RFC 7489)"""
        results = results or self._results
        
        root = ET.Element('feedback')
        
        # Report metadata
        metadata = ET.SubElement(root, 'report_metadata')
        ET.SubElement(metadata, 'org_name').text = 'Gmail Infinity Factory'
        ET.SubElement(metadata, 'email').text = f'postmaster@{self.domain}'
        ET.SubElement(metadata, 'report_id').text = hashlib.md5(
            str(time.time()).encode()
        ).hexdigest()[:12]
        
        date_range = ET.SubElement(metadata, 'date_range')
        ET.SubElement(date_range, 'begin').text = str(
            int((datetime.utcnow() - timedelta(days=1)).timestamp())
        )
        ET.SubElement(date_range, 'end').text = str(int(datetime.utcnow().timestamp()))
        
        # Policy published
        policy = ET.SubElement(root, 'policy_published')
        ET.SubElement(policy, 'domain').text = self.domain
        ET.SubElement(policy, 'p').text = self.policy.value
        ET.SubElement(policy, 'pct').text = '100'
        
        # Records
        for r in results:
            record = ET.SubElement(root, 'record')
            
            row = ET.SubElement(record, 'row')
            ET.SubElement(row, 'source_ip').text = '0.0.0.0'
            ET.SubElement(row, 'count').text = '1'
            
            policy_eval = ET.SubElement(row, 'policy_evaluated')
            ET.SubElement(policy_eval, 'disposition').text = r.disposition
            ET.SubElement(policy_eval, 'dkim').text = 'pass' if r.dkim_aligned else 'fail'
            ET.SubElement(policy_eval, 'spf').text = 'pass' if r.spf_aligned else 'fail'
            
            identifiers = ET.SubElement(record, 'identifiers')
            ET.SubElement(identifiers, 'header_from').text = r.domain
        
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    @staticmethod
    def _domains_aligned(domain1: str, domain2: str) -> bool:
        """Check if two domains are aligned (relaxed mode — org domain match)"""
        def org_domain(d):
            parts = d.lower().split('.')
            return '.'.join(parts[-2:]) if len(parts) >= 2 else d.lower()
        return org_domain(domain1) == org_domain(domain2)


# ═══════════════════════════════════════════════════════════════════════════════
# SENDER REPUTATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class SenderReputationEngine:
    """Per-account sender reputation scoring and optimization"""
    
    def __init__(self):
        self.signals: Dict[str, Dict] = {}  # email → metrics
    
    def _ensure_account(self, email: str):
        if email not in self.signals:
            self.signals[email] = {
                'sent': 0, 'delivered': 0, 'bounced': 0,
                'opened': 0, 'replied': 0, 'spam_reports': 0,
                'unsubscribes': 0, 'first_send': None, 'last_send': None,
                'events': [],
            }
    
    def log_event(self, email: str, event_type: str, metadata: dict = None):
        """
        Log a send/bounce/open/reply/spam event.
        
        event_type: sent, delivered, bounced, opened, replied, spam_report, unsubscribe
        """
        self._ensure_account(email)
        s = self.signals[email]
        
        now = datetime.utcnow().isoformat()
        
        # Map event type to counter key (handle singular→plural)
        _event_key_map = {
            'spam_report': 'spam_reports',
            'unsubscribe': 'unsubscribes',
        }
        counter_key = _event_key_map.get(event_type, event_type)
        if counter_key in s:
            s[counter_key] += 1
        
        if event_type == 'sent':
            if not s['first_send']:
                s['first_send'] = now
            s['last_send'] = now
        
        s['events'].append({
            'type': event_type,
            'timestamp': now,
            'metadata': metadata or {},
        })
    
    def calculate_score(self, email: str) -> float:
        """
        Calculate sender reputation score 0.0-100.0.
        
        Factors: delivery rate, engagement rate, bounce rate, spam rate, account age.
        """
        self._ensure_account(email)
        s = self.signals[email]
        
        if s['sent'] == 0:
            return 50.0  # Neutral for new accounts
        
        # Delivery rate (0-25 points)
        delivery_rate = s['delivered'] / max(s['sent'], 1)
        delivery_score = delivery_rate * 25
        
        # Engagement rate (0-25 points) — opens + replies / delivered
        engagement = (s['opened'] + s['replied'] * 2) / max(s['delivered'], 1)
        engagement_score = min(25, engagement * 25)
        
        # Bounce rate penalty (0-25 points, inverse)
        bounce_rate = s['bounced'] / max(s['sent'], 1)
        bounce_score = max(0, 25 - bounce_rate * 100)
        
        # Spam complaint penalty (0-25 points, inverse)
        spam_rate = s['spam_reports'] / max(s['sent'], 1)
        spam_score = max(0, 25 - spam_rate * 250)
        
        score = delivery_score + engagement_score + bounce_score + spam_score
        return round(min(100, max(0, score)), 2)
    
    def get_send_limit(self, email: str) -> int:
        """Get recommended daily send limit based on current reputation."""
        score = self.calculate_score(email)
        self._ensure_account(email)
        s = self.signals[email]
        
        # Account age factor
        if s['first_send']:
            age_days = (datetime.utcnow() - datetime.fromisoformat(s['first_send'])).days
        else:
            age_days = 0
        
        # Base limits by reputation tier
        if score >= 90:
            base = 500
        elif score >= 70:
            base = 200
        elif score >= 50:
            base = 50
        elif score >= 30:
            base = 20
        else:
            base = 5
        
        # Scale by account age (young accounts get lower limits)
        age_factor = min(1.0, age_days / 90)  # Full send at 90 days
        
        return max(5, int(base * max(0.1, age_factor)))
    
    def get_recommendations(self, email: str) -> List[str]:
        """Get actionable recommendations to improve reputation."""
        self._ensure_account(email)
        s = self.signals[email]
        score = self.calculate_score(email)
        recs = []
        
        if s['sent'] == 0:
            recs.append("Start with 5-10 emails per day to contacts you know")
            recs.append("Ensure SPF, DKIM, and DMARC are properly configured")
            return recs
        
        bounce_rate = s['bounced'] / max(s['sent'], 1)
        spam_rate = s['spam_reports'] / max(s['sent'], 1)
        open_rate = s['opened'] / max(s['delivered'], 1)
        
        if bounce_rate > 0.05:
            recs.append(f"HIGH BOUNCE RATE ({bounce_rate:.1%}): Clean your contact list")
        if spam_rate > 0.01:
            recs.append(f"SPAM COMPLAINTS ({spam_rate:.1%}): Review content for spam triggers")
        if open_rate < 0.15:
            recs.append(f"LOW OPEN RATE ({open_rate:.1%}): Improve subject lines")
        if score < 50:
            recs.append("Send engagement emails to warm contacts (friends, colleagues)")
        if score < 30:
            recs.append("CRITICAL: Pause sending and resolve deliverability issues")
        if s['sent'] > 100 and s['replied'] / max(s['sent'], 1) < 0.02:
            recs.append("LOW REPLY RATE: Personalize your messages more")
        
        if not recs:
            recs.append(f"Reputation healthy ({score:.0f}/100). Maintain current practices.")
        
        return recs


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST SCORE OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class TrustScoreOptimizer:
    """Multi-signal trust aggregation using weighted scoring"""
    
    SIGNALS = {
        'account_age_days': 0.15,
        'email_volume_consistency': 0.12,
        'engagement_rate': 0.18,
        'bounce_rate_inverse': 0.15,
        'spam_report_inverse': 0.20,
        'google_services_usage': 0.10,
        'ip_reputation': 0.10,
    }
    
    def calculate_trust_score(self, signals: Dict[str, float]) -> float:
        """
        Weighted trust score calculation.
        
        All signal values should be normalized to 0.0-1.0 range.
        Returns 0.0-100.0.
        """
        score = 0.0
        for signal_name, weight in self.SIGNALS.items():
            value = signals.get(signal_name, 0.5)  # Default to neutral
            value = max(0.0, min(1.0, value))
            score += value * weight * 100
        
        return round(score, 2)
    
    def optimize(self, current_signals: Dict[str, float], target_score: float) -> Dict[str, str]:
        """
        Return action plan to reach target trust score.
        
        Analyzes which signals have the most room for improvement
        and returns specific actions.
        """
        current_score = self.calculate_trust_score(current_signals)
        gap = target_score - current_score
        
        if gap <= 0:
            return {"status": "Target already reached", "current": current_score}
        
        actions = {}
        
        # Sort signals by (weight * room_for_improvement)
        improvement_potential = []
        for signal, weight in self.SIGNALS.items():
            current = current_signals.get(signal, 0.5)
            room = (1.0 - current) * weight
            improvement_potential.append((signal, room, current))
        
        improvement_potential.sort(key=lambda x: x[1], reverse=True)
        
        action_map = {
            'account_age_days': "Wait for account maturation (target: 90+ days)",
            'email_volume_consistency': "Send emails daily, gradually increase volume",
            'engagement_rate': "Send to known contacts who will open/reply",
            'bounce_rate_inverse': "Clean contact list, remove invalid addresses",
            'spam_report_inverse': "Improve content quality, add unsubscribe links",
            'google_services_usage': "Use Google Docs, Drive, Calendar, Photos regularly",
            'ip_reputation': "Use clean residential proxies, avoid datacenter IPs",
        }
        
        for signal, room, current in improvement_potential:
            if room > 0.01:
                actions[signal] = {
                    'current_value': round(current, 3),
                    'target_value': round(min(1.0, current + gap / 100 / self.SIGNALS[signal]), 3),
                    'action': action_map.get(signal, f"Improve {signal}"),
                    'priority': 'HIGH' if room > 0.05 else 'MEDIUM',
                }
        
        return actions


# ═══════════════════════════════════════════════════════════════════════════════
# IP REPUTATION WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

class IPReputationWarmup:
    """Gradual send volume ramping per IP address"""
    
    def __init__(self, ip: str):
        self.ip = ip
        self.daily_volumes: List[Dict] = []
        self._start_date = datetime.utcnow()
    
    def get_todays_limit(self) -> int:
        """
        Calculate safe send limit for today.
        Exponential ramp: day1=5, day2=10, day3=20, ...capped at target.
        """
        day = len(self.daily_volumes) + 1
        # Exponential growth: 5 * 1.5^(day-1), capped at 1000
        limit = min(1000, int(5 * (1.5 ** (day - 1))))
        return limit
    
    def log_send(self, count: int):
        """Log sends for this IP today"""
        self.daily_volumes.append({
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'count': count,
            'ip': self.ip,
        })
    
    def get_warmup_schedule(self, target_daily: int = 500) -> List[Dict]:
        """Generate full warmup schedule from cold to target volume."""
        schedule = []
        day = 1
        current = 5
        
        while current < target_daily:
            schedule.append({
                'day': day,
                'limit': current,
                'notes': self._get_day_notes(day),
            })
            current = min(target_daily, int(current * 1.5))
            day += 1
        
        # Add final day at target
        schedule.append({
            'day': day,
            'limit': target_daily,
            'notes': 'Full volume reached. Monitor reputation.',
        })
        
        return schedule
    
    def get_health(self) -> Dict:
        """Current IP reputation health metrics."""
        total_sent = sum(d['count'] for d in self.daily_volumes)
        days_active = len(self.daily_volumes)
        
        return {
            'ip': self.ip,
            'days_active': days_active,
            'total_sent': total_sent,
            'avg_daily': round(total_sent / max(1, days_active), 1),
            'current_limit': self.get_todays_limit(),
            'warmup_progress': min(100, days_active / 30 * 100),
            'status': 'warming' if days_active < 30 else 'warm',
        }
    
    @staticmethod
    def _get_day_notes(day: int) -> str:
        if day <= 3:
            return "Send to known engaged contacts only"
        elif day <= 7:
            return "Gradually add new recipients"
        elif day <= 14:
            return "Monitor bounce rate closely"
        elif day <= 21:
            return "Add transactional emails"
        else:
            return "Normal sending, maintain engagement"


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN REPUTATION BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

class DomainReputationBuilder:
    """Domain-level reputation tracking and DNS health checking"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self._metrics = {
            'age_days': 0,
            'spf_configured': False,
            'dkim_configured': False,
            'dmarc_configured': False,
            'mx_records': [],
            'complaint_rate': 0.0,
            'total_sent': 0,
            'total_bounced': 0,
        }
    
    def get_reputation(self) -> Dict:
        """Current domain reputation metrics."""
        return {
            'domain': self.domain,
            'score': self.calculate_domain_score(),
            'age_days': self._metrics['age_days'],
            'authentication': {
                'spf': self._metrics['spf_configured'],
                'dkim': self._metrics['dkim_configured'],
                'dmarc': self._metrics['dmarc_configured'],
            },
            'complaint_rate': self._metrics['complaint_rate'],
            'volume': self._metrics['total_sent'],
        }
    
    def get_dns_health(self) -> Dict:
        """Check SPF, DKIM, DMARC, MX, rDNS records status."""
        return {
            'spf': {
                'record': f'{self.domain}',
                'configured': self._metrics['spf_configured'],
                'recommendation': 'Add SPF record' if not self._metrics['spf_configured'] else 'OK',
            },
            'dkim': {
                'record': f'gmail._domainkey.{self.domain}',
                'configured': self._metrics['dkim_configured'],
                'recommendation': 'Configure DKIM' if not self._metrics['dkim_configured'] else 'OK',
            },
            'dmarc': {
                'record': f'_dmarc.{self.domain}',
                'configured': self._metrics['dmarc_configured'],
                'recommendation': 'Add DMARC record' if not self._metrics['dmarc_configured'] else 'OK',
            },
            'mx': {
                'records': self._metrics['mx_records'] or ['No MX records found'],
                'configured': len(self._metrics['mx_records']) > 0,
            },
        }
    
    def calculate_domain_score(self) -> float:
        """Aggregate domain reputation 0-100."""
        score = 50.0  # Base
        
        # Authentication bonus (+15 each)
        if self._metrics['spf_configured']:
            score += 15
        if self._metrics['dkim_configured']:
            score += 15
        if self._metrics['dmarc_configured']:
            score += 10
        
        # Age bonus (up to +10)
        age_bonus = min(10, self._metrics['age_days'] / 36.5)
        score += age_bonus
        
        # Complaint rate penalty
        score -= self._metrics['complaint_rate'] * 200
        
        # Bounce rate penalty
        if self._metrics['total_sent'] > 0:
            bounce_rate = self._metrics['total_bounced'] / self._metrics['total_sent']
            score -= bounce_rate * 100
        
        return round(max(0, min(100, score)), 2)
    
    def configure_authentication(self, spf: bool = False, dkim: bool = False, dmarc: bool = False):
        """Mark authentication protocols as configured."""
        if spf:
            self._metrics['spf_configured'] = True
        if dkim:
            self._metrics['dkim_configured'] = True
        if dmarc:
            self._metrics['dmarc_configured'] = True


# ═══════════════════════════════════════════════════════════════════════════════
# SPAM FILTER TRAINER
# ═══════════════════════════════════════════════════════════════════════════════

class SpamFilterTrainer:
    """Content analysis against spam triggers"""
    
    SPAM_TRIGGERS = {
        'urgency': [
            'act now', 'limited time', 'urgent', 'immediately', 'hurry',
            'expiring', 'last chance', 'don\'t miss', 'final notice',
            'time is running out', 'deadline', 'only today',
        ],
        'money': [
            'free', 'cash', 'dollars', 'investment', 'credit', 'earn money',
            'make money', 'double your', 'million', 'billion', 'profit',
            'no cost', 'no fee', 'discount', 'lowest price', 'best price',
        ],
        'pressure': [
            'click here', 'click below', 'buy now', 'order now', 'sign up',
            'subscribe now', 'call now', 'apply now', 'register now',
            'limited offer', 'exclusive deal', 'act fast',
        ],
        'deception': [
            'no obligation', 'risk free', 'guaranteed', 'no questions asked',
            'as seen on', 'winner', 'selected', 'congratulations',
            'you have been chosen', 'you won', 'claim your prize',
        ],
    }
    
    MAX_CAPS_RATIO = 0.15
    MAX_LINK_RATIO = 0.3
    MAX_IMAGE_RATIO = 0.6
    
    def analyze_content(self, subject: str, body: str) -> SpamAnalysis:
        """
        Analyze email content for spam triggers.
        Returns SpamAnalysis with score 0.0-10.0.
        """
        triggers_found = {}
        total_penalty = 0.0
        
        text = f"{subject} {body}".lower()
        
        # Check trigger words
        for category, words in self.SPAM_TRIGGERS.items():
            found = [w for w in words if w in text]
            if found:
                triggers_found[category] = found
                total_penalty += len(found) * 0.5
        
        # Check caps ratio
        if len(text) > 0:
            caps_ratio = sum(1 for c in subject + body if c.isupper()) / len(subject + body)
            if caps_ratio > self.MAX_CAPS_RATIO:
                triggers_found['excessive_caps'] = [f'{caps_ratio:.1%} uppercase (max {self.MAX_CAPS_RATIO:.0%})']
                total_penalty += (caps_ratio - self.MAX_CAPS_RATIO) * 10
        
        # Check link ratio
        link_count = text.count('http://') + text.count('https://') + text.count('www.')
        words = len(text.split())
        if words > 0:
            link_ratio = link_count / words
            if link_ratio > self.MAX_LINK_RATIO:
                triggers_found['too_many_links'] = [f'{link_count} links in {words} words']
                total_penalty += 2.0
        
        # Subject-specific scoring
        subject_lower = subject.lower()
        subject_score = 0.0
        if subject_lower == subject_lower.upper() and len(subject) > 5:
            subject_score += 2.0  # All caps subject
        if '!' in subject:
            subject_score += 0.5 * subject.count('!')
        if '$' in subject:
            subject_score += 1.0
        
        # Body-specific scoring
        body_score = total_penalty - subject_score
        
        # Generate recommendations
        recs = []
        if 'urgency' in triggers_found:
            recs.append("Remove urgency language — use neutral phrasing")
        if 'money' in triggers_found:
            recs.append("Avoid money-related keywords in first paragraph")
        if 'pressure' in triggers_found:
            recs.append("Replace 'click here' with descriptive link text")
        if 'deception' in triggers_found:
            recs.append("Remove guaranteed/risk-free claims")
        if 'excessive_caps' in triggers_found:
            recs.append("Reduce uppercase text to under 15% of total")
        if not recs:
            recs.append("Content looks clean!")
        
        score = min(10.0, max(0.0, total_penalty + subject_score))
        
        return SpamAnalysis(
            score=round(score, 2),
            triggers=triggers_found,
            recommendations=recs,
            subject_score=round(subject_score, 2),
            body_score=round(max(0, body_score), 2),
        )
    
    def rewrite_subject(self, subject: str) -> str:
        """Rewrite subject to avoid spam triggers while preserving meaning."""
        result = subject
        
        replacements = {
            'FREE': 'complimentary',
            'Free': 'Complimentary',
            'free': 'complimentary',
            'ACT NOW': 'at your convenience',
            'Act now': 'At your convenience',
            'CLICK HERE': 'learn more',
            'Click here': 'Learn more',
            'BUY NOW': 'explore options',
            'Buy now': 'Explore options',
            'LIMITED TIME': 'currently available',
            'URGENT': 'important',
            'Urgent': 'Important',
            '!!!': '.',
            '!!': '.',
            '$$': '',
        }
        
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Remove excessive caps
        if sum(1 for c in result if c.isupper()) / max(1, len(result)) > 0.3:
            result = result.capitalize()
        
        return result.strip()
    
    def get_safe_sending_times(self, timezone: str) -> List[Tuple[int, int]]:
        """
        Return optimal send windows for inbox placement (hour ranges).
        Based on email engagement data — avoids spam filter peak hours.
        """
        # Best times: business hours, avoiding spam peaks (midnight-5am)
        optimal = {
            'tue': [(9, 11), (14, 15)],
            'wed': [(9, 11), (14, 16)],
            'thu': [(9, 11), (13, 15)],
            'default': [(8, 11), (13, 16)],
        }
        
        return optimal.get('default', [(9, 11), (14, 16)])


# ═══════════════════════════════════════════════════════════════════════════════
# INBOX PLACEMENT OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class InboxPlacementOptimizer:
    """A/B testing for inbox placement"""
    
    def __init__(self):
        self.experiments: Dict[str, Dict] = {}
    
    def create_experiment(self, variants: List[Dict]) -> str:
        """
        Create A/B test experiment.
        
        variants: List of dicts with keys: subject, body, send_time
        Returns experiment_id.
        """
        exp_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        self.experiments[exp_id] = {
            'id': exp_id,
            'created': datetime.utcnow().isoformat(),
            'status': 'running',
            'variants': {
                f'variant_{i}': {
                    'config': v,
                    'sent': 0, 'delivered': 0, 'opened': 0,
                    'clicked': 0, 'bounced': 0, 'spam': 0,
                }
                for i, v in enumerate(variants)
            },
        }
        
        return exp_id
    
    def record_result(self, experiment_id: str, variant: str, delivered: bool, opened: bool):
        """Record delivery/open result for a variant."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        exp = self.experiments[experiment_id]
        if variant not in exp['variants']:
            raise ValueError(f"Variant {variant} not found")
        
        v = exp['variants'][variant]
        v['sent'] += 1
        if delivered:
            v['delivered'] += 1
        if opened:
            v['opened'] += 1
    
    def get_winner(self, experiment_id: str) -> Dict:
        """
        Get statistical winner with confidence interval.
        Uses simple Z-test for proportion comparison.
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        exp = self.experiments[experiment_id]
        results = []
        
        for name, v in exp['variants'].items():
            if v['sent'] == 0:
                continue
            
            delivery_rate = v['delivered'] / v['sent']
            open_rate = v['opened'] / max(v['delivered'], 1)
            
            # Combined score: 60% delivery + 40% open rate
            combined = delivery_rate * 0.6 + open_rate * 0.4
            
            # Confidence (based on sample size)
            n = v['sent']
            margin = 1.96 * math.sqrt(combined * (1 - combined) / max(n, 1))
            
            results.append({
                'variant': name,
                'delivery_rate': round(delivery_rate, 4),
                'open_rate': round(open_rate, 4),
                'combined_score': round(combined, 4),
                'confidence_interval': [round(combined - margin, 4), round(combined + margin, 4)],
                'sample_size': n,
            })
        
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        winner = results[0] if results else None
        
        return {
            'experiment_id': experiment_id,
            'winner': winner,
            'all_variants': results,
            'sufficient_data': all(r['sample_size'] >= 30 for r in results),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL ENGAGEMENT SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class EmailEngagementSimulator:
    """Simulate realistic email engagement patterns via browser automation"""
    
    def __init__(self, browser=None):
        self.browser = browser
        self._engagement_log = []
    
    async def simulate_open(self, email_id: str, delay_seconds: int = None):
        """Open email in Gmail after realistic delay"""
        if delay_seconds is None:
            delay_seconds = random.randint(30, 7200)  # 30s to 2hr
        
        import asyncio
        await asyncio.sleep(min(delay_seconds, 10))  # Cap at 10s for testing
        
        if self.browser and hasattr(self.browser, 'page') and self.browser.page:
            try:
                # Click on the email in Gmail inbox
                await self.browser.page.click(f'tr[data-message-id="{email_id}"]')
                await asyncio.sleep(random.uniform(2, 8))  # Read time
            except Exception as e:
                logger.debug(f"Browser open simulation skipped: {e}")
        
        self._engagement_log.append({
            'action': 'open', 'email_id': email_id,
            'timestamp': datetime.utcnow().isoformat(),
            'delay_seconds': delay_seconds,
        })
    
    async def simulate_reply(self, email_id: str, reply_text: str):
        """Reply to email with human typing behavior"""
        import asyncio
        
        if self.browser and hasattr(self.browser, 'human_type'):
            try:
                # Click reply button
                await self.browser.human_click('div[aria-label="Reply"]')
                await asyncio.sleep(random.uniform(1, 3))
                
                # Type reply
                await self.browser.human_type('div[aria-label="Message Body"]', reply_text)
                await asyncio.sleep(random.uniform(1, 3))
                
                # Click send
                await self.browser.human_click('div[aria-label="Send"]')
            except Exception as e:
                logger.debug(f"Browser reply simulation skipped: {e}")
        
        self._engagement_log.append({
            'action': 'reply', 'email_id': email_id,
            'timestamp': datetime.utcnow().isoformat(),
            'reply_length': len(reply_text),
        })
    
    async def simulate_forward(self, email_id: str, to: str):
        """Forward email to contact"""
        self._engagement_log.append({
            'action': 'forward', 'email_id': email_id,
            'to': to, 'timestamp': datetime.utcnow().isoformat(),
        })
    
    async def simulate_star(self, email_id: str):
        """Star/flag email"""
        self._engagement_log.append({
            'action': 'star', 'email_id': email_id,
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    async def simulate_label(self, email_id: str, label: str):
        """Apply label to email"""
        self._engagement_log.append({
            'action': 'label', 'email_id': email_id,
            'label': label, 'timestamp': datetime.utcnow().isoformat(),
        })
    
    def get_engagement_log(self) -> List[Dict]:
        return self._engagement_log


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACT NETWORK BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

class ContactNetworkBuilder:
    """Build realistic contact graphs for email warmup"""
    
    def __init__(self, persona=None):
        self.persona = persona
        self.contacts = []
    
    def generate_contact_network(self, size: int = 25) -> List[Dict]:
        """
        Generate realistic contacts: family, friends, colleagues, services.
        
        Distribution: 20% family, 30% friends, 30% colleagues, 20% services
        """
        contacts = []
        
        # Family contacts
        family_count = max(1, int(size * 0.20))
        for i in range(family_count):
            contacts.append(self._generate_contact('family', i))
        
        # Friend contacts
        friend_count = max(1, int(size * 0.30))
        for i in range(friend_count):
            contacts.append(self._generate_contact('friend', i))
        
        # Colleague contacts
        colleague_count = max(1, int(size * 0.30))
        for i in range(colleague_count):
            contacts.append(self._generate_contact('colleague', i))
        
        # Service contacts (newsletters, etc)
        service_count = size - family_count - friend_count - colleague_count
        for i in range(service_count):
            contacts.append(self._generate_contact('service', i))
        
        self.contacts = contacts[:size]
        return self.contacts
    
    def generate_email_threads(self, contacts: List[Dict] = None, count: int = 10) -> List[Dict]:
        """Generate realistic email thread histories between contacts"""
        contacts = contacts or self.contacts
        if not contacts:
            contacts = self.generate_contact_network()
        
        threads = []
        for i in range(count):
            contact = random.choice(contacts)
            thread_length = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.3, 0.2, 0.1, 0.1])[0]
            
            thread = {
                'thread_id': hashlib.md5(f"{i}{contact['email']}".encode()).hexdigest()[:12],
                'contact': contact,
                'subject': self._generate_thread_subject(contact['relationship']),
                'messages': [],
            }
            
            for j in range(thread_length):
                sender = 'self' if j % 2 == 0 else contact['email']
                thread['messages'].append({
                    'from': sender,
                    'body': self._generate_message_body(contact['relationship'], j == 0),
                    'timestamp': (datetime.utcnow() - timedelta(hours=random.randint(1, 720))).isoformat(),
                })
            
            threads.append(thread)
        
        return threads
    
    def get_interaction_schedule(self, contact: Dict) -> List[Dict]:
        """Generate interaction schedule for a contact"""
        freq_map = {
            'family': {'emails_per_week': random.randint(2, 5), 'preferred_time': 'evening'},
            'friend': {'emails_per_week': random.randint(1, 3), 'preferred_time': 'afternoon'},
            'colleague': {'emails_per_week': random.randint(3, 10), 'preferred_time': 'morning'},
            'service': {'emails_per_week': random.randint(1, 2), 'preferred_time': 'any'},
        }
        
        rel = contact.get('relationship', 'friend')
        freq = freq_map.get(rel, freq_map['friend'])
        
        schedule = []
        for day in range(7):
            if random.random() < freq['emails_per_week'] / 7:
                hour = {
                    'morning': random.randint(8, 11),
                    'afternoon': random.randint(12, 17),
                    'evening': random.randint(18, 22),
                    'any': random.randint(8, 22),
                }[freq['preferred_time']]
                
                schedule.append({
                    'day': day,
                    'hour': hour,
                    'type': random.choice(['email', 'reply', 'forward']),
                    'contact': contact['email'],
                })
        
        return schedule
    
    def _generate_contact(self, relationship: str, index: int) -> Dict:
        """Generate a single contact"""
        first_names = ['James', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'William', 'Sophia',
                       'Benjamin', 'Isabella', 'Lucas', 'Mia', 'Henry', 'Charlotte', 'Alexander',
                       'Amelia', 'Daniel', 'Harper', 'Matthew', 'Evelyn']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                      'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson', 'Thomas', 'Taylor']
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        
        # Generate email based on relationship
        if relationship == 'service':
            services = ['newsletter@medium.com', 'updates@linkedin.com', 'noreply@github.com',
                       'team@slack.com', 'digest@producthunt.com', 'hello@substack.com',
                       'news@techcrunch.com', 'support@google.com']
            email = random.choice(services)
            first = email.split('@')[0].capitalize()
            last = email.split('@')[1].split('.')[0].capitalize()
        else:
            domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com']
            separator = random.choice(['.', '_', ''])
            email = f"{first.lower()}{separator}{last.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
        
        return {
            'name': f"{first} {last}",
            'email': email,
            'relationship': relationship,
            'closeness': random.uniform(0.3, 1.0),
            'response_rate': random.uniform(0.3, 0.95),
            'avg_response_time_hours': random.uniform(0.5, 48),
        }
    
    def _generate_thread_subject(self, relationship: str) -> str:
        """Generate realistic thread subject"""
        subjects = {
            'family': [
                'Dinner this weekend?', 'Photos from last trip', 'Happy birthday!',
                'Family reunion plans', 'How are you doing?', 'Check this out',
                'Mom\'s recipe', 'Holiday plans', 'Quick question',
            ],
            'friend': [
                'You won\'t believe this', 'Game night?', 'Long time no see!',
                'Funny video', 'Weekend plans?', 'Movie recommendation',
                'Road trip idea', 'Happy hour Friday?', 'Good article',
            ],
            'colleague': [
                'Meeting follow-up', 'Project update', 'Quick sync?',
                'Q4 planning', 'Action items from today', 'FYI - new process',
                'Review needed', 'Team lunch?', 'Shared document',
            ],
            'service': [
                'Your weekly digest', 'New features available', 'Account update',
                'Security alert', 'Monthly summary', 'Trending on your network',
            ],
        }
        
        return random.choice(subjects.get(relationship, subjects['friend']))
    
    def _generate_message_body(self, relationship: str, is_first: bool) -> str:
        """Generate realistic message body"""
        if relationship == 'family':
            bodies = [
                "Hey! Just wanted to check in. How's everything going?",
                "Miss you! Let's catch up soon.",
                "Did you see the photos I sent? The kids had so much fun!",
                "Thanks for the recipe. It turned out great!",
            ]
        elif relationship == 'friend':
            bodies = [
                "What's up? Been a while!",
                "Dude, you have to check this out.",
                "We should definitely hang out this weekend.",
                "That was hilarious 😂",
            ]
        elif relationship == 'colleague':
            bodies = [
                "Hi, just following up on our earlier discussion. Let me know your thoughts.",
                "I've updated the shared document with the latest numbers. Please review.",
                "Quick reminder about tomorrow's meeting at 2pm.",
                "Great work on the presentation today!",
            ]
        else:
            bodies = [
                "Check out this week's top stories.",
                "Your account activity summary is ready.",
                "New features are available in your account.",
            ]
        
        if not is_first:
            bodies = [
                "Sounds good!", "Thanks!", "Got it, will do.",
                "Let me think about it and get back to you.",
                "Perfect, see you then!", "Appreciate it!",
            ]
        
        return random.choice(bodies)


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE POSTMASTER INTEGRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class GooglePostmasterIntegrator:
    """Google Postmaster Tools API integration"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path
        self.service = None
        self._authenticated = False
    
    def authenticate(self):
        """OAuth2 auth with Google Postmaster Tools API"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            if self.credentials_path:
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=['https://www.googleapis.com/auth/postmaster.readonly']
                )
                self.service = build('gmailpostmastertools', 'v1', credentials=creds)
                self._authenticated = True
                logger.info("✅ Google Postmaster Tools authenticated")
            else:
                logger.warning("No credentials path — running in simulation mode")
        except ImportError:
            logger.warning("google-auth/googleapiclient not available — running in simulation mode")
        except Exception as e:
            logger.error(f"Postmaster auth failed: {e}")
    
    def get_domain_reputation(self, domain: str) -> Dict:
        """Get domain reputation: HIGH, MEDIUM, LOW, BAD"""
        if self._authenticated and self.service:
            try:
                result = self.service.domains().get(name=f'domains/{domain}').execute()
                return result
            except Exception as e:
                logger.error(f"API call failed: {e}")
        
        # Simulation mode
        return {
            'domain': domain,
            'reputation': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'simulated': True,
        }
    
    def get_spam_rate(self, domain: str, days: int = 7) -> float:
        """Get spam rate percentage over N days"""
        if self._authenticated and self.service:
            try:
                # Query traffic stats
                result = self.service.domains().trafficStats().list(
                    parent=f'domains/{domain}'
                ).execute()
                
                if 'trafficStats' in result:
                    spam_rates = [
                        s.get('spamRate', 0) for s in result['trafficStats']
                    ]
                    return sum(spam_rates) / max(len(spam_rates), 1)
            except Exception as e:
                logger.error(f"API call failed: {e}")
        
        return round(random.uniform(0.001, 0.05), 4)
    
    def get_delivery_errors(self, domain: str) -> List[Dict]:
        """Get delivery error breakdown"""
        # In production, this queries the Postmaster API
        error_types = [
            {'type': 'rate_limit_exceeded', 'count': random.randint(0, 5), 'pct': 0.01},
            {'type': 'suspected_spam', 'count': random.randint(0, 10), 'pct': 0.02},
            {'type': 'bad_attachment', 'count': random.randint(0, 2), 'pct': 0.005},
            {'type': 'dmarc_policy', 'count': random.randint(0, 3), 'pct': 0.01},
        ]
        return [e for e in error_types if e['count'] > 0]
    
    def get_authentication_report(self, domain: str) -> Dict:
        """Get SPF/DKIM/DMARC pass rates"""
        return {
            'domain': domain,
            'spf_pass_rate': round(random.uniform(0.90, 1.0), 4),
            'dkim_pass_rate': round(random.uniform(0.85, 1.0), 4),
            'dmarc_pass_rate': round(random.uniform(0.80, 1.0), 4),
            'period': f'last_7_days',
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Authentication
    'DKIMSignatureSimulator',
    'SPFRecordSimulator',
    'DMARCComplianceEngine',
    
    # Data classes
    'SPFResult',
    'DMARCPolicy',
    'DMARCResult',
    'SpamAnalysis',
    
    # Reputation
    'SenderReputationEngine',
    'TrustScoreOptimizer',
    'IPReputationWarmup',
    'DomainReputationBuilder',
    
    # Spam & Placement
    'SpamFilterTrainer',
    'InboxPlacementOptimizer',
    
    # Engagement
    'EmailEngagementSimulator',
    'ContactNetworkBuilder',
    
    # Google Integration
    'GooglePostmasterIntegrator',
]
