import asyncio
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import aiohttp

def _convert_to_degrees(value):
    d, m, s = value
    return float(d) + float(m) / 60.0 + float(s) / 3600.0

def _get_gps_coords(gps_info):
    try:
        lat = _convert_to_degrees(gps_info[2])
        lon = _convert_to_degrees(gps_info[4])
        if gps_info[1] == "S":
            lat = -lat
        if gps_info[3] == "W":
            lon = -lon
        return lat, lon
    except:
        return None, None

async def extract_exif_from_url(url: str) -> dict:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {"error": f"No se pudo descargar la imagen (HTTP {resp.status})"}
                data = await resp.read()
                return await asyncio.get_event_loop().run_in_executor(None, _extract_exif, data)
        except Exception as e:
            return {"error": str(e)}

async def extract_exif_from_bytes(data: bytes) -> dict:
    return await asyncio.get_event_loop().run_in_executor(None, _extract_exif, data)

def _extract_exif(data: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(data))
    except:
        return {"error": "No se pudo abrir la imagen"}

    exif_data = img._getexif()
    if not exif_data:
        return {"error": "La imagen no tiene metadatos EXIF"}

    result = {}
    gps_info = {}

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            for gps_tag in value:
                sub_tag = GPSTAGS.get(gps_tag, gps_tag)
                gps_info[sub_tag] = value[gps_tag]
        elif isinstance(value, bytes):
            try:
                result[tag] = value.decode("utf-8", errors="replace")[:200]
            except:
                result[tag] = str(value)[:200]
        else:
            result[tag] = str(value)[:200]

    if gps_info:
        lat, lon = _get_gps_coords(gps_info)
        if lat and lon:
            result["GPS Latitud"] = str(lat)
            result["GPS Longitud"] = str(lon)
            result["GPS Mapa"] = f"https://www.google.com/maps?q={lat},{lon}"
            result["GPS OpenStreetMap"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"

    return result
