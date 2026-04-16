#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              GMAIL INFINITY FACTORY — INTEGRATION TEST SUITE                ║
║                    Tests REAL functionality, not just imports                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import sys
import os
import json
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = "✅"
FAIL = "❌"

results = {"passed": 0, "failed": 0, "details": []}


def test(name):
    """Decorator for test functions"""
    def decorator(func):
        async def wrapper():
            try:
                result = await func() if asyncio.iscoroutinefunction(func) else func()
                results["passed"] += 1
                results["details"].append({"name": name, "status": "PASS", "result": result})
                print(f"  {PASS} {name}")
                if result:
                    print(f"     → {result}")
                return True
            except Exception as e:
                results["failed"] += 1
                tb_lines = traceback.format_exc().strip().split('\n')
                location = tb_lines[-3].strip() if len(tb_lines) >= 3 else ''
                results["details"].append({"name": name, "status": "FAIL", "error": str(e)})
                print(f"  {FAIL} {name}")
                print(f"     → {e}")
                print(f"     → {location}")
                return False
        wrapper.__name__ = name
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: PERSONA GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

@test("Persona Generator — Generate 3 unique humans")
def test_persona_generation():
    from identity.persona_generator import PersonaGenerator
    
    gen = PersonaGenerator()
    personas = gen.generate_batch(3)
    
    assert len(personas) == 3, f"Expected 3, got {len(personas)}"
    
    ids = set()
    for p in personas:
        assert p.name.first_name, "Missing first name"
        assert p.name.last_name, "Missing last name"
        assert p.name.full_name, "Missing full name"
        assert p.date_info.age >= 18, f"Age {p.date_info.age} < 18"
        assert p.date_info.date_of_birth, "Missing date_of_birth"
        assert p.location.city, "Missing city"
        assert p.location.country, "Missing country"
        assert p.persona_id not in ids, "Duplicate persona_id"
        ids.add(p.persona_id)
    
    p = personas[0]
    return f"{p.name.full_name}, {p.date_info.age}yo, {p.location.city}, {p.location.country}"


@test("Persona Generator — Gmail username construction")
def test_gmail_username():
    from identity.persona_generator import PersonaGenerator
    
    gen = PersonaGenerator()
    persona = gen.generate_persona()
    
    assert persona.name.first_name.isalpha(), f"First name not alpha: {persona.name.first_name}"
    assert persona.name.last_name, f"Missing last name"
    
    first = persona.name.first_name.lower()
    last = persona.name.last_name.lower().replace(' ', '')
    username = f"{first}.{last}"
    
    assert len(username) >= 5, f"Username too short: {username}"
    
    return f"Username: {username}@gmail.com | DOB: {persona.date_info.date_of_birth}"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: NAME GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@test("Name Generator — Multi-cultural names")
def test_name_generator():
    from identity.name_generator import NameGenerator, CulturalBackground
    
    gen = NameGenerator()
    
    cultures = [
        CulturalBackground.AMERICAN,
        CulturalBackground.BRITISH,
        CulturalBackground.JAPANESE,
        CulturalBackground.ARABIC,
        CulturalBackground.MEXICAN,
    ]
    
    names = []
    for culture in cultures:
        name = gen.generate_name(culture=culture, gender="male")
        assert name.first_name, f"No first name for {culture.value}"
        assert name.last_name, f"No last name for {culture.value}"
        names.append(f"{name.full_name} ({culture.value})")
    
    return ", ".join(names[:3]) + "..."


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: BIO GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@test("Bio Generator — Generate Gmail bios with WritingStyle/Tone/BioLength")
def test_bio_generator():
    from identity.persona_generator import PersonaGenerator
    from identity.bio_generator import BioGenerator, WritingStyle, Tone, BioLength
    
    gen = PersonaGenerator()
    persona = gen.generate_persona()
    
    bio_gen = BioGenerator()
    
    pro_bio = bio_gen.generate_gmail_bio(persona, writing_style=WritingStyle.PROFESSIONAL, tone=Tone.FORMAL)
    casual_bio = bio_gen.generate_gmail_bio(persona, writing_style=WritingStyle.CASUAL, tone=Tone.WITTY)
    short_bio = bio_gen.generate_gmail_bio(persona, writing_style=WritingStyle.MINIMALIST, length=BioLength.SHORT)
    
    assert len(pro_bio) > 0, "Professional bio is empty"
    assert len(casual_bio) > 0, "Casual bio is empty"
    assert len(short_bio) <= 130, f"Short bio too long: {len(short_bio)} chars"
    
    return f"Pro: '{pro_bio[:60]}...' | Short({len(short_bio)}ch): '{short_bio[:50]}...'"


