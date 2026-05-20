import aiohttp
from urllib.parse import quote

async def search_wikipedia(name: str) -> dict:
    url = (
        "https://es.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={quote(name)}"
        f"&format=json&srlimit=5&srprop=snippet|pageid"
    )
    headers = {"User-Agent": "OSINTBot/1.0"}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    for item in data.get("query", {}).get("search", []):
                        results.append({
                            "title": item["title"],
                            "snippet": item["snippet"].replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                            "url": f"https://es.wikipedia.org/wiki/{quote(item['title'].replace(' ', '_'))}"
                        })
                    return {"found": len(results) > 0, "results": results}
                return {"found": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"found": False, "error": str(e)}

async def search_duckduckgo(name: str) -> list:
    url = f"https://api.duckduckgo.com/?q={quote(name)}&format=json&no_html=1&t=osintbot"
    headers = {"User-Agent": "OSINTBot/1.0"}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    abstract = data.get("AbstractText", "")
                    if abstract:
                        results.append({"tipo": "Resumen", "texto": abstract[:500], "url": data.get("AbstractURL", "")})
                    infobox = data.get("Infobox", "")
                    if infobox:
                        results.append({"tipo": "Infobox", "texto": str(infobox)[:300]})
                    for topic in data.get("RelatedTopics", [])[:5]:
                        if "Text" in topic:
                            results.append({"tipo": "Relacionado", "texto": topic["Text"][:300], "url": topic.get("FirstURL", "")})
                    return results
                return []
        except:
            return []

def search_google_dorks(name: str) -> dict:
    encoded = quote(name)
    dorks = {
        "linkedin": f'https://www.google.com/search?q=site:linkedin.com/in/+"{encoded}"',
        "facebook": f'https://www.google.com/search?q=site:facebook.com+"{encoded}"',
        "twitter": f'https://www.google.com/search?q=site:twitter.com+"{encoded}"',
        "instagram": f'https://www.google.com/search?q=site:instagram.com+"{encoded}"',
        "tiktok": f'https://www.google.com/search?q=site:tiktok.com+"{encoded}"',
        "reddit": f'https://www.google.com/search?q=site:reddit.com+"{encoded}"',
        "youtube": f'https://www.google.com/search?q=site:youtube.com+"{encoded}"',
        "noticias": f'https://www.google.com/search?q="{encoded}"+noticias',
        "documentos": f'https://www.google.com/search?q="{encoded}"+filetype:pdf',
    }
    return dorks

def build_search_links(name: str) -> dict:
    encoded = quote(name)
    return {
        "google": f"https://www.google.com/search?q={encoded}",
        "google_dork": f"https://www.google.com/search?q=%22{encoded}%22+OR+%22{encoded.replace(' ', '+')}%22",
        "duckduckgo": f"https://duckduckgo.com/?q={encoded}",
        "bing": f"https://www.bing.com/search?q={encoded}",
        "facebook": f"https://www.facebook.com/search/top?q={encoded}",
        "twitter": f"https://x.com/search?q={encoded}&src=typed_query",
        "linkedin": f"https://www.linkedin.com/search/results/all/?keywords={encoded}",
        "instagram": f"https://www.instagram.com/web/search/topsearch/?query={encoded}",
        "youtube": f"https://www.youtube.com/results?search_query={encoded}",
        "tiktok": f"https://www.tiktok.com/search?q={encoded}",
        "reddit": f"https://www.reddit.com/search/?q={encoded}",
    }

async def search_person(name: str) -> dict:
    wikipedia = await search_wikipedia(name)
    duckduckgo = await search_duckduckgo(name)
    dorks = search_google_dorks(name)
    search_links = build_search_links(name)

    return {
        "name": name,
        "wikipedia": wikipedia,
        "duckduckgo": duckduckgo,
        "dorks": dorks,
        "search_links": search_links,
    }
