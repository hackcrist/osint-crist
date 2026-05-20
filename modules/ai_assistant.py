from google import genai
from config import GEMINI_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

async def ask_ai(prompt: str) -> str:
    if not client:
        return "❌ IA no configurada. Revisa tu GEMINI_KEY en .env"

    system = (
        "Eres un asistente OSINT experto en investigación de personas. "
        "Ayudas a analizar información de fuentes públicas. "
        "Sé conciso, preciso y útil. Responde en español."
    )

    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def _sync_call():
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"{system}\n\nUsuario: {prompt}",
            )
            return response.text

        result = await loop.run_in_executor(None, _sync_call)
        return result[:4000] if result else "Sin respuesta"
    except Exception as e:
        return f"Error al consultar IA: {str(e)[:200]}"