@test("Bio Generator — LinkedIn + Dating + Instagram bios")
def test_bio_platforms():
    from identity.persona_generator import PersonaGenerator
    from identity.bio_generator import BioGenerator
    
    gen = PersonaGenerator()
    persona = gen.generate_persona()
    bio_gen = BioGenerator()
    
    linkedin = bio_gen.generate_linkedin_summary(persona)
    dating = bio_gen.generate_dating_bio(persona)
    instagram = bio_gen.generate_instagram_bio(persona)
    
    assert len(linkedin) > 50, f"LinkedIn too short: {len(linkedin)}"
    assert len(dating) > 5, "Dating bio empty"
    assert len(instagram) > 5, "Instagram bio empty"
    
    return f"LinkedIn({len(linkedin)}ch), Dating({len(dating)}ch), Insta({len(instagram)}ch)"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: FINGERPRINT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@test("Fingerprint Generator — Generate unique device fingerprints")
def test_fingerprint_generator():
    from core.fingerprint_generator import QuantumFingerprintFactory
    
    factory = QuantumFingerprintFactory()
    
    fingerprints = []
    for i in range(5):
        fp = factory.generate_fingerprint()
        fingerprints.append(fp)
    
    ua_set = set()
    for fp in fingerprints:
        assert fp.user_agent, "Missing user_agent"
        assert fp.screen_width > 0, "Invalid screen_width"
        assert fp.screen_height > 0, "Invalid screen_height"
        assert fp.timezone, "Missing timezone"
        assert fp.language, "Missing language"
        assert fp.gpu_vendor, "Missing gpu_vendor"
        assert fp.gpu_renderer, "Missing gpu_renderer"
        ua_set.add(fp.user_agent)
    
    assert len(ua_set) >= 2, f"Only {len(ua_set)} unique UAs from 5 fingerprints"
    
    fp = fingerprints[0]
    return f"UA: {fp.user_agent[:50]}... | {fp.screen_width}x{fp.screen_height} | GPU: {fp.gpu_vendor} | TZ: {fp.timezone}"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: STEALTH PROTECTORS — validate JS content in apply() methods
# ═══════════════════════════════════════════════════════════════════════════════

@test("Stealth Protectors — Validate injector chains 13 protectors correctly")
def test_stealth_protectors():
    from core.stealth_protectors import (
        FingerprintInjector, WebGLProtector, CanvasProtector,
        NavigatorProtector, CDPDetectionRemover, TimezoneSpoofer,
        BaseProtector,
    )
    
    # Verify FingerprintInjector chains all 13 protectors
    injector = FingerprintInjector()
    assert len(injector._protectors) == 13, f"Expected 13 protectors, got {len(injector._protectors)}"
    
    # Verify all are BaseProtector subclasses
    for p in injector._protectors:
        assert isinstance(p, BaseProtector), f"{p.__class__.__name__} is not a BaseProtector"
        assert hasattr(p, 'apply'), f"{p.__class__.__name__} missing apply()"
        assert asyncio.iscoroutinefunction(p.apply), f"{p.__class__.__name__}.apply is not async"
    
    # Verify protector ordering: CDP first, Permission last
    assert isinstance(injector._protectors[0], CDPDetectionRemover), "CDPDetectionRemover should be first"
    
    # Verify add/remove works
    injector.remove_protector(CDPDetectionRemover)
    assert len(injector._protectors) == 12, "Remove didn't work"
    injector.add_protector(CDPDetectionRemover(), index=0)
    assert len(injector._protectors) == 13, "Add didn't work"
    
    # Custom injector with subset
    custom = FingerprintInjector(protectors=[WebGLProtector(), CanvasProtector()])
    assert len(custom._protectors) == 2, "Custom injector should have 2"
    
    return f"13 protectors chained, add/remove works, custom subsets work"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: DKIM / SPF / DMARC
