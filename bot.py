import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, Message, Update
from aiogram.filters import Command

from config import BOT_TOKEN, OWNER_ID
from core.logger import logger
from database.db import init_db
from handlers.commands import router as commands_router
from handlers.osint_handlers import router as osint_router
from handlers.auth import router as auth_router
from database.db import is_user_registered

async def main():
    logger.info("Iniciando OSINT Bot...")

    await init_db()
    logger.info("Base de datos inicializada")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(auth_router)
    dp.include_router(commands_router)
    dp.include_router(osint_router)

    @dp.message.middleware()
    async def auth_middleware(handler, message: Message, data):
        uid = message.from_user.id
        if uid == OWNER_ID:
            return await handler(message, data)
        cmd = message.text or ""
        if not cmd.startswith("/"):
            return await handler(message, data)
        cmd_name = cmd.split()[0].lstrip("/").split("@")[0].lower()
        public_commands = {"start", "help", "register", "perfil", "usuarios", "estadisticas", "aprobar", "ban"}
        if cmd_name in public_commands:
            return await handler(message, data)
        if not await is_user_registered(uid):
            await message.answer(
                "⚠️ Debes registrarte primero.\n\nUsa /register para acceder al bot."
            )
            return
        return await handler(message, data)

    bot_info = await bot.get_me()
    logger.info(f"Bot conectado: @{bot_info.username} (ID: {bot_info.id})")

    await bot.set_my_commands([
        BotCommand(command="start", description="Inicio y lista de comandos"),
        BotCommand(command="email", description="Investigar un correo electrónico"),
        BotCommand(command="domain", description="Buscar emails por dominio (Hunter)"),
        BotCommand(command="phone", description="Información de un número telefónico"),
        BotCommand(command="user", description="Buscar username en redes sociales"),
        BotCommand(command="person", description="Buscar información de una persona"),
        BotCommand(command="geo", description="Coordenadas GPS a dirección"),
        BotCommand(command="web", description="Escaneo de sitios web"),
        BotCommand(command="ip", description="Información de una IP"),
        BotCommand(command="whois", description="Consulta WHOIS de dominio"),
        BotCommand(command="exif", description="Metadatos de imágenes"),
        BotCommand(command="hash", description="Generar hashes criptográficos"),
        BotCommand(command="qr", description="Generar código QR"),
        BotCommand(command="track", description="Tracker de visitas (IP+ubicación)"),
        BotCommand(command="spam", description="Verificar reputación de número"),
        BotCommand(command="breach", description="Buscar filtraciones de seguridad"),
        BotCommand(command="fbi", description="Buscar en FBI Most Wanted"),
        BotCommand(command="historial", description="Ver últimas búsquedas"),
        BotCommand(command="ai", description="Preguntar a la IA"),
        BotCommand(command="register", description="Registrarse en el bot"),
        BotCommand(command="perfil", description="Ver mi perfil"),
        BotCommand(command="help", description="Ayuda detallada del bot"),
    ], scope=BotCommandScopeDefault())

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.exception(f"Error fatal: {e}")
    finally:
        await bot.session.close()
        logger.info("Sesión cerrada")

if __name__ == "__main__":
    asyncio.run(main())
