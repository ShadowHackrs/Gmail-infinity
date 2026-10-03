"""
SMS Manager - Unified async SMS service handler
Provides a single interface for all SMS services:
  - 5sim.net (with cancel/finish/balance)
  - SMS-Activate
  - OnlineSIM
  - GetSMS
"""
import asyncio
import re
import logging
import aiohttp
from config.settings import Config

logger = logging.getLogger('gmail_creator_sms')

MAX_POLL_SECONDS = 180
POLL_INTERVAL = 5


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API (async)
# ══════════════════════════════════════════════════════════════════════════════

async def get_phone_from_any_service():
    """
    Try to get a phone number from any configured SMS service.
    Returns: {'phone': str, 'id': str, 'service': str} or None
    """
    services = [
        ("5sim",         Config.FIVESIM_API_KEY,       _get_5sim_phone),
        ("sms_activate", Config.SMS_ACTIVATE_API_KEY,   _get_sms_activate_phone),
        ("onlinesim",    Config.ONLINESIM_API_KEY,      _get_onlinesim_phone),
        ("getsms",       Config.GETSMS_API_KEY,         _get_getsms_phone),
        ("herosms",      Config.HEROSMS_API_KEY,        _get_herosms_phone),
    ]

    for name, api_key, get_fn in services:
        if not api_key:
            continue
        try:
            logger.info(f"Trying SMS service: {name}")
            result = await get_fn()
            if result:
                result['service'] = name
                logger.info(f"Got phone from {name}: {result['phone']}")
                return result
        except Exception as e:
            logger.warning(f"{name} failed: {e}")

    logger.error("No SMS service available or all failed.")
    return None


async def get_code_from_service(service_name: str, order_id: str, wait_time: int = MAX_POLL_SECONDS):
    """
    Wait for and retrieve the SMS verification code.
    Returns: str (code) or None
    """
    poll_fn = {
        '5sim':         _poll_5sim_code,
        'sms_activate': _poll_sms_activate_code,
        'onlinesim':    _poll_onlinesim_code,
        'getsms':       _poll_getsms_code,
        'herosms':      _poll_herosms_code,
    }.get(service_name)

    if not poll_fn:
        logger.error(f"Unknown SMS service: {service_name}")
        return None

    return await poll_fn(order_id, wait_time)


async def cancel_order(service_name: str, order_id: str):
    """Cancel an SMS order (saves money when verification fails)."""
    try:
        cancel_fn = {
            '5sim':         _cancel_5sim_order,
            'sms_activate': _cancel_sms_activate_order,
            'onlinesim':    _cancel_onlinesim_order,
            'getsms':       _cancel_getsms_order,
            'herosms':      _cancel_herosms_order,
        }.get(service_name)

        if cancel_fn:
            await cancel_fn(order_id)
            logger.info(f"Order {order_id} cancelled on {service_name}")
    except Exception as e:
        logger.warning(f"Failed to cancel order {order_id} on {service_name}: {e}")


async def finish_order(service_name: str, order_id: str):
    """Mark an SMS order as completed (after successful verification)."""
    try:
        finish_fn = {
            '5sim':         _finish_5sim_order,
            'sms_activate': _finish_sms_activate_order,
            'onlinesim':    None,
            'getsms':       _finish_getsms_order,
            'herosms':      _finish_herosms_order,
        }.get(service_name)

        if finish_fn:
            await finish_fn(order_id)
            logger.info(f"Order {order_id} finished on {service_name}")
    except Exception as e:
        logger.warning(f"Failed to finish order {order_id} on {service_name}: {e}")


async def check_balance(service_name: str = None):
    """Check balance for a specific service or all configured services."""
    results = {}
    services = {
        '5sim': (Config.FIVESIM_API_KEY, _get_5sim_balance),
        'sms_activate': (Config.SMS_ACTIVATE_API_KEY, _get_sms_activate_balance),
        'herosms': (Config.HEROSMS_API_KEY, _get_herosms_balance),
    }

    if service_name:
        key, fn = services.get(service_name, (None, None))
        if key and fn:
            results[service_name] = await fn()
    else:
        for name, (key, fn) in services.items():
            if key:
                try:
                    results[name] = await fn()
                except Exception:
                    results[name] = None

    return results