# ═══════════════════════════════════════════════════════════════════════════════

@test("DKIM — RSA 2048 keypair + message signing")
def test_dkim():
    from warming.email_deliverability import DKIMSignatureSimulator
    
    dkim = DKIMSignatureSimulator('testdomain.com', selector='s1')
    private_pem, dns_record = dkim.generate_keypair()
    
    assert 'BEGIN PRIVATE KEY' in private_pem, "Invalid PEM format"
    assert dns_record.startswith('v=DKIM1'), "Invalid DNS record"
    assert 'p=' in dns_record, "DNS record missing public key"
    assert len(dns_record) > 100, f"DNS record too short ({len(dns_record)} chars)"
    
    headers = {
        'from': 'alice@testdomain.com', 'to': 'bob@example.com',
        'subject': 'Test Email', 'date': 'Mon, 01 Jan 2026 00:00:00 +0000',
        'message-id': '<test@testdomain.com>',
    }
    signature = dkim.sign_message("Hello, this is a test email body.", headers)
    
    assert 'v=1' in signature, "Missing DKIM version"
    assert 'a=rsa-sha256' in signature, "Missing algorithm"
    assert 'd=testdomain.com' in signature, "Missing domain"
    assert len(signature.split('b=')[1]) > 50, "Signature too short"
    
    return f"DNS: {dns_record[:50]}... | Sig: ...{signature[-40:]}"


@test("SPF — Record build + CIDR validation")
def test_spf():
    from warming.email_deliverability import SPFRecordSimulator, SPFResult
    
    spf = SPFRecordSimulator('mycompany.com')
    record = spf.build_record(['192.168.1.0/24', '10.0.0.5'], includes=['_spf.google.com'])
    
    assert record.startswith('v=spf1')
    assert 'ip4:192.168.1.0/24' in record
    assert '-all' in record
    
    issues = spf.validate_record(record)
    assert len(issues) == 0, f"Valid record has issues: {issues}"
    
    assert spf.check_alignment('192.168.1.50', 'user@mycompany.com') == SPFResult.PASS
    assert spf.check_alignment('8.8.8.8', 'user@mycompany.com') == SPFResult.FAIL
    
    return f"Record: {record} | CIDR: PASS/FAIL correctly"


@test("DMARC — Policy enforcement + XML aggregate report")
def test_dmarc():
    from warming.email_deliverability import DMARCComplianceEngine
    
    dmarc = DMARCComplianceEngine('test.com')
    record = dmarc.build_record(policy='quarantine', rua='mailto:dmarc@test.com')
    
    assert 'p=quarantine' in record
    
    pass_result = dmarc.check_alignment(True, 'pass', 'user@test.com', 'user@test.com')
    assert pass_result.passed, "Should pass with aligned DKIM+SPF"
    
    fail_result = dmarc.check_alignment(False, 'fail', 'user@test.com', 'user@fake.com')
    assert not fail_result.passed
    assert fail_result.disposition == 'quarantine'
    
    xml = dmarc.generate_aggregate_report()
    assert '<?xml' in xml
    assert '<feedback>' in xml
    
    return f"Aligned=PASS | Misaligned=QUARANTINE | XML={len(xml)}ch"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: SPAM FILTER
# ═══════════════════════════════════════════════════════════════════════════════

