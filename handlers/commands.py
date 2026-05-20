from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import save_search, get_history
from utils.formatting import bold, code, link, paginate
from core.logger import logger

router = Router()

async def _main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📧 Email", callback_data="info_email")
    builder.button(text="📞 Teléfono", callback_data="info_phone")
    builder.button(text="👤 Usuario", callback_data="info_user")
    builder.button(text="👤 Persona", callback_data="info_person")
    builder.button(text="🌐 IP", callback_data="info_ip")
    builder.button(text="🌐 Web", callback_data="info_web")
    builder.button(text="📍 GPS", callback_data="info_geo")
    builder.button(text="🔓 Breach", callback_data="info_breach")
    builder.button(text="📋 WHOIS", callback_data="info_whois")
    builder.button(text="📸 EXIF", callback_data="info_exif")
    builder.button(text="🔐 Hash", callback_data="info_hash")
    builder.button(text="📱 QR", callback_data="info_qr")
    builder.button(text="📡 Tracker", callback_data="info_tracker")
    builder.button(text="🤖 IA", callback_data="info_ai")
    builder.button(text="📵 Spam", callback_data="info_spam")
    builder.button(text="🎯 Domain", callback_data="info_domain")
    builder.button(text="🚔 FBI", callback_data="info_fbi")
    builder.adjust(2)
    return builder.as_markup()

async def _back_button():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Menú principal", callback_data="back_menu")
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        f"🕵️ {bold('OSINT BOT')} — Investigación de Personas\n\n"
        f"Recopila información de fuentes públicas 100% gratuitas.\n\n"
        f"Selecciona un módulo para ver su uso:"
    )
    await message.answer(text, reply_markup=await _main_menu(), disable_web_page_preview=True)

