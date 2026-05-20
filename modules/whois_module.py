import aiohttp
import re
from urllib.parse import urlparse

WHOIS_SERVERS = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "info": "whois.afilias.net",
    "io": "whois.nic.io",
    "dev": "whois.nic.google",
    "app": "whois.nic.google",
    "xyz": "whois.nic.xyz",
    "es": "whois.nic.es",
    "mx": "whois.mx",
    "co": "whois.nic.co",
}

async def whois_lookup(domain: str) -> dict:
    if not domain.startswith("http"):
        domain = "https://" + domain
    parsed = urlparse(domain)
    hostname = parsed.netloc or parsed.path
    hostname = hostname.split(":")[0].strip()

    tld = hostname.split(".")[-1].lower()
    server = WHOIS_SERVERS.get(tld, "whois.verisign-grs.com")

    try:
        import asyncio
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(server, 43), timeout=8
        )
        writer.write(f"{hostname}\r\n".encode())
        await writer.drain()

        data = b""
        while True:
            chunk = await asyncio.wait_for(reader.read(4096), timeout=5)
            if not chunk:
                break
            data += chunk

        writer.close()
        text = data.decode("utf-8", errors="ignore")

        fields = {
            "Domain Name": "dominio",
            "Registry Domain ID": "id",
            "Registrar": "registrador",
            "Creation Date": "creado",
            "Registry Expiry Date": "expira",
            "Expiration Date": "expira",
            "Name Server": "nameservers",
            "Registrant Name": "registrante",
            "Registrant Organization": "organizacion",
            "Registrant Country": "pais",
            "Admin Email": "email_admin",
        }

        result = {"domain": hostname, "raw": text[:1000]}
        for search_key, result_key in fields.items():
            match = re.search(rf"{search_key}:\s*(.+)", text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if result_key not in result:
                    result[result_key] = val
                elif isinstance(result[result_key], list):
                    result[result_key].append(val)
                else:
                    result[result_key] = [result[result_key], val]

        return result

    except asyncio.TimeoutError:
        return {"domain": hostname, "error": "Timeout en servidor WHOIS"}
    except Exception as e:
        return {"domain": hostname, "error": str(e)}