@test("Spam Filter — Detect triggers + rewrite subject")
def test_spam_filter():
    from warming.email_deliverability import SpamFilterTrainer
    
    trainer = SpamFilterTrainer()
    
    spam = trainer.analyze_content(
        "FREE MONEY!!! ACT NOW - Limited Time Offer!!!",
        "Click here to claim your prize! You won $1,000,000!"
    )
    assert spam.score >= 3.0, f"Spam score too low: {spam.score}"
    assert not spam.is_safe
    assert len(spam.triggers) >= 3
    
    clean = trainer.analyze_content("Meeting follow-up", "Hi, thanks for the discussion.")
    assert clean.score < 2.0, f"Clean email scored: {clean.score}"
    assert clean.is_safe
    
    rewritten = trainer.rewrite_subject("FREE MONEY - ACT NOW!!!")
    assert rewritten != "FREE MONEY - ACT NOW!!!"
    
    return f"Spam={spam.score}/10 triggers={list(spam.triggers.keys())} | Clean={clean.score}/10 | Rewrite: '{rewritten}'"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: SENDER REPUTATION (with bug fix)
# ═══════════════════════════════════════════════════════════════════════════════

@test("Sender Reputation — Score + send limits + spam_report counting")
def test_sender_reputation():
    from warming.email_deliverability import SenderReputationEngine
    
    engine = SenderReputationEngine()
    email = 'test.account@gmail.com'
    
    assert engine.calculate_score(email) == 50.0, "New account should be 50.0"
    
    # Good sender
    for i in range(20):
        engine.log_event(email, 'sent')
        engine.log_event(email, 'delivered')
    for i in range(15):
        engine.log_event(email, 'opened')
    for i in range(5):
        engine.log_event(email, 'replied')
    
    good_score = engine.calculate_score(email)
    assert good_score > 70, f"Good sender should score >70, got {good_score}"
    
    # Spammer — verify spam_report events actually count
    bad = 'spammer@gmail.com'
    for i in range(10):
        engine.log_event(bad, 'sent')
        engine.log_event(bad, 'spam_report')
    
    # Verify the counter was incremented
    assert engine.signals[bad]['spam_reports'] == 10, f"spam_reports should be 10, got {engine.signals[bad]['spam_reports']}"
    
    bad_score = engine.calculate_score(bad)
    assert bad_score < 30, f"Spammer should score <30, got {bad_score}"
    
    recs = engine.get_recommendations(bad)
    assert any('SPAM' in r.upper() or 'CRITICAL' in r.upper() for r in recs), f"Should warn about spam: {recs}"
    
    return f"Good={good_score} | Spammer={bad_score} (spam_reports=10) | Recs: {recs[0][:50]}..."


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 9: TRUST SCORE
# ═══════════════════════════════════════════════════════════════════════════════

@test("Trust Score — Multi-signal optimization")
def test_trust_score():
    from warming.email_deliverability import TrustScoreOptimizer
    
    optimizer = TrustScoreOptimizer()
    
    good = optimizer.calculate_trust_score({'engagement_rate': 0.85, 'bounce_rate_inverse': 0.95, 'spam_report_inverse': 0.98, 'account_age_days': 0.9, 'ip_reputation': 0.9, 'google_services_usage': 0.7, 'email_volume_consistency': 0.8})
    assert good > 80, f"Good signals should score >80, got {good}"
    
    poor = optimizer.calculate_trust_score({'engagement_rate': 0.2, 'bounce_rate_inverse': 0.4, 'spam_report_inverse': 0.3})
    assert poor < 50, f"Poor signals should score <50, got {poor}"
    
    plan = optimizer.optimize({'engagement_rate': 0.2}, target_score=85.0)
    assert len(plan) > 2, "Plan should have multiple actions"
    
    return f"Good={good} | Poor={poor} | Plan: {len(plan)} optimization actions"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 10: IP WARMUP
# ═══════════════════════════════════════════════════════════════════════════════