INFO_TEXTS = {
    "email": (
        f"📧 {bold('RECONOCIMIENTO DE EMAIL')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/email &lt;correo&gt;')}\n\n"
        f"Analiza un correo electrónico en busca de\n"
        f"información asociada en fuentes abiertas:\n\n"
        f"✅ Verificación de formato y validez\n"
        f"✅ Consulta de servidores MX (correo entrante)\n"
        f"✅ Búsqueda de perfil en Gravatar\n"
        f"✅ Detección de email desechable/temporal\n"
        f"✅ Consulta en bases de filtraciones públicas\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/email usuario@ejemplo.com')}"
    ),
    "phone": (
        f"📞 {bold('ANÁLISIS DE TELÉFONO')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/phone &lt;+código nº&gt;')}\n\n"
        f"Obtén información detallada de cualquier\n"
        f"número telefónico internacional:\n\n"
        f"✅ País de origen con bandera 🇺🇳\n"
        f"✅ Operador o compañía telefónica\n"
        f"✅ Tipo de línea (móvil, fijo, VoIP, etc.)\n"
        f"✅ Zona horaria del número\n"
        f"✅ Ubicación geográfica estimada\n"
        f"✅ Formato internacional y nacional\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/phone +34612345678')}"
    ),
    "user": (
        f"👤 {bold('RASTREO DE USUARIO')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/user &lt;username&gt;')}\n\n"
        f"Escanea más de 25 plataformas digitales\n"
        f"para determinar dónde está registrado\n"
        f"un nombre de usuario:\n\n"
        f"✅ GitHub • Redes Sociales\n"
        f"✅ Instagram • TikTok • YouTube\n"
        f"✅ Reddit • Twitch • Telegram\n"
        f"✅ Steam • Spotify • Patreon\n"
        f"✅ Y muchas más...\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/user midudev')}"
    ),
    "person": (
        f"👤 {bold('BÚSQUEDA DE PERSONAS')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/person &lt;nombre&gt;')}\n\n"
        f"Recopila información pública disponible\n"
        f"sobre una persona en diferentes fuentes:\n\n"
        f"✅ Wikipedia (biografía y datos clave)\n"
        f"✅ DuckDuckGo (resumen web)\n"
        f"✅ Enlaces directos a redes sociales\n"
        f"✅ Búsquedas rápidas en Google y más\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/person Lionel Messi')}"
    ),
    "web": (
        f"🌐 {bold('RECONOCIMIENTO WEB')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/web &lt;url&gt;')}\n\n"
        f"Escanea y analiza la infraestructura de\n"
        f"cualquier sitio web:\n\n"
        f"✅ Cabeceras HTTP y servidor web\n"
        f"✅ Registros DNS (A, MX, NS, TXT)\n"
        f"✅ Certificado SSL y fechas de validez\n"
        f"✅ Tecnologías detectadas en el servidor\n"
        f"✅ Auditoría de seguridad (headers)\n"
        f"✅ Rutas sensibles (robots, .env, etc.)\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/web https://example.com')}"
    ),
    "geo": (
        f"📍 {bold('GEOLOCALIZACIÓN')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comandos:\n"
        f"  {code('/geo &lt;lat, lng&gt;')}\n"
        f"  {code('/geo &lt;+teléfono&gt;')}\n\n"
        f"Dos formas de obtener ubicación:\n\n"
        f"🔹 Por coordenadas GPS:\n"
        f"   Convierte latitud y longitud en una\n"
        f"   dirección completa con calle, ciudad,\n"
        f"   código postal y enlaces a mapas.\n\n"
        f"🔹 Por número telefónico:\n"
        f"   Obtén el país, operador y ubicación\n"
        f"   geográfica asociada al número.\n\n"
        f"📌 Ejemplos:\n"
        f"  {code('/geo 40.4168, -3.7038')}\n"
        f"  {code('/geo +34612345678')}"
    ),
    "breach": (
        f"🔓 {bold('CONSULTA DE FILTRACIONES')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/breach &lt;email o usuario&gt;')}\n\n"
        f"Verifica si una dirección de correo o\n"
        f"nombre de usuario ha sido comprometido\n"
        f"en filtraciones de seguridad públicas:\n\n"
        f"✅ Leak-Check (bases de datos filtradas)\n"
        f"✅ Firefox Monitor\n"
        f"✅ Pastebin y fuentes públicas\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/breach usuario@ejemplo.com')}"
    ),
    "historial": (
        f"📋 {bold('HISTORIAL DE BÚSQUEDAS')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/historial')}\n\n"
        f"Todas tus consultas se almacenan de forma\n"
        f"segura en la base de datos local.\n\n"
        f"✅ Últimas 10 búsquedas realizadas\n"
        f"✅ Fecha y hora de cada consulta\n"
        f"✅ Comando y parámetros utilizados\n\n"
        f"También disponible:\n"
        f"  {code('/help')} — Ayuda completa del bot"
    ),
    "ip": (
        f"🌐 {bold('INVESTIGACIÓN DE IP')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comandos:\n"
        f"  {code('/ip')} — Tu IP pública\n"
        f"  {code('/ip &lt;dirección&gt;')} — Investigar IP\n\n"
        f"Obtén información detallada de cualquier\n"
        f"dirección IP:\n\n"
        f"✅ País de origen con bandera\n"
        f"✅ Región y ciudad aproximada\n"
        f"✅ Coordenadas geográficas\n"
        f"✅ Proveedor de Internet (ISP)\n"
        f"✅ Organización propietaria\n"
        f"✅ Número de AS\n"
        f"✅ Hostname y DNS reverso\n"
        f"✅ Enlace directo a Google Maps\n"
        f"✅ Detección de VPN/Proxy/Tor\n"
        f"✅ Compañía propietaria\n"
        f"✅ Contacto de abuso\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/ip 8.8.8.8')}"
    ),
    "whois": (
        f"📋 {bold('CONSULTA WHOIS')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/whois &lt;dominio&gt;')}\n\n"
        f"Extrae la información de registro de\n"
        f"cualquier dominio de internet:\n\n"
        f"✅ Fecha de creación del dominio\n"
        f"✅ Fecha de expiración\n"
        f"✅ Registrador utilizado\n"
        f"✅ Servidores de nombres (DNS)\n"
        f"✅ Datos del registrante\n"
        f"✅ País de registro\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/whois google.com')}"
    ),
    "exif": (
        f"📸 {bold('EXTRACCIÓN EXIF')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/exif')} (respondiendo a una foto)\n\n"
        f"Revela los metadatos ocultos dentro de\n"
        f"archivos de imagen:\n\n"
        f"✅ Marca y modelo de cámara\n"
        f"✅ Fecha y hora de la captura\n"
        f"✅ Configuración (ISO, apertura, flash)\n"
        f"✅ Coordenadas GPS (si están presentes)\n"
        f"✅ Software de edición utilizado\n"
        f"✅ Y mucho más...\n\n"
        f"📌 Cómo usar:\n"
        f"  Envía una foto y responde a ella\n"
        f"  con el comando /exif"
    ),
    "hash": (
        f"🔐 {bold('GENERADOR DE HASHES')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/hash &lt;texto&gt;')}\n\n"
        f"Convierte cualquier texto en sus\n"
        f"representaciones hash criptográficas:\n\n"
        f"✅ MD5 — 128 bits\n"
        f"✅ SHA-1 — 160 bits\n"
        f"✅ SHA-256 — 256 bits\n"
        f"✅ SHA-512 — 512 bits\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/hash Hola Mundo')}"
    ),
    "qr": (
        f"📱 {bold('GENERADOR QR')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/qr &lt;texto&gt;')}\n\n"
        f"Crea códigos QR personalizados al\n"
        f"instante con cualquier contenido:\n\n"
        f"✅ Enlaces URL\n"
        f"✅ Texto plano\n"
        f"✅ Números de teléfono\n"
        f"✅ Correos electrónicos\n"
        f"✅ Mensajes de texto\n"
        f"✅ Y cualquier otro dato\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/qr https://t.me/osincristbot')}"
    ),
    "domain": (
        f"🎯 {bold('BÚSQUEDA POR DOMINIO')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/domain &lt;dominio&gt;')}\n\n"
        f"Encuentra correos electrónicos asociados\n"
        f"a un dominio usando Hunter.io:\n\n"
        f"✅ Emails públicos encontrados\n"
        f"✅ Tipo de email (personal, genérico)\n"
        f"✅ Fuentes donde aparece\n"
        f"✅ Patrón de nomenclatura\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/domain ejemplo.com')}"
    ),
    "spam": (
        f"📵 {bold('VERIFICACIÓN SPAM')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/spam &lt;número&gt;')}\n\n"
        f"Consulta si un número telefónico ha sido\n"
        f"reportado como spam en bases públicas:\n\n"
        f"✅ Tellows — Base de spam internacional\n"
        f"✅ SpamCalls — Reportes de usuarios\n"
        f"✅ Escala de riesgo del 0 al 10\n\n"
        f"Útil para detectar llamadas o mensajes\n"
        f"sospechosos antes de contestar.\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/spam +34612345678')}"
    ),
    "ai": (
        f"🤖 {bold('ASISTENTE IA')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comando:\n"
        f"  {code('/ai &lt;pregunta&gt;')}\n\n"
        f"Impulsado por Google Gemini, puedes\n"
        f"consultar cualquier cosa:\n\n"
        f"✅ Análisis de resultados OSINT\n"
        f"✅ Resúmenes de informes\n"
        f"✅ Preguntas genéricas\n"
        f"✅ Traducciones y explicaciones\n"
        f"✅ Asistencia en investigación\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/ai Analiza esta IP: 8.8.8.8')}"
    ),
    "fbi": (
        f"🚔 {bold('FBI MOST WANTED')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comandos:\n"
        f"  {code('/fbi &lt;nombre&gt;')} — Buscar persona\n"
        f"  {code('/fbi top')} — Top 10 más buscados\n\n"
        f"Consulta directamente la base de datos\n"
        f"pública del FBI de personas buscadas:\n\n"
        f"✅ Nombre y descripción física\n"
        f"✅ Recompensa ofrecida\n"
        f"✅ Estado (capturado, prófugo, etc.)\n"
        f"✅ Lugar de nacimiento y alias\n"
        f"✅ Fotos (thumbnails)\n"
        f"✅ Precaución / peligrosidad\n\n"
        f"📌 Ejemplos:\n"
        f"  {code('/fbi Donald')}\n"
        f"  {code('/fbi top')}\n\n"
        f"🔗 Fuente: api.fbi.gov (pública y gratuita)"
    ),
    "tracker": (
        f"📡 {bold('TRACKER DE VISITAS')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Comandos:\n"
        f"  {code('/track new &lt;nombre&gt;')} — Crear link\n"
        f"  {code('/track list')} — Ver links\n"
        f"  {code('/track view &lt;nombre&gt;')} — Resultados\n\n"
        f"Genera enlaces que registran cada visita\n"
        f"de forma discreta:\n\n"
        f"✅ Dirección IP del visitante\n"
        f"✅ País y ubicación geográfica\n"
        f"✅ Proveedor de Internet (ISP)\n"
        f"✅ Navegador y sistema operativo\n"
        f"✅ Fecha y hora exacta\n"
        f"✅ Historial completo de visitas\n\n"
        f"📌 Requisito:\n"
        f"  Tener track.php instalado en tu hosting\n\n"
        f"📌 Ejemplo:\n"
        f"  {code('/track new enlace1')} → genera link\n"
        f"  {code('/track view enlace1')} → muestra datos"
    ),
}

