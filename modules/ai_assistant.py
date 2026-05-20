import asyncio
import base64
from groq import Groq
from config import GROQ_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
VISION_MODEL = "llama-3.2-90b-vision-preview"

chat_memory: dict[int, list[dict]] = {}
MAX_HISTORY = 20

SYSTEM_PROMPT = (
    "Eres un asistente técnico especializado en consultar APIs y bases de datos "
    "públicas para obtener información de código abierto. "
    "Tu función es ejecutar comandos del bot cuando el usuario los solicite.\n\n"
    "COMANDOS DISPONIBLES (responde SOLO con CMD: y el comando, nada más):\n"
    "- CMD:email <correo> — Datos públicos de un email\n"
    "- CMD:phone <número> — Datos públicos de un teléfono\n"
    "- CMD:user <username> — Buscar username en redes\n"
    "- CMD:person <nombre> — Resumen público de persona\n"
    "- CMD:ip <dirección> — Geolocalización de IP\n"
    "- CMD:dox <target> — Escaneo múltiple de fuentes abiertas\n"
    "- CMD:breach <email> — Historial de filtraciones\n"
    "- CMD:pastes <email/username> — Buscar en Pastebin\n"
    "- CMD:web <url> — Analizar sitio web\n"
    "- CMD:whois <dominio> — WHOIS de dominio\n"
    "- CMD:spam <número> — Reputación de número\n"
    "- CMD:geo <lat,lon> — Georlocalización\n"
    "- CMD:fbi <nombre> — FBI Most Wanted\n\n"
    "REGLAS:\n"
    "1. Si el usuario QUIERE EJECUTAR un comando, responde SOLO con CMD:<comando> y los argumentos.\n"
    "   Ej: 'busca el email test@email.com' → CMD:email test@email.com\n"
    "2. Si el usuario hace una pregunta normal, responde de forma útil.\n"
    "3. Si preguntan por algo que no involucra los comandos, responde normal.\n"
    "4. Siempre responde en español.\n"
    "5. Sé conciso."
)

async def ask_ai(prompt: str, user_id: int = 0) -> str:
    if not client:
        return "❌ IA no configurada. Revisa tu GROQ_KEY en .env"

    history = chat_memory.get(user_id, [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-MAX_HISTORY:]:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})

    try:
        loop = asyncio.get_event_loop()

        def _sync_call():
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=4000,
                temperature=0.7,
            )
            return response.choices[0].message.content or "Sin respuesta"

        result = await loop.run_in_executor(None, _sync_call)
        result = result[:4000] if result else "Sin respuesta"

        if user_id:
            if user_id not in chat_memory:
                chat_memory[user_id] = []
            chat_memory[user_id].append({"role": "user", "content": prompt})
            chat_memory[user_id].append({"role": "assistant", "content": result})
            if len(chat_memory[user_id]) > MAX_HISTORY * 2:
                chat_memory[user_id] = chat_memory[user_id][-MAX_HISTORY:]

        return result
    except Exception as e:
        return f"Error al consultar IA: {str(e)[:200]}"

async def analyze_file(user_id: int, file_name: str, file_bytes: bytes, caption: str = "") -> str:
    return (
        "❌ Análisis de imágenes no disponible con esta API.\n\n"
        "Para analizar archivos, usa /ai y describe el contenido, "
        "o envíame un texto directamente."
    )

def extract_cmd(text: str) -> str | None:
    if text.startswith("CMD:"):
        return text[4:].strip()
    return None

def reset_memory(user_id: int):
    chat_memory.pop(user_id, None)