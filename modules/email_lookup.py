import asyncio
import dns.resolver
import aiohttp
from utils.validators import is_valid_email
from config import HUNTER_KEY

async def check_gravatar(email: str) -> dict:
    import hashlib
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entry = data.get("entry", [{}])[0]
                    return {
                        "has_gravatar": True,
                        "profile_url": f"https://www.gravatar.com/{email_hash}",
                        "avatar_url": f"https://www.gravatar.com/avatar/{email_hash}?s=200",
                        "display_name": entry.get("displayName", ""),
                        "location": entry.get("currentLocation", ""),
                    }
        except:
            pass
    return {"has_gravatar": False}

async def check_mx(email: str) -> dict:
    domain = email.split("@")[1]
    try:
        records = dns.resolver.resolve(domain, "MX", lifetime=5)
        mx_servers = [str(r.exchange) for r in records]
        return {"has_mx": True, "mx_servers": mx_servers[:5]}
    except:
        return {"has_mx": False}

async def check_disposable(email: str) -> dict:
    domain = email.split("@")[1]
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        try:
            async with session.get(f"https://open.kickbox.com/v1/disposable/{domain}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"is_disposable": data.get("disposable", False)}
        except:
            pass
    return {"is_disposable": False}

async def search_email_breaches(email: str) -> list:
    results = []
    sources = [
        {"name": "Leak-Check", "url": f"https://leak-check.net/api?key=public&check={email}"},
        {"name": "Intelligence X", "url": f"https://intelx.io/?s={email}"},
    ]
    for source in sources:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(source["url"]) as resp:
                    if resp.status == 200:
                        results.append(f"{source['name']}: Datos encontrados")
                    else:
                        results.append(f"{source['name']}: Sin resultados públicos")
        except:
            results.append(f"{source['name']}: Error de conexión")
    return results

async def hunter_verify(email: str) -> dict:
    if not HUNTER_KEY:
        return {"error": "Sin API key"}
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_KEY}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    d = data.get("data", {})
                    return {
                        "result": d.get("result", ""),
                        "score": d.get("score", 0),
                        "sources": d.get("sources", []),
                        "accept_all": d.get("accept_all", False),
                        "pattern": d.get("pattern", ""),
                    }
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

async def hunter_domain_search(domain: str) -> dict:
    if not HUNTER_KEY:
        return {"error": "Sin API key"}
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_KEY}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    d = data.get("data", {})
                    emails = d.get("emails", [])
                    return {
                        "total": len(emails),
                        "emails": [{"value": e.get("value", ""), "type": e.get("type", ""), "sources": e.get("sources", [])} for e in emails[:10]],
                        "pattern": d.get("pattern", ""),
                    }
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

async def lookup_email(email: str) -> dict:
    if not is_valid_email(email):
        return {"error": "Email inválido"}

    tasks = {
        "mx": check_mx(email),
        "disposable": check_disposable(email),
        "gravatar": check_gravatar(email),
        "breaches": search_email_breaches(email),
        "hunter_verify": hunter_verify(email),
    }

    results = {}
    for key, coro in tasks.items():
        try:
            results[key] = await coro
        except asyncio.TimeoutError:
            results[key] = {"error": "Timeout"}
        except Exception as e:
            results[key] = {"error": str(e)}

    return {
        "email": email,
        "domain": email.split("@")[1],
        "mx_status": results.get("mx", {}),
        "disposable": results.get("disposable", {}),
        "gravatar": results.get("gravatar", {}),
        "breaches": results.get("breaches", []),
        "hunter_verify": results.get("hunter_verify", {}),
    }
