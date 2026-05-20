import aiohttp
from urllib.parse import quote

async def check_tellows(number: str) -> dict:
    clean = number.replace("+", "").replace(" ", "").replace("-", "")
    url = f"https://www.tellows.es/num/{clean}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    score = 0
                    if "spam" in text.lower() or "estafa" in text.lower():
                        score = 5
                    return {"source": "Tellows", "url": url, "score": score, "found": resp.status == 200}
                return {"source": "Tellows", "url": url, "score": 0, "found": False}
        except:
            return {"source": "Tellows", "error": "Error de conexión"}

async def check_spamcalls(number: str) -> dict:
    clean = number.replace("+", "").replace(" ", "")
    url = f"https://spamcalls.net/es/number/{clean}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return {"source": "SpamCalls", "url": url, "found": "comentario" in text.lower() or "report" in text.lower()}
                return {"source": "SpamCalls", "url": url, "found": False}
        except:
            return {"source": "SpamCalls", "error": "Error de conexión"}

async def search_google_spam(number: str) -> list:
    clean = number.replace("+", "").replace(" ", "")
    results = []
    queries = [
        f"https://www.google.com/search?q={clean}+spam",
        f"https://www.google.com/search?q=%22{clean}%22+estafa+teléfono",
    ]
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for url in queries:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        results.append({"url": url, "found": True})
                    else:
                        results.append({"url": url, "found": False})
            except:
                pass
    return results

async def check_spam(number: str) -> dict:
    import asyncio
    tellows, spamcalls = await asyncio.gather(
        check_tellows(number), check_spamcalls(number), return_exceptions=True
    )

    results = {}
    if not isinstance(tellows, Exception):
        results["tellows"] = tellows
    if not isinstance(spamcalls, Exception):
        results["spamcalls"] = spamcalls

    total_score = sum(
        d.get("score", 2) for d in results.values()
        if isinstance(d, dict) and d.get("found")
    )

    return {
        "number": number,
        "risk_score": min(total_score, 10),
        "sources": results,
    }
