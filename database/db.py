import aiosqlite
from pathlib import Path
from config import DATABASE_PATH

async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    return db

async def init_db():
    Path(DATABASE_PATH).parent.mkdir(exist_ok=True)
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT DEFAULT '',
            command TEXT NOT NULL,
            query TEXT NOT NULL,
            result TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id);
        CREATE INDEX IF NOT EXISTS idx_searches_created ON searches(created_at);

        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            full_name TEXT DEFAULT '',
            status TEXT DEFAULT 'activo',
            role TEXT DEFAULT 'user',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
    """)
    await db.commit()
    await db.close()

async def save_search(user_id: int, username: str, command: str, query: str, result: str = ""):
    db = await get_db()
    await db.execute(
        "INSERT INTO searches (user_id, username, command, query, result) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, command, query, result[:500]),
    )
    await db.commit()
    await db.close()

async def register_user(user_id: int, username: str, full_name: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        exists = await cursor.fetchone()
        if exists:
            await db.execute(
                "UPDATE users SET username = ?, full_name = ?, last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
                (username, full_name, user_id),
            )
            await db.commit()
            await db.close()
            return False
        await db.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        await db.commit()
        await db.close()
        return True
    except:
        await db.close()
        return False

async def is_user_registered(user_id: int) -> bool:
    db = await get_db()
    cursor = await db.execute(
        "SELECT user_id FROM users WHERE user_id = ? AND status = 'activo'",
        (user_id,),
    )
    row = await cursor.fetchone()
    await db.close()
    return row is not None

async def get_user_info(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None

async def get_all_users(status: str = None) -> list:
    db = await get_db()
    if status:
        cursor = await db.execute(
            "SELECT * FROM users WHERE status = ? ORDER BY registered_at DESC", (status,)
        )
    else:
        cursor = await db.execute("SELECT * FROM users ORDER BY registered_at DESC")
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]

async def update_user_status(user_id: int, status: str) -> bool:
    db = await get_db()
    try:
        await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        await db.commit()
        await db.close()
        return True
    except:
        await db.close()
        return False

async def update_user_role(user_id: int, role: str) -> bool:
    db = await get_db()
    try:
        await db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        await db.commit()
        await db.close()
        return True
    except:
        await db.close()
        return False

async def get_stats() -> dict:
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as total FROM users")
    total = (await cursor.fetchone())[0]
    cursor = await db.execute("SELECT COUNT(*) as total FROM users WHERE status = 'activo'")
    activos = (await cursor.fetchone())[0]
    cursor = await db.execute("SELECT COUNT(*) as total FROM searches")
    busquedas = (await cursor.fetchone())[0]
    await db.close()
    return {"total": total, "activos": activos, "busquedas": busquedas}

async def get_history(user_id: int, limit: int = 10):
    db = await get_db()
    cursor = await db.execute(
        "SELECT command, query, created_at FROM searches WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = await cursor.fetchall()
    await db.close()
    return rows