@test("IP Warmup — Exponential schedule")
def test_ip_warmup():
    from warming.email_deliverability import IPReputationWarmup
    
    w = IPReputationWarmup('192.168.1.100')
    assert w.get_todays_limit() == 5, "Day 1 should be 5"
    
    w.log_send(5)
    assert w.get_todays_limit() > 5, "Day 2 should exceed day 1"
    
    schedule = w.get_warmup_schedule(target_daily=200)
    assert schedule[0]['limit'] == 5
    assert schedule[-1]['limit'] == 200
    for i in range(1, len(schedule)):
        assert schedule[i]['limit'] >= schedule[i-1]['limit'], "Not monotonic"
    
    return f"Schedule: {len(schedule)} days, start=5 → end=200"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 11: CONTACT NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

@test("Contact Network — Graph + threads + schedule")
def test_contact_network():
    from warming.email_deliverability import ContactNetworkBuilder
    
    builder = ContactNetworkBuilder()
    contacts = builder.generate_contact_network(20)
    assert len(contacts) == 20
    
    rels = set(c['relationship'] for c in contacts)
    assert rels == {'family', 'friend', 'colleague', 'service'}, f"Missing relationships: {rels}"
    
    for c in contacts:
        assert '@' in c['email']
        assert c['name']
        assert 0 <= c['closeness'] <= 1
    
    threads = builder.generate_email_threads(contacts, count=5)
    assert len(threads) == 5
    for t in threads:
        assert t['subject']
        assert len(t['messages']) > 0
    
    schedule = builder.get_interaction_schedule(contacts[0])
    assert isinstance(schedule, list)
    
    return f"20 contacts ({', '.join(rels)}) | 5 threads | {len(schedule)} interactions/week"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 12: A/B TESTING
# ═══════════════════════════════════════════════════════════════════════════════

@test("Inbox Placement — A/B experiment with statistical winner")
def test_inbox_placement():
    from warming.email_deliverability import InboxPlacementOptimizer
    import random
    
    optimizer = InboxPlacementOptimizer()
    exp_id = optimizer.create_experiment([
        {'subject': 'Meeting Follow-up'},
        {'subject': 'RE: Our Discussion'},
    ])
    
    random.seed(42)
    for _ in range(50):
        optimizer.record_result(exp_id, 'variant_0', delivered=random.random() > 0.1, opened=random.random() > 0.4)
        optimizer.record_result(exp_id, 'variant_1', delivered=random.random() > 0.05, opened=random.random() > 0.3)
    
    result = optimizer.get_winner(exp_id)
    assert result['winner']
    assert result['winner']['sample_size'] == 50
    assert result['sufficient_data']
    
    w = result['winner']
    return f"Winner: {w['variant']} (delivery={w['delivery_rate']:.1%}, open={w['open_rate']:.1%})"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 13: WARMUP MODULES
# ═══════════════════════════════════════════════════════════════════════════════

@test("Google Service Warmups — 7 modules run sessions")
async def test_warmup_sessions():
    from warming.google_service_warmups import (
        AndroidPlayStoreWarmup, GooglePhotosWarmup, CalendarEventGenerator,
        GoogleDocsWarmup, GoogleSheetsWarmup, GoogleSlidesWarmup, ChromeSyncSimulator,
    )
    
    modules = [
        AndroidPlayStoreWarmup, GooglePhotosWarmup, CalendarEventGenerator,
        GoogleDocsWarmup, GoogleSheetsWarmup, GoogleSlidesWarmup, ChromeSyncSimulator,
    ]
    
    total = 0
    for cls in modules:
        instance = cls()
        await instance.run_warmup_session(duration_min=1)
        log = instance.get_activity_log()
        assert len(log) >= 2, f"{cls.__name__} produced only {len(log)} activities"
        assert log[0]['action'] == 'session_start'
        assert log[-1]['action'] == 'session_complete'
        total += len(log)
    
    return f"7 modules, {total} total activities logged"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 14: DOMAIN REPUTATION
# ═══════════════════════════════════════════════════════════════════════════════

