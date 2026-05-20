from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from modules.email_lookup import lookup_email, hunter_domain_search
from modules.phone_lookup import lookup_phone
from modules.username_search import search_username
from modules.breach_check import check_breach
from modules.geo_lookup import reverse_geocode, parse_coordinates
from modules.person_search import search_person
from modules.web_recon import recon
from modules.ip_lookup import lookup_ip, is_valid_ip, get_public_ip
from modules.whois_module import whois_lookup
from modules.exif_module import extract_exif_from_url, extract_exif_from_bytes
from modules.utils_module import generate_hashes, generate_qr
from modules.ai_assistant import ask_ai, extract_cmd, reset_memory
from modules.fbi_wanted import search_fbi, list_top_ten
from modules.spam_check import check_spam
from modules.tracker import generate_link, fetch_logs, save_link_id, get_links, TRACKER_DOMAIN
from modules.dox_module import full_dox, detect_input_type
from modules.paste_search import search_pastes
from modules.email_generator import gen_emails
from database.db import save_search
from utils.formatting import bold, code, link, paginate, esc
from core.logger import logger

router = Router()

@router.message(Command("email"))
async def cmd_email(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /email correo@ejemplo.com")
        return

    email = command.args.strip()
    await message.answer(f"{bold('🔍 Investigando email...')}\n{code(email)}")

    try:
        data = await lookup_email(email)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('📧 Resultados Email')}\n",
            f"Email: {code(data['email'])}",
            f"Dominio: {code(data['domain'])}",
            "",
        ]

        mx = data.get("mx_status", {})
        lines.append(f"{bold('📡 MX (Servidores de Correo)')}:")
        if mx.get("has_mx"):
            for srv in mx.get("mx_servers", []):
                lines.append(f"  • {code(srv)}")
        else:
            lines.append("  • Sin servidores MX")
        lines.append("")

        disp = data.get("disposable", {})
        lines.append(f"{bold('📬 Desechable')}:")
        lines.append(f"  {'⚠️ Sí' if disp.get('is_disposable') else '✅ No'}")
        lines.append("")

        grav = data.get("gravatar", {})
        lines.append(f"{bold('🖼️ Gravatar')}:")
        if grav.get("has_gravatar"):
            lines.append(f"  • Nombre: {grav.get('display_name', 'N/A')}")
            lines.append(f"  • Ubicación: {grav.get('location', 'N/A')}")
            lines.append(f"  • Perfil: {grav.get('profile_url', 'N/A')}")
        else:
            lines.append("  • Sin Gravatar asociado")
        lines.append("")

        hunter = data.get("hunter_verify", {})
        if hunter and "error" not in hunter:
            lines.append(f"{bold('🎯 Hunter.io Verificación')}:")
            lines.append(f"  Resultado: {hunter.get('result', 'N/A')}")
            lines.append(f"  Score: {hunter.get('score', 'N/A')}%")
            if hunter.get("pattern"):
                lines.append(f"  Patrón: {hunter['pattern']}")
            if hunter.get("accept_all"):
                lines.append(f"  Accept All: {'Sí' if hunter['accept_all'] else 'No'}")
            if hunter.get("sources"):
                lines.append(f"  Fuentes encontradas: {len(hunter['sources'])}")
            lines.append("")

        breaches = data.get("breaches", [])
        lines.append(f"{bold('🔓 Filtraciones')}:")
        if breaches:
            for b in breaches:
                lines.append(f"  • {b}")
        else:
            lines.append("  • Sin datos de filtraciones")
        lines.append("")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "email", email, result_text[:500])

        pages = paginate(result_text)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en email lookup")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("domain"))
async def cmd_domain(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /domain <dominio>\nEj: /domain ejemplo.com")
        return

    domain = command.args.strip()
    await message.answer(f"{bold('🔍 Buscando emails en dominio...')}\n{code(domain)}")

    try:
        data = await hunter_domain_search(domain)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('📧 Emails en dominio')}\n",
            f"Dominio: {code(domain)}",
            f"Emails encontrados: {data.get('total', 0)}",
            f"Patrón: {data.get('pattern', 'N/A')}",
            "",
        ]

        for e in data.get("emails", []):
            lines.append(f"  • {e['value']} ({e['type']})")
            if e.get("sources"):
                for s in e["sources"][:2]:
                    lines.append(f"    ↳ {s.get('uri', '')}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "domain", domain, result_text[:500])
        pages = paginate(result_text)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en domain search")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("phone"))
async def cmd_phone(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /phone +521234567890")
        return

    number = command.args.strip()
    await message.answer(f"{bold('🔍 Investigando teléfono...')}\n{code(number)}")

    try:
        data = lookup_phone(number)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('📞 Resultados Teléfono')}\n",
            f"Internacional: {code(data['internacional'])}",
            f"Nacional: {code(data['nacional'])}",
            f"E.164: {code(data['e164'])}",
            f"",
            f"{bold('📍 Ubicación')}: {data['ubicacion']}",
            f"{bold('🏢 Operador')}: {data['operador']}",
            f"{bold('📱 Tipo línea')}: {data['tipo_linea']}",
            f"{bold('🌐 Zona horaria')}: {data['zona_horaria']}",
            f"{bold('País')}: {data['bandera']} {data['codigo_pais']} ({data['pais_region']})",
        ]

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "phone", number, result_text[:500])
        await message.answer(result_text)

    except Exception as e:
        logger.exception("Error en phone lookup")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("user"))
