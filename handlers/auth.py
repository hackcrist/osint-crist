from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import (
    register_user, is_user_registered, get_user_info,
    get_all_users, update_user_status, update_user_role, get_stats
)
from utils.formatting import bold, code
from core.logger import logger
from config import OWNER_ID

router = Router()

@router.message(Command("register"))
async def cmd_register(message: types.Message):
    user = message.from_user
    reg = await register_user(
        user.id, user.username or "", user.full_name or ""
    )
    if reg:
        text = (
            f"{bold('✅ Registro exitoso')}\n\n"
            f"Bienvenido {user.full_name}!\n"
            f"Ya puedes usar todos los comandos del bot.\n\n"
            f"Escribe /start para ver el menú."
        )
    else:
        text = (
            f"{bold('⚠️ Ya estás registrado')}\n\n"
            f"Tu cuenta ya está activa. "
            f"Usa /perfil para ver tus datos."
        )
    await message.answer(text)

@router.message(Command("perfil"))
async def cmd_profile(message: types.Message):
    user = await get_user_info(message.from_user.id)
    if not user:
        await message.answer(
            "No estás registrado. Usa /register primero."
        )
        return

    lines = [
        f"{bold('👤 Mi Perfil')}\n",
        f"ID: {code(user['user_id'])}",
        f"Usuario: @{user['username'] or 'N/A'}",
        f"Nombre: {user['full_name'] or 'N/A'}",
        f"Estado: {user['status']}",
        f"Rol: {user['role']}",
        f"Registrado: {user['registered_at'][:19]}",
    ]
    await message.answer("\n".join(lines))

@router.message(Command("usuarios"))
async def cmd_users(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("Solo el owner puede usar este comando.")
        return

    users = await get_all_users()
    if not users:
        await message.answer("No hay usuarios registrados.")
        return

    lines = [f"{bold('📋 Usuarios registrados')}: {len(users)}\n"]
    for u in users:
        flag = "🟢" if u["status"] == "activo" else "🔴"
        lines.append(
            f"{flag} {u['full_name']} (@{u['username']}) — {u['role']}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Actualizar", callback_data="admin_refresh")
    await message.answer(
        "\n".join(lines), reply_markup=builder.as_markup()
    )

@router.message(Command("estadisticas"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("Solo el owner puede usar este comando.")
        return

    s = await get_stats()
    text = (
        f"{bold('📊 Estadísticas')}\n\n"
        f"Usuarios totales: {s['total']}\n"
        f"Usuarios activos: {s['activos']}\n"
        f"Búsquedas totales: {s['busquedas']}"
    )
    await message.answer(text)

@router.message(Command("aprobar"))
async def cmd_approve(message: types.Message, command: CommandObject):
    if message.from_user.id != OWNER_ID:
        await message.answer("Solo el owner puede usar este comando.")
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usa: /aprobar <user_id>\nEj: /aprobar 123456789")
        return

    uid = int(command.args.strip())
    ok = await update_user_status(uid, "activo")
    if ok:
        await message.answer(f"✅ Usuario {uid} activado.")
    else:
        await message.answer(f"❌ Error al activar usuario.")

@router.message(Command("ban"))
async def cmd_ban(message: types.Message, command: CommandObject):
    if message.from_user.id != OWNER_ID:
        await message.answer("Solo el owner puede usar este comando.")
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usa: /ban <user_id>\nEj: /ban 123456789")
        return

    uid = int(command.args.strip())
    ok = await update_user_status(uid, "baneado")
    if ok:
        await message.answer(f"✅ Usuario {uid} baneado.")
    else:
        await message.answer(f"❌ Error al banear usuario.")

@router.callback_query(lambda c: c.data == "admin_refresh")
async def admin_refresh(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("No autorizado")
        return

    users = await get_all_users()
    lines = [f"{bold('📋 Usuarios registrados')}: {len(users)}\n"]
    for u in users:
        flag = "🟢" if u["status"] == "activo" else "🔴"
        lines.append(
            f"{flag} {u['full_name']} (@{u['username']}) — {u['role']}"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Actualizar", callback_data="admin_refresh")

    try:
        await callback.message.edit_text(
            "\n".join(lines), reply_markup=builder.as_markup()
        )
    except:
        pass
    await callback.answer()