def format_phone_for_google(phone: str) -> str:
    """
    Format phone number for Google's input field.
    Google expects the number WITH country code but sometimes without '+'.
    """
    phone = phone.strip()
    if phone.startswith('+'):
        return phone
    if len(phone) > 10 and not phone.startswith('+'):
        return '+' + phone
    return phone


# ══════════════════════════════════════════════════════════════════════════════
# 5sim implementation
# ══════════════════════════════════════════════════════════════════════════════

def _5sim_headers():
    return {"Authorization": f"Bearer {Config.FIVESIM_API_KEY}", "Accept": "application/json"}


async def _get_5sim_balance():
    url = "https://5sim.net/v1/user/profile"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_5sim_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                balance = data.get("balance", 0)
                logger.info(f"5sim balance: {balance}")
                return balance
    return None


async def _get_5sim_phone():
    balance = await _get_5sim_balance()
    if balance is not None and balance < 1:
        logger.error(f"5sim balance too low: {balance}")
        return None

    country = getattr(Config, 'FIVESIM_COUNTRY', 'usa')
    operator = getattr(Config, 'FIVESIM_OPERATOR', 'any')
    url = f"https://5sim.net/v1/user/buy/activation/{country}/{operator}/google"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_5sim_headers(), timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"5sim buy failed ({resp.status}): {text}")
                return None
            data = await resp.json()

    phone = data.get("phone", "")
    order_id = str(data.get("id", ""))
    if phone and order_id:
        return {"phone": phone, "id": order_id}
    return None


