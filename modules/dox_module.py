import re
import asyncio
from utils.formatting import bold, code

def detect_input_type(text: str) -> str:
    text = text.strip()
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', text):
        return "email"
    if re.match(r'^\+?\d{7,15}$', text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")):
        return "phone"
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
        return "ip"
    if re.match(r'^[a-zA-Z0-9_]{3,}$', text):
        return "username"
    return "name"

async def full_dox(target: str) -> str:
    target = target.strip()
    source_type = detect_input_type(target)
    tasks = {}
    lines = [
        f"🚀 {bold('DOX COMPLETO')}\n",
        f"Objetivo: {code(target)}",
        f"Tipo detectado: {source_type.upper()}\n",
        "━" * 30
    ]

    if source_type == "email":
        from modules.email_lookup import lookup_email
        from modules.breach_check import check_breach

        async def do_email():
            r = await lookup_email(target)
            parts = []
            if "error" in r:
                parts.append(f"  ❌ {r['error']}")
                return "\n".join(parts)
            parts.append(f"\n{bold('📧 EMAIL')}")
            if r.get("mx_status") and not r["mx_status"].get("error"):
                parts.append(f"  MX: {', '.join(r['mx_status'].get('mx_records', []))}")
            if r.get("disposable") and r["disposable"].get("disposable"):
                parts.append(f"  ⚠️ Desechable: Sí")
            if r.get("gravatar") and r["gravatar"].get("profile_url"):
                parts.append(f"  Gravatar: {r['gravatar']['profile_url']}")
            if r.get("hunter_verify") and r["hunter_verify"].get("data"):
                hd = r["hunter_verify"]["data"]
                parts.append(f"  Hunter Score: {hd.get('score', 'N/A')}")
                parts.append(f"  Formato: {hd.get('pattern', 'N/A')}")
            return "\n".join(parts)

        async def do_breach():
            r = await check_breach(target)
            parts = [f"\n{bold('🔓 FILTRACIONES')}"]
            if r.get("leak_check") and r["leak_check"].get("found"):
                parts.append(f"  Leak-Check: {r['leak_check']['message']}")
            if r.get("firefox") and r["firefox"].get("found"):
                parts.append(f"  Firefox Monitor: {r['firefox']['message']}")
            if r.get("scylla") and r["scylla"].get("found"):
                parts.append(f"  Scylla.so: {r['scylla']['message']}")
            if r.get("pastebin"):
                for p in r["pastebin"][:3]:
                    parts.append(f"  Pastebin: {p.get('url', 'N/A')}")
            if r.get("intelx") and r["intelx"].get("found"):
                parts.append(f"  IntelX: {r['intelx']['message']}")
            if len(parts) == 1:
                parts.append("  Sin filtraciones encontradas")
            return "\n".join(parts)

        tasks["email"] = do_email()
        tasks["breach"] = do_breach()

    elif source_type == "phone":
        from modules.phone_lookup import lookup_phone
        from modules.spam_check import check_spam

        async def do_phone():
            r = await asyncio.get_event_loop().run_in_executor(None, lookup_phone, target)
            parts = [f"\n{bold('📞 TELÉFONO')}"]
            if "error" in r:
                parts.append(f"  ❌ {r['error']}")
                return "\n".join(parts)
            parts.append(f"  País: {r.get('country', 'N/A')} {r.get('flag', '')}")
            parts.append(f"  Operador: {r.get('carrier', 'N/A')}")
            parts.append(f"  Tipo: {r.get('line_type', 'N/A')}")
            parts.append(f"  Zona: {r.get('timezone', 'N/A')}")
            parts.append(f"  Ubicación: {r.get('location', 'N/A')}")
            return "\n".join(parts)

        async def do_spam():
            r = await check_spam(target)
            parts = [f"\n{bold('📵 SPAM')}"]
            if "error" in r:
                parts.append(f"  {r['error']}")
                return "\n".join(parts)
            parts.append(f"  Tellows: {r.get('tellows', {}).get('score', 'N/A')}/10")
            parts.append(f"  SpamCalls: {r.get('spamcalls', {}).get('score', 'N/A')}/10")
            return "\n".join(parts)

        tasks["phone"] = do_phone()
        tasks["spam"] = do_spam()

    elif source_type == "username":
        from modules.username_search import search_username
        from modules.breach_check import check_breach

        async def do_user():
            r = await search_username(target)
            parts = [f"\n{bold('👤 USUARIO')}"]
            if r.get("total_found", 0) > 0:
                for p in r["platforms"]:
                    parts.append(f"  ✅ {p['name']}: {p.get('url', '')}")
            else:
                parts.append("  Sin resultados en plataformas")
            extras = r.get("extras", {})
            if extras.get("github"):
                g = extras["github"]
                parts.append(f"\n  GitHub: {g.get('bio', 'Sin bio')}")
                parts.append(f"  Repos: {g.get('repos', 'N/A')} · Seguidores: {g.get('followers', 'N/A')}")
            return "\n".join(parts)

        async def do_breach_username():
            r = await check_breach(target)
            parts = [f"\n{bold('🔓 FILTRACIONES')}"]
            if r.get("leak_check") and r["leak_check"].get("found"):
                parts.append(f"  Leak-Check: {r['leak_check']['message']}")
            if r.get("pastebin"):
                for p in r["pastebin"][:3]:
                    parts.append(f"  Pastebin: {p.get('url', 'N/A')}")
            if len(parts) == 1:
                parts.append("  Sin filtraciones encontradas")
            return "\n".join(parts)

        tasks["user"] = do_user()
        tasks["breach"] = do_breach_username()

    elif source_type == "ip":
        from modules.ip_lookup import lookup_ip

        async def do_ip():
            r = await lookup_ip(target)
            parts = [f"\n{bold('🌐 IP')}"]
            if "error" in r:
                parts.append(f"  ❌ {r['error']}")
                return "\n".join(parts)
            parts.append(f"  ISP: {r.get('isp', 'N/A')}")
            parts.append(f"  País: {r.get('country', 'N/A')} {r.get('flag', '')}")
            parts.append(f"  Ciudad: {r.get('city', 'N/A')}, {r.get('region', 'N/A')}")
            parts.append(f"  Coordenadas: {r.get('lat', 'N/A')}, {r.get('lon', 'N/A')}")
            parts.append(f"  Organización: {r.get('org', 'N/A')}")
            if r.get("vpn"):
                parts.append(f"  🛡️ VPN/Proxy/Tor: {'Sí' if r['vpn'].get('proxy') else 'No'}")
            return "\n".join(parts)

        tasks["ip"] = do_ip()

    else:
        from modules.person_search import search_person
        from modules.fbi_wanted import search_fbi

        async def do_person():
            r = await search_person(target)
            parts = [f"\n{bold('👤 PERSONA')}"]
            if r.get("wikipedia"):
                parts.append(f"  Wikipedia: {r['wikipedia'].get('extract', '')[:300]}")
            if r.get("duckduckgo"):
                parts.append(f"  DuckDuckGo: {r['duckduckgo'][0][:300] if r['duckduckgo'] else 'N/A'}")
            if r.get("links"):
                parts.append(f"\n  Enlaces encontrados: {len(r['links'])}")
                for link in r["links"][:5]:
                    parts.append(f"  🔗 {link}")
            if r.get("dorks"):
                parts.append(f"\n  Google Dorks sugeridos:\n    {chr(10).join(r['dorks'][:5])}")
            return "\n".join(parts)

        async def do_fbi():
            r = await search_fbi(target)
            parts = [f"\n{bold('🚔 FBI')}"]
            if r.get("total", 0) > 0:
                for item in r.get("items", [])[:3]:
                    parts.append(f"  {item.get('title', 'N/A')}")
                    if item.get("reward"):
                        parts.append(f"  Recompensa: {item['reward']}")
            else:
                parts.append("  Sin coincidencias en FBI")
            return "\n".join(parts)

        tasks["person"] = do_person()
        tasks["fbi"] = do_fbi()

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            lines.append(f"\n  ❌ Error: {str(r)[:200]}")
        elif r:
            lines.append(r)
        lines.append("")

    lines.append(f"\n{code('⚡ Powered by OSINT BOT')}")
    return "\n".join(lines)