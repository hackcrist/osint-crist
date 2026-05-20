import aiohttp
import asyncio

PLATFORMS = [
    {"name": "GitHub",   "url": "https://github.com/{}",       "api": "https://api.github.com/users/{}"},
    {"name": "Twitter/X","url": "https://x.com/{}",            "api": None},
    {"name": "Instagram","url": "https://instagram.com/{}",    "api": None},
    {"name": "Reddit",   "url": "https://reddit.com/user/{}",  "api": None},
    {"name": "TikTok",   "url": "https://tiktok.com/@{}",      "api": None},
    {"name": "YouTube",  "url": "https://youtube.com/@{}",     "api": None},
    {"name": "Pinterest","url": "https://pinterest.com/{}",    "api": None},
    {"name": "Tumblr",   "url": "https://{}.tumblr.com",       "api": None},
    {"name": "Twitch",   "url": "https://twitch.tv/{}",        "api": None},
    {"name": "Patreon",  "url": "https://patreon.com/{}",      "api": None},
    {"name": "Keybase",  "url": "https://keybase.io/{}",       "api": None},
    {"name": "Telegram", "url": "https://t.me/{}",             "api": None},
    {"name": "Medium",   "url": "https://medium.com/@{}",      "api": None},
    {"name": "Dev.to",   "url": "https://dev.to/{}",           "api": None},
    {"name": "Steam",    "url": "https://steamcommunity.com/id/{}", "api": None},
    {"name": "Spotify",  "url": "https://open.spotify.com/user/{}", "api": None},
    {"name": "SoundCloud","url": "https://soundcloud.com/{}",  "api": None},
    {"name": "Behance",  "url": "https://behance.net/{}",      "api": None},
    {"name": "Dribbble", "url": "https://dribbble.com/{}",     "api": None},
    {"name": "VK",       "url": "https://vk.com/{}",           "api": None},
    {"name": "Facebook", "url": "https://facebook.com/{}",     "api": None},
    {"name": "Linktree", "url": "https://linktr.ee/{}",        "api": None},
    {"name": "Replit",   "url": "https://replit.com/@{}",      "api": None},
    {"name": "HackerNews","url": "https://news.ycombinator.com/user?id={}", "api": None},
    {"name": "TryHackMe","url": "https://tryhackme.com/p/{}",   "api": None},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}", "api": None},
    {"name": "Pastebin", "url": "https://pastebin.com/u/{}",   "api": None},
    {"name": "BuyMeACoffee", "url": "https://buymeacoffee.com/{}", "api": None},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}", "api": None},
    {"name": "Fiverr",   "url": "https://fiverr.com/{}",       "api": None},
]

async def check_platform(session: aiohttp.ClientSession, platform: dict, username: str) -> dict:
    url = platform["url"].format(username)
    try:
        async with session.get(url, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            return {"name": platform["name"], "exists": resp.status != 404, "url": url}
    except:
        return {"name": platform["name"], "exists": False, "url": url}

async def fetch_github_profile(session: aiohttp.ClientSession, username: str) -> dict:
    try:
        async with session.get(
            f"https://api.github.com/users/{username}",
            timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "name": data.get("name", ""),
                    "bio": data.get("bio", ""),
                    "avatar": data.get("avatar_url", ""),
                    "company": data.get("company", ""),
                    "location": data.get("location", ""),
                    "repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0),
                }
    except:
        pass
    return {}

async def fetch_instagram_info(session: aiohttp.ClientSession, username: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(
            f"https://www.instagram.com/{username}/?__a=1",
            headers=headers, timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                user = data.get("graphql", {}).get("user", {})
                if user:
                    return {
                        "name": user.get("full_name", ""),
                        "bio": user.get("biography", ""),
                        "posts": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                        "followers": user.get("edge_followed_by", {}).get("count", 0),
                    }
    except:
        pass
    return {}

async def search_username(username: str) -> dict:
    found_platforms = []
    not_found = []

    connector = aiohttp.TCPConnector(limit=10, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_platform(session, p, username) for p in PLATFORMS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, dict):
                if r["exists"]:
                    found_platforms.append(r)
                else:
                    not_found.append(r["name"])

        extras = {}
        if any(p["name"] == "GitHub" for p in found_platforms):
            extras["github"] = await fetch_github_profile(session, username)

    return {
        "username": username,
        "total_checked": len(PLATFORMS),
        "total_found": len(found_platforms),
        "platforms": found_platforms,
        "not_found": not_found,
        "extras": extras,
    }
