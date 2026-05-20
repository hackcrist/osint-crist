import aiohttp
import asyncio

async def check_leak_check(query: str, session: aiohttp.ClientSession) -> dict:
    try:
        async with session.get(
            f"https://leak-check.net/api?key=public&check={query}",
            timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {"source": "Leak-Check", "found": True, "data": str(data)[:200]}
            return {"source": "Leak-Check", "found": False}
    except:
        return {"source": "Leak-Check", "error": "Timeout"}

async def check_firefox_monitor(email: str, session: aiohttp.ClientSession) -> dict:
    return {"source": "Firefox Monitor", "url": "https://monitor.firefox.com/", "note": "Verifica manualmente en el enlace"}

async def check_pastebin(query: str, session: aiohttp.ClientSession) -> list:
    results = []
    urls = [
        f"https://psbdmp.ws/api/search/{query}",
    ]
    for url in urls:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    count = len(data) if isinstance(data, list) else 0
                    results.append({"source": "Pastebin Dumps", "found": count > 0, "count": count})
                else:
                    results.append({"source": "Pastebin Dumps", "found": False})
        except:
            results.append({"source": "Pastebin Dumps", "error": "Timeout"})
    return results

async def check_scylla(query: str, session: aiohttp.ClientSession) -> dict:
    try:
        async with session.get(
            f"https://scylla.so/search?q={query}",
            timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            return {"source": "Scylla.so", "found": resp.status == 200, "url": f"https://scylla.so/search?q={query}"}
    except:
        return {"source": "Scylla.so", "error": "Timeout"}

async def check_intelx(query: str, session: aiohttp.ClientSession) -> dict:
    return {"source": "IntelligenceX", "url": f"https://intelx.io/?s={query}", "note": "Busca manualmente en el enlace"}

async def check_username_paste(username: str, session: aiohttp.ClientSession) -> list:
    results = []
    sites = [
        f"https://www.google.com/search?q=%22{username}%22+leak+OR+breach+OR+dump",
        f"https://www.google.com/search?q=%22{username}%22+password+OR+combo",
    ]
    for url in sites:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                results.append({"source": "Google Dork", "url": url, "found": resp.status == 200})
        except:
            pass
    return results

async def check_breach(query: str) -> dict:
    is_email = "@" in query
    results = {}

    async with aiohttp.ClientSession() as session:
        if is_email:
            tasks = {
                "leak_check": check_leak_check(query, session),
                "firefox": check_firefox_monitor(query, session),
                "pastebin": check_pastebin(query, session),
                "intelx": check_intelx(query, session),
            }
        else:
            tasks = {
                "leak_check": check_leak_check(query, session),
                "pastebin": check_pastebin(query, session),
                "intelx": check_intelx(query, session),
                "scylla": check_scylla(query, session),
                "google": check_username_paste(query, session),
            }

        for key, coro in tasks.items():
            try:
                results[key] = await coro
            except Exception as e:
                results[key] = {"error": str(e)}

    return {
        "query": query,
        "type": "email" if is_email else "username",
        "results": results,
    }
