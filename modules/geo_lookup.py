import aiohttp
from urllib.parse import quote

async def reverse_geocode(lat: float, lng: float) -> dict:
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?format=json&lat={lat}&lon={lng}&addressdetails=1&accept-language=es"
    )
    headers = {"User-Agent": "OSINTBot/1.0"}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    addr = data.get("address", {})
                    return {
                        "success": True,
                        "display_name": data.get("display_name", ""),
                        "lat": lat,
                        "lng": lng,
                        "osm_url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=15/{lat}/{lng}",
                        "google_url": f"https://www.google.com/maps?q={lat},{lng}",
                        "tipo": data.get("type", ""),
                        "direccion": {
                            "calle": addr.get("road", ""),
                            "numero": addr.get("house_number", ""),
                            "ciudad": addr.get("city", addr.get("town", addr.get("village", ""))),
                            "estado": addr.get("state", ""),
                            "pais": addr.get("country", ""),
                            "codigo_postal": addr.get("postcode", ""),
                            "barrio": addr.get("suburb", addr.get("neighbourhood", "")),
                        }
                    }
                return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def parse_coordinates(text: str) -> tuple | None:
    import re
    text = text.strip().replace(",", " ").replace(";", " ")
    parts = re.findall(r"-?\d+\.?\d*", text)
    if len(parts) >= 2:
        try:
            lat = float(parts[0])
            lng = float(parts[1])
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return (lat, lng)
        except:
            pass
    return None
