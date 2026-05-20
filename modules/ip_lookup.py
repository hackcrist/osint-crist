import aiohttp
import socket
from config import IPLOCATE_KEY

async def get_public_ip() -> str:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("https://api.ipify.org?format=json") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("ip", "")
    except:
        pass
    return ""

async def lookup_ip(ip: str) -> dict:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query&lang=es") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "success":
                        try:
                            hostname = socket.gethostbyaddr(ip)[0]
                        except:
                            hostname = ""

                        result = {
                            "success": True,
                            "ip": data["query"],
                            "continente": data.get("continent", ""),
                            "codigo_continente": data.get("continentCode", ""),
                            "pais": data.get("country", ""),
                            "codigo_pais": data.get("countryCode", ""),
                            "region": data.get("regionName", ""),
                            "ciudad": data.get("city", ""),
                            "distrito": data.get("district", ""),
                            "codigo_postal": data.get("zip", ""),
                            "lat": data.get("lat"),
                            "lon": data.get("lon"),
                            "zona_horaria": data.get("timezone", ""),
                            "offset": data.get("offset", ""),
                            "moneda": data.get("currency", ""),
                            "isp": data.get("isp", ""),
                            "org": data.get("org", ""),
                            "asn": data.get("as", ""),
                            "asname": data.get("asname", ""),
                            "hostname": hostname,
                            "reverso": data.get("reverse", ""),
                            "mobile": data.get("mobile", False),
                            "proxy": data.get("proxy", False),
                            "hosting": data.get("hosting", False),
                            "map_url": f"https://www.google.com/maps?q={data['lat']},{data['lon']}",
                            "vpn": False,
                            "tor": False,
                            "abuse_email": "",
                            "abuse_phone": "",
                            "company_name": "",
                            "company_domain": "",
                        }

                        if IPLOCATE_KEY:
                            try:
                                async with session.get(f"https://iplocate.io/api/lookup/{ip}?apikey={IPLOCATE_KEY}") as iresp:
                                    if iresp.status == 200:
                                        ipl = await iresp.json()
                                        privacy = ipl.get("privacy", {})
                                        result["vpn"] = privacy.get("is_vpn", False)
                                        result["proxy"] = privacy.get("is_proxy", False)
                                        result["tor"] = privacy.get("is_tor", False)
                                        result["hosting"] = privacy.get("is_hosting", False)
                                        abuse = ipl.get("abuse", {})
                                        if abuse.get("email"):
                                            result["abuse_email"] = abuse["email"]
                                        if abuse.get("phone"):
                                            result["abuse_phone"] = abuse["phone"]
                                        company = ipl.get("company", {})
                                        if company.get("name"):
                                            result["company_name"] = company["name"]
                                        if company.get("domain"):
                                            result["company_domain"] = company["domain"]
                            except:
                                pass

                        return result
                    return {"success": False, "error": data.get("message", "Error desconocido")}
                return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def is_valid_ip(text: str) -> bool:
    import socket
    try:
        socket.inet_aton(text.strip())
        return True
    except:
        return False

async def resolve_domain(domain: str) -> list:
    try:
        return list(set([str(r) for r in socket.getaddrinfo(domain, 80)]))
    except:
        return []