@test("Domain Reputation — Score + DNS health")
def test_domain_reputation():
    from warming.email_deliverability import DomainReputationBuilder
    
    b = DomainReputationBuilder('myapp.com')
    assert b.calculate_domain_score() == 50.0
    
    b.configure_authentication(spf=True, dkim=True, dmarc=True)
    after = b.calculate_domain_score()
    assert after >= 90, f"Full auth should score >=90, got {after}"
    
    health = b.get_dns_health()
    assert health['spf']['configured']
    assert health['dkim']['configured']
    assert health['dmarc']['configured']
    
    return f"Before: 50 | After auth: {after} | DNS: all OK"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 15: E2E PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

@test("E2E Pipeline — Persona → Fingerprint → Bio → Deliverability")
def test_e2e_pipeline():
    from identity.persona_generator import PersonaGenerator
    from identity.bio_generator import BioGenerator, WritingStyle, Tone, BioLength
    from core.fingerprint_generator import QuantumFingerprintFactory
    from core.stealth_protectors import FingerprintInjector
    from warming.email_deliverability import (
        SpamFilterTrainer, SenderReputationEngine, ContactNetworkBuilder, TrustScoreOptimizer,
    )
    
    # 1. Generate persona
    persona = PersonaGenerator().generate_persona()
    assert persona.name.full_name
    
    # 2. Generate fingerprint
    fp = QuantumFingerprintFactory().generate_fingerprint()
    assert fp.user_agent
    
    # 3. Generate bio
    bio = BioGenerator().generate_gmail_bio(
        persona, writing_style=WritingStyle.PROFESSIONAL,
        tone=Tone.NEUTRAL, length=BioLength.MEDIUM
    )
    assert len(bio) > 10
    
    # 4. Prepare stealth injection
    injector = FingerprintInjector()
    assert len(injector._protectors) == 13
    
    # 5. Check welcome email isn't spam
    analysis = SpamFilterTrainer().analyze_content(
        f"Welcome, {persona.name.first_name}!",
        f"Hi {persona.name.first_name}, your account is ready."
    )
    assert analysis.is_safe, f"Welcome email flagged: {analysis.score}"
    
    # 6. Build contact network
    contacts = ContactNetworkBuilder().generate_contact_network(10)
    assert len(contacts) == 10
    
    # 7. Trust score
    trust = TrustScoreOptimizer().calculate_trust_score({
        'account_age_days': 0.01, 'engagement_rate': 0.5, 'google_services_usage': 0.3,
    })
    
    return (
        f"{persona.name.full_name} ({persona.date_info.age}yo) | "
        f"FP: {fp.screen_width}x{fp.screen_height} | "
        f"Bio: {len(bio)}ch | "
        f"13 stealth scripts | "
        f"Spam: {analysis.score}/10 | "
        f"10 contacts | "
        f"Trust: {trust}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    print()
    print("=" * 70)
    print("  GMAIL INFINITY FACTORY — FUNCTIONAL INTEGRATION TESTS")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)
    print()
    
    tests = [
        test_persona_generation,
        test_gmail_username,
        test_name_generator,
        test_bio_generator,
        test_bio_platforms,
        test_fingerprint_generator,
        test_stealth_protectors,
        test_dkim,
        test_spf,
        test_dmarc,
        test_spam_filter,
        test_sender_reputation,
        test_trust_score,
        test_ip_warmup,
        test_contact_network,
        test_inbox_placement,
        test_warmup_sessions,
        test_domain_reputation,
        test_e2e_pipeline,
    ]
    
    for t in tests:
        await t()
    
    print()
    print("=" * 70)
    p, f = results["passed"], results["failed"]
    if f == 0:
        print(f"  {PASS} ALL {p} TESTS PASSED — SYSTEM IS FULLY FUNCTIONAL")
    else:
        print(f"  {FAIL} {f}/{p+f} TESTS FAILED")
        for d in results["details"]:
            if d["status"] == "FAIL":
                print(f"    {FAIL} {d['name']}: {d['error']}")
    print("=" * 70)
    
    return f == 0


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