@router.callback_query(lambda c: c.data and c.data.startswith("info_"))
async def info_callback(callback: types.CallbackQuery):
    key = callback.data.replace("info_", "")
    text = INFO_TEXTS.get(key, "Información no disponible")
    await callback.message.answer(text, reply_markup=await _back_button())
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_menu")
async def back_menu_callback(callback: types.CallbackQuery):
    text = (
        f"🕵️ {bold('OSINT BOT')} — Investigación de Personas\n\n"
        f"Recopila información de fuentes públicas 100% gratuitas.\n\n"
        f"Selecciona un módulo para ver su uso:"
    )
    await callback.message.answer(text, reply_markup=await _main_menu())
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        f"{bold('📖 Ayuda Detallada')}\n\n"
        f"{bold('Email')}\n"
        "  /email correo@ejemplo.com\n"
        "  Valida el email, verifica MX, busca Gravatar,\n"
        "  comprueba si es desechable y busca filtraciones.\n\n"
        f"{bold('Teléfono')}\n"
        "  /phone +521234567890\n"
        "  Muestra país, operador, tipo de línea, zona horaria.\n"
        "  Soporta formato internacional.\n\n"
        f"{bold('Usuario')}\n"
        "  /user nombre_usuario\n"
        "  Busca el username en 25+ plataformas sociales\n"
        "  y dice en cuáles existe.\n\n"
        f"{bold('Filtraciones')}\n"
        "  /breach email o username\n"
        "  Busca filtraciones en fuentes públicas.\n\n"
        f"{bold('Historial')}\n"
        "  /historial - Últimas 10 búsquedas\n\n"
        f"{bold('Consejos')}\n"
        "  • Usa prefijo +34 para España, +52 para México, etc.\n"
        "  • Los resultados se guardan automáticamente.\n"
        "  • 100% gratuito y open-source."
    )
    await message.answer(text, disable_web_page_preview=True)

@router.message(Command("historial"))
async def cmd_history(message: types.Message):
    rows = await get_history(message.from_user.id)
    if not rows:
        await message.answer("No tienes búsquedas aún.")
        return

    lines = [f"{bold('📋 Historial de búsquedas')}\n"]
    for i, row in enumerate(rows, 1):
        cmd = row["command"]
        q = row["query"]
        t = row["created_at"][:19]
        lines.append(f"{i}. {code('/' + cmd)} {q} — {t}")

    await message.answer("\n".join(lines), disable_web_page_preview=True)

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    from config import OWNER_ID
    if message.from_user.id != OWNER_ID:
        await message.answer("Solo el owner puede usar este comando.")
        return
    rows = await get_history(message.from_user.id, limit=9999)
    total = len(rows)
    cmds = {}
    for r in rows:
        c = r["command"]
        cmds[c] = cmds.get(c, 0) + 1
    lines = [f"{bold('📊 Estadísticas')}\n", f"Total búsquedas: {total}\n"]
    for cmd, count in sorted(cmds.items(), key=lambda x: -x[1]):
        lines.append(f"  /{cmd}: {count}")
    await message.answer("\n".join(lines))