async def cmd_user(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /user nombre_usuario")
        return

    username = command.args.strip()
    msg = await message.answer(f"{bold('🔍 Buscando usuario en 25+ plataformas...')}\n{code(username)}")

    try:
        data = await search_username(username)
        lines = [
            f"{bold('👤 Búsqueda de Usuario')}\n",
            f"Usuario: {code(data['username'])}",
            f"Plataformas revisadas: {data['total_checked']}",
            f"Encontrado en: {data['total_found']}",
            "",
            f"{bold('✅ Encontrado en')}:",
        ]

        if data["platforms"]:
            for p in data["platforms"]:
                lines.append(f"  • {link(p['name'], p['url'])}")
        else:
            lines.append("  • Ninguna")

        extras = data.get("extras", {})
        if extras.get("github"):
            gh = extras["github"]
            lines.append("")
            lines.append(f"{bold('🐙 GitHub Info')}:")
            if gh.get("name"): lines.append(f"  Nombre: {gh['name']}")
            if gh.get("bio"): lines.append(f"  Bio: {gh['bio'][:100]}")
            if gh.get("location"): lines.append(f"  Ubicación: {gh['location']}")
            if gh.get("company"): lines.append(f"  Empresa: {gh['company']}")
            lines.append(f"  Repos: {gh.get('repos', 0)} • Followers: {gh.get('followers', 0)}")

        if data["not_found"]:
            lines.append("")
            lines.append(f"{bold('❌ No encontrado en')}:")
            for name in data["not_found"]:
                lines.append(f"  • {name}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "user", username, result_text[:500])

        pages = paginate(result_text)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en username search")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("breach"))
async def cmd_breach(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /breach email o usuario")
        return

    query = command.args.strip()
    await message.answer(f"{bold('🔍 Buscando filtraciones...')}\n{code(query)}")

    try:
        data = await check_breach(query)
        lines = [
            f"{bold('🔓 Búsqueda de Filtraciones')}\n",
            f"Consulta: {code(data['query'])}",
            f"Tipo: {data['type']}",
            "",
        ]

        results = data.get("results", {})
        for source_key, source_data in results.items():
            if isinstance(source_data, dict):
                src_name = source_data.get("source", source_key)
                lines.append(f"{bold(f'📁 {src_name}')}:")
                if source_data.get("found"):
                    lines.append("  ⚠️ Posibles datos filtrados encontrados")
                elif source_data.get("error"):
                    lines.append(f"  ❌ {source_data['error']}")
                else:
                    lines.append("  ✅ Sin resultados públicos")
            elif isinstance(source_data, list):
                for item in source_data:
                    src_name = item.get("source", "")
                    lines.append(f"{bold(f'📁 {src_name}')}:")
                    if item.get("found"):
                        lines.append(f"  🔗 {item.get('url', 'N/A')}")
                    else:
                        lines.append("  ✅ Sin resultados")
            lines.append("")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "breach", query, result_text[:500])
        await message.answer(result_text, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en breach check")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("geo"))
async def cmd_geo(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /geo <lat, lng> o /geo <teléfono>\nEj: /geo 40.4168, -3.7038 o /geo +34612345678")
        return

    query = command.args.strip()
    is_phone = query.startswith("+")

    if is_phone:
        await message.answer(f"{bold('📍 Obteniendo ubicación del número...')}\n{code(query)}")
        try:
            data = lookup_phone(query)
            if "error" in data:
                await message.answer(f"Error: {data['error']}")
                return

            lines = [
                f"{bold('📍 Ubicación por Teléfono')}\n",
                f"{bold('Número')}: {code(data['internacional'])}",
                f"{bold('País')}: {data['bandera']} {data['codigo_pais']} ({data['pais_region']})",
                f"{bold('Ubicación')}: {data['ubicacion']}",
                f"{bold('Operador')}: {data['operador']}",
                f"{bold('Tipo línea')}: {data['tipo_linea']}",
                f"{bold('Zona horaria')}: {data['zona_horaria']}",
                "",
                f"{bold('🗺️ Mapa')}:",
                f"  • Google Maps: https://www.google.com/maps/search/{data['ubicacion']}",
            ]
            result_text = "\n".join(lines)
            await save_search(message.from_user.id, message.from_user.full_name, "geo", query, result_text[:500])
            await message.answer(result_text, disable_web_page_preview=True)
        except Exception as e:
            logger.exception("Error en geo phone lookup")
            await message.answer(f"Error inesperado: {str(e)}")
        return

    coords = parse_coordinates(query)
    if not coords:
        await message.answer("Formato inválido. Usa:\n  GPS: /geo lat, lng\n  Teléfono: /geo +código número")
        return

    lat, lng = coords
    await message.answer(f"{bold('📍 Obteniendo ubicación...')}\n{code(f'{lat}, {lng}')}")

    try:
        data = await reverse_geocode(lat, lng)
        if not data.get("success"):
            await message.answer(f"Error: {data.get('error', 'Desconocido')}")
            return

        dir_data = data["direccion"]
        lines = [
            f"{bold('📍 Ubicación GPS')}\n",
            f"{bold('Coordenadas')}: {code(f'{lat}, {lng}')}",
            f"{bold('Dirección')}: {data['display_name']}",
            "",
            f"{bold('📋 Detalles')}:",
            f"  • Calle: {dir_data['calle'] or 'N/A'} {dir_data['numero'] or ''}",
            f"  • Barrio: {dir_data['barrio'] or 'N/A'}",
            f"  • Ciudad: {dir_data['ciudad'] or 'N/A'}",
            f"  • Estado: {dir_data['estado'] or 'N/A'}",
            f"  • País: {dir_data['pais'] or 'N/A'}",
            f"  • CP: {dir_data['codigo_postal'] or 'N/A'}",
            "",
            f"{bold('🗺️ Mapas')}:",
            f"  • OpenStreetMap: {data['osm_url']}",
            f"  • Google Maps: {data['google_url']}",
        ]

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "geo", query, result_text[:500])
        await message.answer(result_text, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en geo lookup")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("person"))
async def cmd_person(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /person nombre completo\nEj: /person Lionel Messi")
        return

    name = command.args.strip()
    msg = await message.answer(f"{bold('🔍 Buscando información de persona...')}\n{code(name)}")

    try:
        data = await search_person(name)
        lines = [
            f"{bold('👤 Búsqueda de Persona')}\n",
            f"Nombre: {code(data['name'])}",
            "",
        ]

        wiki = data.get("wikipedia", {})
        if wiki.get("found"):
            lines.append(f"{bold('📖 Wikipedia')}:")
            for r in wiki.get("results", []):
                lines.append(f"  • {r['title']}")
                lines.append(f"    {r['snippet'][:200]}...")
                lines.append(f"    {r['url']}")
            lines.append("")
        else:
            lines.append(f"{bold('📖 Wikipedia')}: Sin resultados\n")

        ddg = data.get("duckduckgo", [])
        if ddg:
            lines.append(f"{bold('🔎 DuckDuckGo')}:")
            for r in ddg[:3]:
                if r.get("texto"):
                    lines.append(f"  • {r['texto'][:200]}")
                    if r.get("url"):
                        lines.append(f"    {r['url']}")
            lines.append("")

        dorks = data.get("dorks", {})
        if dorks:
            lines.append(f"{bold('🔍 Google Dorks')}:")
            dork_names = {
                "linkedin": "LinkedIn", "facebook": "Facebook", "twitter": "Twitter",
                "instagram": "Instagram", "tiktok": "TikTok", "reddit": "Reddit",
                "youtube": "YouTube", "noticias": "Noticias", "documentos": "Documentos (PDF)",
            }
            for key, icon in dork_names.items():
                url = dorks.get(key, "")
                if url:
                    lines.append(f"  • {icon}: {url}")

        links = data.get("search_links", {})
        lines.append(f"{bold('🔗 Búsquedas generales')}:")
        platform_icons = {
            "google": "Google", "duckduckgo": "DuckDuckGo", "bing": "Bing",
            "facebook": "Facebook", "twitter": "X/Twitter", "linkedin": "LinkedIn",
            "instagram": "Instagram", "youtube": "YouTube", "tiktok": "TikTok",
            "reddit": "Reddit",
        }
        for key, icon in platform_icons.items():
            url = links.get(key, "")
            if url:
                lines.append(f"  • {icon}: {url}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "person", name, result_text[:500])
        await message.answer(result_text, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en person search")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("web"))
async def cmd_web(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /web <url>\nEj: /web https://example.com")
        return

    url = command.args.strip()
    msg = await message.answer(f"{bold('🌐 Escaneando sitio web...')}\n{code(url)}")

    try:
        data = await recon(url)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('🌐 Web Recon')}\n",
            f"{bold('URL')}: {data['url']}",
            f"{bold('Estado')}: {data['status']}",
            f"{bold('Servidor')}: {data['server']}",
            f"{bold('Tipo')}: {data['content_type']}",
            f"{bold('Destino final')}: {data['final_url']}",
            f"{bold('Cookies')}: {len(data['cookies'])} establecidas",
            "",
        ]

        if data.get("technologies"):
            lines.append(f"{bold('🛠️ Tecnologías detectadas')}:")
            for t in data["technologies"]:
                lines.append(f"  • {t.capitalize()}")
            lines.append("")

        sec = data.get("security", {})
        lines.append(f"{bold('🔒 Seguridad')}:")
        if sec.get("present"):
            lines.append(f"  ✅ {', '.join(sec['present'])}")
        if sec.get("missing"):
            lines.append(f"  ❌ Faltan: {', '.join(sec['missing'])}")
        lines.append("")

        dns = data.get("dns", {})
        if isinstance(dns, dict) and "error" not in dns:
            lines.append(f"{bold('📡 DNS')}:")
            for rtype in ["A", "MX", "NS", "TXT"]:
                if dns.get(rtype):
                    lines.append(f"  {rtype}: {', '.join(dns[rtype][:3])}")
            lines.append("")

        ssl_info = data.get("ssl", {})
        if isinstance(ssl_info, dict) and ssl_info.get("valid"):
            lines.append(f"{bold('🔐 SSL')}: Válido")
            if ssl_info.get("issuer"):
                org = ssl_info["issuer"].get("organizationName", "N/A")
                lines.append(f"  Emisor: {org}")
            lines.append(f"  Expira: {ssl_info.get('expires', 'N/A')}")

        vt = data.get("virustotal")
        if vt:
            lines.append(f"{bold('🦠 VirusTotal')}:")
            if vt.get("malicioso", 0) > 0:
                lines.append(f"  🔴 Malicioso: {vt['malicioso']}/{vt['total']}")
            else:
                lines.append(f"  ✅ Limpio ({vt.get('limpio', 0)}/{vt.get('total', 0)})")
            lines.append(f"  Reputación: {vt.get('reputation', 0)}")
            if vt.get("categories"):
                lines.append(f"  Categorías: {', '.join(vt['categories'][:3])}")
            lines.append("")

        if data.get("subdomains"):
            lines.append(f"{bold('📂 Subdominios')}: {len(data['subdomains'])} encontrados")
            for s in data["subdomains"][:10]:
                lines.append(f"  • {s}")
            if len(data["subdomains"]) > 10:
                lines.append(f"  ... y {len(data['subdomains']) - 10} más")

        if data.get("wayback"):
            wb = data["wayback"]
            lines.append(f"{bold('📜 Wayback Machine')}: {wb.get('snapshots', 0)} snapshots")
            lines.append(f"  Primero: {wb.get('first', 'N/A')}")
            lines.append(f"  Último: {wb.get('last', 'N/A')}")

        if data.get("common_paths"):
            lines.append("")
            lines.append(f"{bold('📁 Rutas encontradas')}:")
            for p in data["common_paths"]:
                status_str = f"HTTP {p['status']}"
                lines.append(f"  • /{p['path']} → {status_str}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "web", url, result_text[:500])

        pages = paginate(result_text)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en web recon")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("ip"))
async def cmd_ip(message: types.Message, command: CommandObject):
    ip = (command.args or "").strip()
    if not ip:
        ip = await get_public_ip()
        if not ip:
            await message.answer("Usa: /ip <dirección IP>\nEj: /ip 8.8.8.8")
            return
        await message.answer(f"{bold('🌐 Tu IP pública')}: {code(ip)}\n\nObteniendo información...")

    await message.answer(f"{bold('📍 Escaneando IP...')}\n{code(ip)}")

    try:
        data = await lookup_ip(ip)
        if not data.get("success"):
            await message.answer(f"Error: {data.get('error', 'Desconocido')}")
            return

        flag = ""
        if len(data.get("codigo_pais", "")) == 2:
            c = data["codigo_pais"].upper()
            flag = chr(ord(c[0]) + 127397) + chr(ord(c[1]) + 127397)

        lines = [
            f"{bold('🌐 Información de IP')}\n",
            f"{bold('IP')}: {code(data['ip'])}",
            f"{bold('País')}: {flag} {data['pais']} ({data['codigo_pais']})",
            f"{bold('Región')}: {data['region']}",
            f"{bold('Ciudad')}: {data['ciudad']}",
            f"{bold('CP')}: {data['codigo_postal']}",
            f"{bold('Coordenadas')}: {data['lat']}, {data['lon']}",
            f"{bold('Zona horaria')}: {data['zona_horaria']}",
            f"{bold('ISP')}: {data['isp']}",
            f"{bold('Organización')}: {data['org']}",
            f"{bold('ASN')}: {data['asn']}",
        ]
        if data.get("hostname"):
            lines.append(f"{bold('Hostname')}: {data['hostname']}")

        lines.append("")
        lines.append(f"{bold('🗺️ Mapa')}: {data['map_url']}")

        threats = []
        if data.get("vpn"): threats.append("VPN")
        if data.get("proxy"): threats.append("Proxy")
        if data.get("tor"): threats.append("Tor")
        if data.get("hosting"): threats.append("Hosting/Cloud")
        if threats:
            lines.append(f"{bold('🛡️ Detección')}: {' ⚠️ '.join(threats)}")
        else:
            lines.append(f"{bold('🛡️ Detección')}: ✅ IP residencial/limpia")

        if data.get("company_name"):
            lines.append(f"{bold('🏢 Compañía')}: {data['company_name']}")
            if data.get("company_domain"):
                lines.append(f"  Web: {data['company_domain']}")
        if data.get("abuse_email") or data.get("abuse_phone"):
            lines.append(f"{bold('📞 Contacto abuso')}:")
            if data.get("abuse_email"):
                lines.append(f"  Email: {data['abuse_email']}")
            if data.get("abuse_phone"):
                lines.append(f"  Tel: {data['abuse_phone']}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "ip", ip, result_text[:500])
        await message.answer(result_text, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en ip lookup")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("whois"))
async def cmd_whois(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /whois <dominio>\nEj: /whois example.com")
        return

    domain = command.args.strip()
    await message.answer(f"{bold('🔍 Consultando WHOIS...')}\n{code(domain)}")

    try:
        data = await whois_lookup(domain)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('📋 WHOIS')}\n",
            f"{bold('Dominio')}: {data.get('domain', '')}",
            f"{bold('Registrador')}: {data.get('registrador', 'N/A')}",
            f"{bold('Creado')}: {data.get('creado', 'N/A')}",
            f"{bold('Expira')}: {data.get('expira', 'N/A')}",
        ]

        ns = data.get("nameservers", [])
        if ns:
            ns_list = ns if isinstance(ns, list) else [ns]
            lines.append(f"{bold('Nameservers')}:")
            for n in ns_list:
                lines.append(f"  • {n}")

        if data.get("registrante"):
            lines.append(f"{bold('Registrante')}: {data['registrante']}")
        if data.get("organizacion"):
            lines.append(f"{bold('Organización')}: {data['organizacion']}")
        if data.get("pais"):
            lines.append(f"{bold('País')}: {data['pais']}")

        result_text = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "whois", domain, result_text[:500])
        await message.answer(result_text, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en whois")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("exif"))
async def cmd_exif(message: types.Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer("Envía una foto y responde con /exif\nO usa: /exif <url_de_imagen>")
        return

    photo = message.reply_to_message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

    await message.answer(f"{bold('🔍 Extrayendo metadatos...')}")

    try:
        data = await extract_exif_from_url(url)
        if "error" in data:
            await message.answer(f"Sin metadatos EXIF: {data['error']}")
            return

        lines = [f"{bold('📸 Metadatos EXIF')}\n"]
        for key, val in data.items():
            if val:
                lines.append(f"{bold(key)}: {code(str(val)[:300])}")

        result_text = "\n".join(lines)
        pages = paginate(result_text)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en exif")
        await message.answer(f"Error inesperado: {str(e)}")

@router.message(Command("hash"))
async def cmd_hash(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /hash <texto>\nEj: /hash Hola Mundo")
        return

    text = command.args.strip()
    hashes = generate_hashes(text)
    lines = [
        f"{bold('🔐 Hashes')}\n",
        f"Texto: {code(text[:100])}",
        "",
        f"{bold('MD5')}: {code(hashes['md5'])}",
        f"{bold('SHA1')}: {code(hashes['sha1'])}",
        f"{bold('SHA256')}: {code(hashes['sha256'])}",
        f"{bold('SHA512')}: {code(hashes['sha512'])}",
    ]
    await message.answer("\n".join(lines))

@router.message(Command("qr"))
async def cmd_qr(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /qr <texto>\nEj: /qr https://t.me/osincristbot")
        return

    text = command.args.strip()
    try:
        img_bytes = generate_qr(text)
        await message.answer_photo(
            types.BufferedInputFile(img_bytes, filename="qr.png"),
            caption=f"{bold('QR generado')} para: {code(text[:50])}"
        )
    except Exception as e:
        await message.answer(f"Error generando QR: {str(e)}")

@router.message(Command("track"))
async def cmd_track(message: types.Message, command: CommandObject):
    args = (command.args or "").strip().split()
    if not args:
        lines = [
            f"{bold('📡 TRACKER')}\n",
            f"Genera links que registran IP y ubicación\n"
            f"de quien los visita.\n",
            f"{bold('Comandos')}:",
            f"  {code('/track new &lt;nombre&gt;')} — Crear link",
            f"  {code('/track list')} — Ver links",
            f"  {code('/track view &lt;nombre&gt;')} — Ver resultados",
            f"",
            f"Links: https://{TRACKER_DOMAIN}/track.php?c=ID",
        ]
        await message.answer("\n".join(lines), disable_web_page_preview=True)
        return

    sub = args[0].lower()

    if sub == "new" and len(args) >= 2:
        name = args[1]
        import uuid
        link_id = uuid.uuid4().hex[:8]
        save_link_id(name, link_id)
        url = generate_link(link_id)
        qr = generate_qr(url)
        await message.answer_photo(
            types.BufferedInputFile(qr, filename="qr.png"),
            caption=(
                f"{bold('✅ Link creado')}\n\n"
                f"Nombre: {code(name)}\n"
                f"ID: {code(link_id)}\n"
                f"Link: {url}\n\n"
                f"Cada vez que alguien lo visite,\n"
                f"usa {code('/track view ' + name)} para ver los datos."
            ),
            disable_web_page_preview=True,
        )
        return

    if sub == "list":
        links = get_links()
        if not links:
            await message.answer("No hay links creados aún. Usa /track new <nombre>")
            return
        lines = [f"{bold('📡 Links activos')}\n"]
        for name, lid in links.items():
            url = generate_link(lid)
            lines.append(f"  • {name}: {url}")
        await message.answer("\n".join(lines), disable_web_page_preview=True)
        return

    if sub == "view" and len(args) >= 2:
        name = args[1]
        links = get_links()
        lid = links.get(name, name)

        await message.answer(f"{bold('📡 Consultando hits...')}")

        data = await fetch_logs(lid)
        if not data.get("success"):
            await message.answer(f"Sin datos aún. Comparte el link y espera visitas.")
            return

        hits = data.get("hits", [])
        lines = [
            f"{bold(f'📊 Hits: {name}')}",
            f"Total: {data['count']} visita(s)\n",
        ]

        for i, hit in enumerate(reversed(hits[-10:]), 1):
            hit_time = hit.get("time", "N/A")
            lines.append(f"{bold(f'#{i} — {hit_time}')}")
            lines.append(f"  IP: {hit['ip']}")

            ip_data = await lookup_ip(hit["ip"])
            if ip_data.get("success"):
                lines.append(f"  Ubicación: {ip_data.get('ciudad', '')}, {ip_data.get('pais', '')}")
                lines.append(f"  ISP: {ip_data.get('isp', '')}")
                lines.append(f"  Mapa: {ip_data.get('map_url', '')}")

            if hit.get("user_agent"):
                ua = hit["user_agent"][:80]
                lines.append(f"  Navegador: {ua}")
            lines.append("")

        result = "\n".join(lines)
        pages = paginate(result)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)
        return

    await message.answer("Usa: /track new &lt;nombre&gt;, /track list, o /track view &lt;nombre&gt;")

@router.message(Command("ai"))
async def cmd_ai(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "Usa: /ai <pregunta>\n"
            "Ej: /ai qué puedes hacer?\n\n"
            "También puedes analizar resultados:\n"
            "Ej: /ai analiza esta IP: 8.8.8.8"
        )
        return

    prompt = command.args.strip()
    msg = await message.answer(f"{bold('🤖 Pensando...')}")

    try:
        response = await ask_ai(prompt, message.from_user.id)
        cmd = extract_cmd(response)
        if cmd:
            await msg.delete()
            await _execute_agent_command(message, cmd)
        else:
            safe = esc(response)
            pages = paginate(f"{bold('🤖 IA')}\n\n{safe}")
            await msg.delete()
            for page in pages:
                await message.answer(page, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error en AI")
        try:
            await msg.edit_text(f"Error: {str(e)[:200]}")
        except:
            await message.answer(f"Error: {str(e)[:200]}")

@router.message(Command("aireset"))
async def cmd_ai_reset(message: types.Message):
    reset_memory(message.from_user.id)
    await message.answer("🧠 Memoria de IA reiniciada.")

@router.message(lambda msg: msg.text and not msg.text.startswith("/"))
async def agent_text(message: types.Message):
    uid = message.from_user.id
    logger.info(f"Agent text from {uid}: {message.text[:50]}")
    msg = await message.answer(f"{bold('🤖 Procesando...')}")

    try:
        response = await ask_ai(message.text, uid)
        cmd = extract_cmd(response)
        if cmd:
            logger.info(f"Agent executing CMD: {cmd}")
            await msg.delete()
            await _execute_agent_command(message, cmd)
        else:
            safe = esc(response)
            pages = paginate(f"{bold('🤖 IA')}\n\n{safe}")
            await msg.delete()
            for page in pages:
                await message.answer(page, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error en agente")
        try:
            await msg.edit_text(f"Error: {str(e)[:200]}")
        except:
            await message.answer(f"Error: {str(e)[:200]}")

@router.message(lambda msg: msg.photo or msg.document)
async def agent_file(message: types.Message):
    await message.answer(
        "❌ Análisis de imágenes no disponible.\n\n"
        "Describe el archivo con /ai y te ayudo."
    )

async def _execute_agent_command(message: types.Message, cmd_line: str):
    parts = cmd_line.strip().split(maxsplit=1)
    if not parts:
        await message.answer("No se pudo interpretar el comando.")
        return
    cmd_name = parts[0].lower()
    cmd_args = parts[1] if len(parts) > 1 else ""

    from aiogram.filters import CommandObject
    fake_command = CommandObject(command=cmd_name, args=cmd_args, prefix="/", mention=False)
    try:
        if cmd_name in CMD_MAP:
            await CMD_MAP[cmd_name](message, fake_command)
        else:
            await message.answer(f"Comando desconocido: /{cmd_name}")
    except Exception as e:
        await message.answer(f"Error ejecutando /{cmd_name}: {str(e)[:200]}")

@router.message(Command("spam"))
async def cmd_spam(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usa: /spam <número>\nEj: /spam +34612345678")
        return

    number = command.args.strip()
    await message.answer(f"{bold('🔍 Verificando reputación...')}\n{code(number)}")

    try:
        data = await check_spam(number)
        score = data["risk_score"]
        bar = "🟢🟢🟢🟢🟢" if score <= 2 else "🟡🟡🟡🟡🟡" if score <= 6 else "🔴🔴🔴🔴🔴"

        lines = [
            f"{bold('📵 Reputación del número')}\n",
            f"Número: {code(number)}",
            f"Riesgo: {bar} ({score}/10)",
            "",
        ]

        sources = data.get("sources", {})
        for key, src in sources.items():
            name = src.get("source", key)
            if src.get("found"):
                lines.append(f"⚠️ Reportado en {name}")
                lines.append(f"   {src.get('url', '')}")
            elif src.get("error"):
                lines.append(f"❌ {name}: {src['error']}")
            else:
                lines.append(f"✅ {name}: Sin reportes")

        result = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "spam", number, result[:500])
        await message.answer(result, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en spam check")
        await message.answer(f"Error: {str(e)[:200]}")

@router.message(Command("fbi"))
async def cmd_fbi(message: types.Message, command: CommandObject):
    args = (command.args or "").strip()

    if not args or args == "top":
        await message.answer(f"{bold('🔍 Obteniendo Top 10 FBI...')}")
        try:
            items = await list_top_ten()
            if not items:
                await message.answer("No se pudieron obtener datos del FBI.")
                return
            lines = [f"{bold('🚔 Top 10 FBI Most Wanted')}\n"]
            for i, item in enumerate(items, 1):
                lines.append(f"{i}. {item['title']}")
                if item.get("reward"):
                    lines.append(f"   💰 {item['reward']}")
                lines.append("")
            result = "\n".join(lines)
            await save_search(message.from_user.id, message.from_user.full_name, "fbi", "top10", result[:500])
            await message.answer(result, disable_web_page_preview=True)
        except Exception as e:
            await message.answer(f"Error: {str(e)[:200]}")
        return

    await message.answer(f"{bold('🚔 Buscando en FBI...')}\n{code(args)}")
    try:
        data = await search_fbi(args)
        if "error" in data:
            await message.answer(f"Error: {data['error']}")
            return

        lines = [
            f"{bold('🚔 FBI Wanted Results')}\n",
            f"Búsqueda: {code(data['query'])}",
            f"Total resultados: {data['total']}",
            "",
        ]

        if not data["results"]:
            lines.append("Sin resultados para esta búsqueda.")
        else:
            for r in data["results"]:
                lines.append(f"{bold(r['title'])}")
                if r.get("reward"):
                    lines.append(f"  💰 Recompensa: {r['reward']}")
                if r.get("status"):
                    lines.append(f"  📌 Estado: {r['status']}")
                if r.get("sex") or r.get("race"):
                    desc = []
                    if r.get("sex"): desc.append(r['sex'])
                    if r.get("race"): desc.append(r['race'])
                    lines.append(f"  🧑‍🦰 {', '.join(desc)}")
                if r.get("height") or r.get("weight"):
                    hw = f"{r.get('height', '')} / {r.get('weight', '')}"
                    lines.append(f"  📏 {hw.strip(' /')}")
                if r.get("hair"):
                    lines.append(f"  💇 Cabello: {r['hair']}")
                if r.get("place_of_birth"):
                    lines.append(f"  🌍 Nacimiento: {r['place_of_birth']}")
                if r.get("aliases"):
                    lines.append(f"  🎭 Alias: {', '.join(r['aliases'][:3])}")
                if r.get("caution"):
                    lines.append(f"  ⚠️ Precaución: {r['caution'][:150]}")
                if r.get("description"):
                    lines.append(f"  📝 {r['description'][:200]}")
                if r.get("url"):
                    lines.append(f"  🔗 {r['url']}")
                if r.get("images"):
                    lines.append(f"  📸 {r['images'][0]}")
                lines.append("")

        result = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "fbi", args, result[:500])
        pages = paginate(result)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)

    except Exception as e:
        logger.exception("Error en FBI lookup")
        await message.answer(f"Error: {str(e)[:200]}")

@router.message(Command("dox"))
async def cmd_dox(message: types.Message, command: CommandObject):
    if not command.args:
        t = (
            f"🚀 {bold('DOX COMPLETO')}\n\n"
            f"Ejecuta múltiples módulos OSINT simultáneamente "
            f"según el tipo de dato ingresado.\n\n"
            f"{bold('Detecta automáticamente:')}\n"
            f"  📧 Email → email + breaches\n"
            f"  📞 Teléfono → número + spam\n"
            f"  👤 Username → redes + breaches\n"
            f"  🌐 IP → geolocalización + VPN\n"
            f"  👤 Nombre → persona + FBI\n\n"
            f"{code('/dox usuario@ejemplo.com')}\n"
            f"{code('/dox +34612345678')}\n"
            f"{code('/dox midudev')}"
        )
        await message.answer(t)
        return

    args = command.args.strip()
    input_type = detect_input_type(args)
    await message.answer(
        f"🚀 Ejecutando doxing completo...\n"
        f"Objetivo: {code(args)}\n"
        f"Tipo: {input_type.upper()}\n\n"
        f"{code('Esto puede tomar unos segundos...')}"
    )

    try:
        result = await full_dox(args)
        await save_search(message.from_user.id, message.from_user.full_name, "dox", args, result[:500])
        pages = paginate(result)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error en dox")
        await message.answer(f"Error: {str(e)[:200]}")

@router.message(Command("pastes"))
async def cmd_pastes(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer(
            f"📋 {bold('BÚSQUEDA EN PASTES')}\n\n"
            f"Comando:\n"
            f"  {code('/pastes &lt;email o username&gt;')}\n\n"
            f"Busca filtraciones y textos expuestos en\n"
            f"Pastebin y otras plataformas de pastes:\n\n"
            f"✅ psbdmp.ws (base de datos de pastes)\n"
            f"✅ Scylla.so (base de datos de leaks)\n\n"
            f"📌 Ejemplos:\n"
            f"  {code('/pastes usuario@ejemplo.com')}\n"
            f"  {code('/pastes midudev')}"
        )
        return

    query = command.args.strip()
    await message.answer(f"📋 Buscando pastes para {code(query)}...")

    try:
        data = await search_pastes(query)
        lines = [f"📋 {bold('PASTES ENCONTRADOS')}\n"]
        lines.append(f"Búsqueda: {code(data['query'])}")
        lines.append(f"Total: {data['total']}\n")

        if data["psbdmp"]:
            lines.append(f"{bold('📄 PSBDMP (Pastebin Dumps)')}:")
            for p in data["psbdmp"][:10]:
                lines.append(f"  • {p['id']}")
                if p["title"] and p["title"] != "Sin título":
                    lines.append(f"    📌 {p['title']}")
                lines.append(f"    🔗 {p['url']}")
                if p["preview"]:
                    lines.append(f"    📝 {p['preview'][:150]}")
                lines.append("")

        if data["scylla"]:
            lines.append(f"{bold('🔗 Scylla.so')}:")
            for s in data["scylla"][:5]:
                lines.append(f"  🔗 {s['url']}")

        if data["total"] == 0:
            lines.append("No se encontraron pastes para esta consulta.")
            lines.append("\n💡 Prueba con un email en lugar de username o viceversa.")

        result = "\n".join(lines)
        await save_search(message.from_user.id, message.from_user.full_name, "pastes", query, result[:500])
        pages = paginate(result)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error en pastes")
        await message.answer(f"Error: {str(e)[:200]}")

@router.message(Command("genemail"))
async def cmd_genemail(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer(
            f"📧 {bold('GENERADOR DE EMAILS')}\n\n"
            f"Comando:\n"
            f"  {code('/genemail &lt;nombre&gt; [@dominio]')}\n\n"
            f"Genera posibles direcciones de email a partir\n"
            f"de un nombre real usando patrones comunes.\n\n"
            f"Si no especificas dominio, usa gmail.com.\n\n"
            f"📌 Ejemplos:\n"
            f"  {code('/genemail Juan Pérez López')}\n"
            f"  {code('/genemail Juan Pérez @empresa.com')}"
        )
        return

    args = command.args.strip()
    await message.answer(f"📧 Generando emails para {code(args)}...")

    try:
        result = await gen_emails(args)
        await save_search(message.from_user.id, message.from_user.full_name, "genemail", args, result[:500])
        pages = paginate(result)
        for page in pages:
            await message.answer(page, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("Error en genemail")
        await message.answer(f"Error: {str(e)[:200]}")

CMD_MAP = {
    "email": cmd_email,
    "domain": cmd_domain,
    "phone": cmd_phone,
    "user": cmd_user,
    "breach": cmd_breach,
    "geo": cmd_geo,
    "person": cmd_person,
    "web": cmd_web,
    "ip": cmd_ip,
    "whois": cmd_whois,
    "exif": cmd_exif,
    "hash": cmd_hash,
    "qr": cmd_qr,
    "track": cmd_track,
    "ai": cmd_ai,
    "spam": cmd_spam,
    "fbi": cmd_fbi,
    "dox": cmd_dox,
    "pastes": cmd_pastes,
    "genemail": cmd_genemail,
}
