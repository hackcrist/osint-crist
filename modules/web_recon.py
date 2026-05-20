import aiohttp
import ssl
import socket
import asyncio
from urllib.parse import urlparse
import dns.resolver
from config import VTOTAL_KEY

SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-frame-options": "X-Frame-Options",
    "x-content-type-options": "X-Content-Type-Options",
    "x-xss-protection": "X-XSS-Protection",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}

TECH_PATTERNS = {
    "cloudflare": {"headers": ["cf-ray", "server:cloudflare"]},
    "nginx": {"headers": ["server:nginx"]},
    "apache": {"headers": ["server:apache"]},
    "wordpress": {"headers": ["x-powered-by:wordpress"], "cookies": ["wordpress_"]},
    "cloudfront": {"headers": ["x-amz-cf-id"]},
    "google cloud": {"headers": ["x-goog-"]},
    "github pages": {"headers": ["server:github.com"]},
    "python/anyio": {"headers": ["server:python"]},
    "netlify": {"headers": ["server:netlify"]},
    "vercel": {"headers": ["x-vercel-id"]},
}

async def get_headers(url: str) -> dict:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url, allow_redirects=True, ssl=False) as resp:
                headers = dict(resp.headers)
                return {
                    "status": resp.status,
                    "server": headers.get("Server", headers.get("server", "N/A")),
                    "content_type": headers.get("Content-Type", "N/A"),
                    "cookies": list(resp.cookies.keys()),
                    "final_url": str(resp.url),
                    "all_headers": headers,
                }
        except Exception as e:
            return {"error": str(e)}

async def check_dns(domain: str) -> dict:
    records = {}
    for record_type in ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]:
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=5)
            records[record_type] = [str(r) for r in answers[:5]]
        except:
            records[record_type] = []
    return records

async def check_ssl(hostname: str, port: int = 443) -> dict:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    "issuer": dict(cert.get("issuer", [])),
                    "subject": dict(cert.get("subject", [])),
                    "expires": cert.get("notAfter", "N/A"),
                    "issued": cert.get("notBefore", "N/A"),
                    "valid": True,
                    "alt_names": cert.get("subjectAltName", []),
                }
    except Exception as e:
        return {"error": str(e), "valid": False}

async def check_common_paths(session: aiohttp.ClientSession, base: str) -> list:
    paths = [
        "robots.txt", "sitemap.xml", ".well-known/security.txt",
        ".env", ".git/config", "wp-admin/", "admin/",
        "backup/", "phpinfo.php", "crossdomain.xml",
        "server-status", ".htaccess", "config/", "login/",
        "api/", "swagger.json", "graphql",
    ]
    results = []
    for path in paths:
        try:
            url = f"{base.rstrip('/')}/{path}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=4), ssl=False) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    results.append({"path": path, "status": resp.status, "size": len(text)})
                elif resp.status in [301, 302, 303, 401, 403, 500]:
                    results.append({"path": path, "status": resp.status})
        except:
            pass
    return results

async def find_subdomains(domain: str) -> list:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    subs = set()
                    for entry in data:
                        name = entry.get("name_value", "")
                        for n in name.split("\n"):
                            n = n.strip().lower()
                            if n.endswith(f".{domain}") and n != f"*.{domain}":
                                subs.add(n)
                    return list(subs)[:30]
                return []
        except:
            return []

async def check_wayback(domain: str) -> dict:
    url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=5&fl=timestamp,original"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if len(data) > 1:
                        return {"snapshots": len(data) - 1, "first": data[1][0], "last": data[-1][0]}
                return {"snapshots": 0}
        except:
            return {"snapshots": 0}

def analyze_security(headers: dict) -> dict:
    found = []
    missing = []
    headers_lower = {k.lower(): v for k, v in headers.items()}
    for header, name in SECURITY_HEADERS.items():
        if header in headers_lower:
            found.append(name)
        else:
            missing.append(name)
    return {"present": found, "missing": missing}

def detect_tech(headers: dict) -> list:
    detected = []
    headers_lower = {k.lower(): v for k, v in headers.items()}
    for tech, patterns in TECH_PATTERNS.items():
        for pattern in patterns.get("headers", []):
            if ":" in pattern:
                key, val = pattern.split(":", 1)
                if key in headers_lower and val in headers_lower[key].lower():
                    detected.append(tech)
                    break
            elif pattern in headers_lower:
                detected.append(tech)
                break
    return detected

async def check_virustotal(domain: str) -> dict:
    if not VTOTAL_KEY:
        return {"error": "Sin API key"}
    headers = {"x-apikey": VTOTAL_KEY}
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    attrs = data.get("data", {}).get("attributes", {})
                    last_analysis = attrs.get("last_analysis_stats", {})
                    categories = attrs.get("categories", {})
                    return {
                        "malicioso": last_analysis.get("malicious", 0),
                        "sospechoso": last_analysis.get("suspicious", 0),
                        "limpio": last_analysis.get("harmless", 0),
                        "total": sum(last_analysis.values()) if last_analysis else 0,
                        "reputation": attrs.get("reputation", 0),
                        "categories": list(categories.values()) if categories else [],
                    }
                return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

async def recon(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    header_data = await get_headers(url)
    if "error" in header_data:
        return {"error": header_data["error"]}

    dns_task = check_dns(domain)
    ssl_task = check_ssl(domain)
    subs_task = find_subdomains(domain)
    wayback_task = check_wayback(domain)
    vt_task = check_virustotal(domain)

    dns_records, ssl_info, subdomains, wayback, vt = await asyncio.gather(
        dns_task, ssl_task, subs_task, wayback_task, vt_task, return_exceptions=True
    )

    common_paths = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        common_paths = await check_common_paths(session, url)

    sec = analyze_security(header_data.get("all_headers", {}))
    tech = detect_tech(header_data.get("all_headers", {}))

    result = {
        "url": url,
        "domain": domain,
        "status": header_data.get("status"),
        "server": header_data.get("server"),
        "content_type": header_data.get("content_type"),
        "final_url": header_data.get("final_url"),
        "cookies": header_data.get("cookies", []),
        "dns": dns_records if not isinstance(dns_records, Exception) else {"error": str(dns_records)},
        "ssl": ssl_info if not isinstance(ssl_info, Exception) else {"error": str(ssl_info)},
        "security": sec,
        "technologies": tech,
        "common_paths": common_paths,
    }

    if not isinstance(subdomains, Exception) and subdomains:
        result["subdomains"] = subdomains[:20]

    if not isinstance(wayback, Exception) and wayback.get("snapshots", 0) > 0:
        result["wayback"] = wayback

    if not isinstance(vt, Exception) and "error" not in vt:
        result["virustotal"] = vt

    return result
