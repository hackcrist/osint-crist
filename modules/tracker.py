import aiohttp
import json
import os
from pathlib import Path

TRACKER_DOMAIN = "porkyvipff.com"
TRACKER_FILE = "track.php"
TRACKER_SECRET = "osint2026"
LOGS_DIR = Path(__file__).parent.parent / "tracker" / "logs"

def generate_link(link_id: str) -> str:
    return f"https://{TRACKER_DOMAIN}/{TRACKER_FILE}?c={link_id}"

async def fetch_logs(link_id: str) -> dict:
    url = f"https://{TRACKER_DOMAIN}/{TRACKER_FILE}?c={link_id}&key={TRACKER_SECRET}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"success": True, "hits": data, "count": len(data)}
                return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def fetch_all_logs(link_ids: list) -> dict:
    results = {}
    for lid in link_ids:
        data = await fetch_logs(lid)
        results[lid] = data
    return results

def save_link_id(name: str, link_id: str):
    db_path = Path(__file__).parent.parent / "tracker" / "links.json"
    db_path.parent.mkdir(exist_ok=True)
    links = {}
    if db_path.exists():
        with open(db_path) as f:
            links = json.load(f)
    links[name] = link_id
    with open(db_path, "w") as f:
        json.dump(links, f, indent=2)
    return link_id

def get_links() -> dict:
    db_path = Path(__file__).parent.parent / "tracker" / "links.json"
    if db_path.exists():
        with open(db_path) as f:
            return json.load(f)
    return {}
