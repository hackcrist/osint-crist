import aiohttp
from urllib.parse import quote

async def search_fbi(name: str) -> dict:
    url = "https://api.fbi.gov/wanted/v1/list"
    params = {"title": name, "pageSize": 5}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items", [])
                    results = []
                    for item in items:
                        results.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", "")[:300],
                            "subjects": item.get("subjects", []),
                            "status": item.get("status", ""),
                            "reward": item.get("reward_text", ""),
                            "sex": item.get("sex", ""),
                            "race": item.get("race", ""),
                            "hair": item.get("hair", ""),
                            "height": item.get("height_max", ""),
                            "weight": item.get("weight", ""),
                            "place_of_birth": item.get("place_of_birth", ""),
                            "aliases": item.get("aliases", [])[:5],
                            "caution": item.get("caution", "")[:200],
                            "url": item.get("url", ""),
                            "images": [img.get("thumb", "") for img in item.get("images", [])[:2]],
                        })
                    return {
                        "total": data.get("total", 0),
                        "results": results,
                        "query": name,
                    }
                return {"error": f"HTTP {resp.status}", "results": []}
        except Exception as e:
            return {"error": str(e), "results": []}

async def list_top_ten() -> list:
    url = "https://api.fbi.gov/wanted/v1/list"
    params = {"pageSize": 10}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items", [])
                    return [{
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "reward": item.get("reward_text", ""),
                    } for item in items[:10]]
                return []
        except:
            return []
