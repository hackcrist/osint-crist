import aiohttp
import asyncio
import re

async def search_psbdmp(query: str) -> list:
    results = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://psbdmp.ws/api/v3/search/{query}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list):
                        for item in data[:15]:
                            dmp_id = item.get("id", "")
                            text = item.get("text", "")
                            title = item.get("title", "")
                            results.append({
                                "id": dmp_id,
                                "title": title or "Sin título",
                                "url": f"https://pastebin.com/{dmp_id}",
                                "preview": text[:200] if text else "",
                                "raw": f"https://psbdmp.ws/raw/{dmp_id}",
                            })
    except:
        pass
    return results

async def search_google_pastes(query: str) -> list:
    results = []
    dork = f"site:pastebin.com \"{query}\""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with session.get(
                f"https://www.google.com/search?q={dork}&num=10",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    urls = re.findall(r'https?://pastebin\.com/[a-zA-Z0-9]+', html)
                    seen = set()
                    for url in urls:
                        if url not in seen:
                            seen.add(url)
                            results.append({
                                "source": "Google",
                                "url": url,
                                "title": "Paste en Pastebin",
                            })
    except:
        pass
    return results

async def search_scylla(query: str) -> list:
    results = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://scylla.so/search?q={query}",
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "Mozilla/5.0"},
            ) as resp:
                if resp.status == 200:
                    results.append({
                        "source": "Scylla.so",
                        "url": f"https://scylla.so/search?q={query}",
                        "title": "Resultados en Scylla",
                    })
    except:
        pass
    return results

async def search_pastes(query: str) -> dict:
    tasks = {
        "psbdmp": search_psbdmp(query),
        "scylla": search_scylla(query),
    }
    results = {}
    for key, coro in tasks.items():
        try:
            results[key] = await coro
        except:
            results[key] = []

    total = sum(len(v) for v in results.values())
    return {
        "query": query,
        "total": total,
        "psbdmp": results.get("psbdmp", []),
        "scylla": results.get("scylla", []),
    }