async def _poll_5sim_code(order_id: str, wait_time: int):
    url = f"https://5sim.net/v1/user/check/{order_id}"
    deadline = asyncio.get_running_loop().time() + wait_time

    async with aiohttp.ClientSession() as session:
        while asyncio.get_running_loop().time() < deadline:
            try:
                async with session.get(url, headers=_5sim_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get("status", "")
                        if status == "CANCELED":
                            logger.warning("5sim: order was cancelled")
                            return None
                        sms_list = data.get("sms", [])
                        if sms_list:
                            code = sms_list[0].get("code")
                            if code:
                                logger.info(f"5sim code received: {code}")
                                return code
            except Exception as e:
                logger.warning(f"5sim poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    logger.warning("5sim: timed out waiting for code")
    return None


async def _cancel_5sim_order(order_id: str):
    url = f"https://5sim.net/v1/user/cancel/{order_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_5sim_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                logger.info(f"5sim order {order_id} cancelled")
            else:
                text = await resp.text()
                logger.warning(f"5sim cancel failed ({resp.status}): {text}")


async def _finish_5sim_order(order_id: str):
    url = f"https://5sim.net/v1/user/finish/{order_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_5sim_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                logger.info(f"5sim order {order_id} finished")


# ══════════════════════════════════════════════════════════════════════════════
# SMS-Activate implementation
# ══════════════════════════════════════════════════════════════════════════════

async def _get_sms_activate_balance():
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {"api_key": Config.SMS_ACTIVATE_API_KEY, "action": "getBalance"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            if text.startswith("ACCESS_BALANCE:"):
                balance = float(text.split(":")[1])
                logger.info(f"SMS-Activate balance: {balance}")
                return balance
    return None


async def _get_sms_activate_phone():
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {
        "api_key": Config.SMS_ACTIVATE_API_KEY,
        "action": "getNumber",
        "service": "go",
        "country": Config.SMS_ACTIVATE_COUNTRY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = (await resp.text()).strip()

    if text.startswith("ACCESS_NUMBER"):
        parts = text.split(":")
        if len(parts) >= 3:
            return {"phone": parts[2], "id": parts[1]}
    elif "NO_NUMBERS" in text:
        logger.warning("SMS-Activate: no numbers available")
    elif "NO_BALANCE" in text:
        logger.error("SMS-Activate: insufficient balance")
    else:
        logger.warning(f"SMS-Activate response: {text}")
    return None


async def _poll_sms_activate_code(order_id: str, wait_time: int):
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {
        "api_key": Config.SMS_ACTIVATE_API_KEY,
        "action": "getStatus",
        "id": order_id,
    }
    deadline = asyncio.get_running_loop().time() + wait_time

    async with aiohttp.ClientSession() as session:
        while asyncio.get_running_loop().time() < deadline:
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = (await resp.text()).strip()
                    if text.startswith("STATUS_OK"):
                        code = text.split(":")[1]
                        logger.info(f"SMS-Activate code received: {code}")
                        return code
                    elif text == "STATUS_CANCEL":
                        logger.warning("SMS-Activate: order cancelled")
                        return None
            except Exception as e:
                logger.warning(f"SMS-Activate poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    logger.warning("SMS-Activate: timed out waiting for code")
    return None


async def _cancel_sms_activate_order(order_id: str):
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {"api_key": Config.SMS_ACTIVATE_API_KEY, "action": "setStatus", "id": order_id, "status": 8}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            logger.info(f"SMS-Activate cancel response: {text}")


async def _finish_sms_activate_order(order_id: str):
    url = "https://api.sms-activate.org/stubs/handler_api.php"
    params = {"api_key": Config.SMS_ACTIVATE_API_KEY, "action": "setStatus", "id": order_id, "status": 6}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            logger.info(f"SMS-Activate finish response: {text}")


# ══════════════════════════════════════════════════════════════════════════════
# OnlineSIM implementation
# ══════════════════════════════════════════════════════════════════════════════

async def _get_onlinesim_phone():
    url = "https://onlinesim.io/api/getNum.php"
    params = {
        "apikey": Config.ONLINESIM_API_KEY,
        "service": "Google",
        "country": Config.ONLINESIM_COUNTRY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            data = await resp.json()

        if data.get("response") == 1:
            tzid = str(data.get("tzid", ""))
            if tzid:
                state_url = "https://onlinesim.io/api/getState.php"
                state_params = {"apikey": Config.ONLINESIM_API_KEY, "tzid": tzid}
                for _ in range(10):
                    try:
                        async with session.get(state_url, params=state_params, timeout=aiohttp.ClientTimeout(total=10)) as sr:
                            state_data = await sr.json()
                            if isinstance(state_data, list) and len(state_data) > 0:
                                item = state_data[0]
                                if item.get("number"):
                                    return {"phone": item["number"], "id": tzid}
                    except Exception:
                        pass
                    await asyncio.sleep(3)
        else:
            logger.warning(f"OnlineSIM getNum response: {data}")
    return None


async def _poll_onlinesim_code(order_id: str, wait_time: int):
    url = "https://onlinesim.io/api/getState.php"
    params = {"apikey": Config.ONLINESIM_API_KEY, "tzid": order_id}
    deadline = asyncio.get_running_loop().time() + wait_time

    async with aiohttp.ClientSession() as session:
        while asyncio.get_running_loop().time() < deadline:
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        msg = data[0].get("msg", "")
                        if msg:
                            code_match = re.search(r'(\d{5,8})', str(msg))
                            if code_match:
                                code = code_match.group(1)
                                logger.info(f"OnlineSIM code received: {code}")
                                return code
            except Exception as e:
                logger.warning(f"OnlineSIM poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    logger.warning("OnlineSIM: timed out waiting for code")
    return None


async def _cancel_onlinesim_order(order_id: str):
    url = "https://onlinesim.io/api/setOperationRevise.php"
    params = {"apikey": Config.ONLINESIM_API_KEY, "tzid": order_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            logger.info(f"OnlineSIM cancel response: {resp.status}")


# ══════════════════════════════════════════════════════════════════════════════
# GetSMS implementation
# ══════════════════════════════════════════════════════════════════════════════

async def _get_getsms_phone():
    url = "https://api.getsms.io/stubs/handler_api.php"
    params = {
        "api_key": Config.GETSMS_API_KEY,
        "action": "getNumber",
        "service": "go",
        "country": Config.GETSMS_COUNTRY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = (await resp.text()).strip()

    if text.startswith("ACCESS_NUMBER"):
        parts = text.split(":")
        if len(parts) >= 3:
            return {"phone": parts[2], "id": parts[1]}

    logger.warning(f"GetSMS getNumber response: {text}")
    return None


async def _poll_getsms_code(order_id: str, wait_time: int):
    url = "https://api.getsms.io/stubs/handler_api.php"
    params = {
        "api_key": Config.GETSMS_API_KEY,
        "action": "getStatus",
        "id": order_id,
    }
    deadline = asyncio.get_running_loop().time() + wait_time

    async with aiohttp.ClientSession() as session:
        while asyncio.get_running_loop().time() < deadline:
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = (await resp.text()).strip()
                    if text.startswith("STATUS_OK"):
                        code = text.split(":")[1]
                        logger.info(f"GetSMS code received: {code}")
                        return code
                    elif text == "STATUS_CANCEL":
                        return None
            except Exception as e:
                logger.warning(f"GetSMS poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    logger.warning("GetSMS: timed out waiting for code")
    return None


async def _cancel_getsms_order(order_id: str):
    url = "https://api.getsms.io/stubs/handler_api.php"
    params = {"api_key": Config.GETSMS_API_KEY, "action": "setStatus", "id": order_id, "status": 8}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            logger.info(f"GetSMS cancel response: {resp.status}")


async def _finish_getsms_order(order_id: str):
    url = "https://api.getsms.io/stubs/handler_api.php"
    params = {"api_key": Config.GETSMS_API_KEY, "action": "setStatus", "id": order_id, "status": 6}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            logger.info(f"GetSMS finish response: {resp.status}")


# ══════════════════════════════════════════════════════════════════════════════
# HeroSMS implementation (SMS-Activate compatible API)
# ══════════════════════════════════════════════════════════════════════════════

def _herosms_headers():
    return {"Accept": "application/json"}


async def _get_herosms_balance():
    url = "https://hero-sms.com/stubs/handler_api.php"
    params = {"api_key": Config.HEROSMS_API_KEY, "action": "getBalance"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=_herosms_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            if text.startswith("ACCESS_BALANCE:"):
                balance = float(text.split(":")[1])
                logger.info(f"HeroSMS balance: {balance}")
                return balance
            else:
                logger.error(f"HeroSMS balance check failed: {text}")
    return None


async def _get_herosms_phone():
    balance = await _get_herosms_balance()
    if balance is not None and balance < 1:
        logger.error(f"HeroSMS balance too low: {balance}")
        return None

    url = "https://hero-sms.com/stubs/handler_api.php"
    params = {
        "api_key": Config.HEROSMS_API_KEY,
        "action": "getNumber",
        "service": "go",  # Google service code
        "country": Config.HEROSMS_COUNTRY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=_herosms_headers(), timeout=aiohttp.ClientTimeout(total=15)) as resp:
            text = (await resp.text()).strip()

    if text.startswith("ACCESS_NUMBER"):
        parts = text.split(":")
        if len(parts) >= 3:
            return {"phone": parts[2], "id": parts[1]}
    elif "NO_NUMBERS" in text:
        logger.warning("HeroSMS: no numbers available")
    elif "NO_BALANCE" in text:
        logger.error("HeroSMS: insufficient balance")
    else:
        logger.warning(f"HeroSMS response: {text}")
    return None


async def _poll_herosms_code(order_id: str, wait_time: int):
    url = "https://hero-sms.com/stubs/handler_api.php"
    params = {
        "api_key": Config.HEROSMS_API_KEY,
        "action": "getStatus",
        "id": order_id,
    }
    deadline = asyncio.get_running_loop().time() + wait_time

    async with aiohttp.ClientSession() as session:
        while asyncio.get_running_loop().time() < deadline:
            try:
                async with session.get(url, params=params, headers=_herosms_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = (await resp.text()).strip()
                    if text.startswith("STATUS_OK"):
                        code = text.split(":")[1]
                        logger.info(f"HeroSMS code received: {code}")
                        return code
                    elif text == "STATUS_CANCEL":
                        logger.warning("HeroSMS: order cancelled")
                        return None
            except Exception as e:
                logger.warning(f"HeroSMS poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    logger.warning("HeroSMS: timed out waiting for code")
    return None


async def _cancel_herosms_order(order_id: str):
    url = "https://hero-sms.com/stubs/handler_api.php"
    params = {"api_key": Config.HEROSMS_API_KEY, "action": "setStatus", "id": order_id, "status": 8}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=_herosms_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            logger.info(f"HeroSMS cancel response: {text}")


async def _finish_herosms_order(order_id: str):
    url = "https://hero-sms.com/stubs/handler_api.php"
    params = {"api_key": Config.HEROSMS_API_KEY, "action": "setStatus", "id": order_id, "status": 6}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=_herosms_headers(), timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = (await resp.text()).strip()
            logger.info(f"HeroSMS finish response: {text}")
