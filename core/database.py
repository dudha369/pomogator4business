import aiosqlite

from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS connections ("
            "connection_id TEXT PRIMARY KEY,"
            "owner_id INTEGER NOT NULL,"
            "owner_chat_id INTEGER NOT NULL,"
            "owner_name TEXT,"
            "owner_username TEXT,"
            "is_enabled INTEGER NOT NULL DEFAULT 1,"
            "prefix TEXT NOT NULL DEFAULT '.',"
            "rights_json TEXT"
            ")"
        )
        for column_def in (
            "owner_name TEXT",
            "owner_username TEXT",
            "rights_json TEXT",
        ):
            try:
                await conn.execute(f"ALTER TABLE connections ADD COLUMN {column_def}")
            except Exception:
                pass
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS disabled_modules ("
            "connection_id TEXT NOT NULL,"
            "module TEXT NOT NULL,"
            "PRIMARY KEY (connection_id, module)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS echo_chats ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS message_log ("
            "log_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "message_id INTEGER NOT NULL"
            ")"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_message_log "
            "ON message_log (connection_id, chat_id, log_id DESC)"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS mutes ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "active INTEGER NOT NULL DEFAULT 0,"
            "until INTEGER,"
            "warn_limit INTEGER,"
            "warn_count INTEGER NOT NULL DEFAULT 0,"
            "warn_duration INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS story_autopost ("
            "connection_id TEXT PRIMARY KEY,"
            "enabled INTEGER NOT NULL DEFAULT 1,"
            "last_post_date TEXT"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS story_queue ("
            "queue_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "connection_id TEXT NOT NULL,"
            "tile_data BLOB NOT NULL"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS known_chats ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS message_history ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "message_id INTEGER NOT NULL,"
            "is_owner INTEGER NOT NULL,"
            "text TEXT,"
            "created_at INTEGER NOT NULL,"
            "PRIMARY KEY (connection_id, chat_id, message_id)"
            ")"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_message_history "
            "ON message_history (connection_id, chat_id, created_at)"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS archive_log ("
            "log_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "message_id INTEGER NOT NULL,"
            "event TEXT NOT NULL,"
            "old_text TEXT,"
            "new_text TEXT,"
            "created_at INTEGER NOT NULL"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS profile_backups ("
            "connection_id TEXT PRIMARY KEY,"
            "bio TEXT,"
            "photo_data BLOB,"
            "saved_at INTEGER NOT NULL"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS mirror_bots ("
            "owner_id INTEGER PRIMARY KEY,"
            "token_encrypted BLOB NOT NULL,"
            "bot_id INTEGER,"
            "bot_username TEXT,"
            "created_at INTEGER NOT NULL,"
            "is_active INTEGER NOT NULL DEFAULT 1"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS clock_packs ("
            "pack_index INTEGER PRIMARY KEY,"
            "pack_name TEXT NOT NULL,"
            "uploaded_count INTEGER NOT NULL DEFAULT 0,"
            "completed INTEGER NOT NULL DEFAULT 0"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS clock_emojis ("
            "time_key TEXT PRIMARY KEY,"
            "pack_index INTEGER NOT NULL,"
            "custom_emoji_id TEXT"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS emoji_status_settings ("
            "owner_id INTEGER PRIMARY KEY,"
            "granted INTEGER NOT NULL DEFAULT 0,"
            "enabled INTEGER NOT NULL DEFAULT 0"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS user_locale ("
            "owner_id INTEGER PRIMARY KEY,"
            "locale TEXT NOT NULL DEFAULT 'ru'"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS voice_effects ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "effect TEXT NOT NULL,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS ttt_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "board TEXT NOT NULL,"
            "turn TEXT NOT NULL,"
            "player_x_id INTEGER NOT NULL,"
            "player_x_name TEXT,"
            "player_o_id INTEGER,"
            "player_o_name TEXT,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "message_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS wordle_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "secret TEXT NOT NULL,"
            "guesses TEXT NOT NULL DEFAULT '[]',"
            "status TEXT NOT NULL DEFAULT 'active',"
            "message_id INTEGER,"
            "starter_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS chk_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "board TEXT NOT NULL,"
            "turn TEXT NOT NULL,"
            "player_w_id INTEGER,"
            "player_w_name TEXT,"
            "player_b_id INTEGER,"
            "player_b_name TEXT,"
            "selected INTEGER,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "message_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS ms_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "size INTEGER NOT NULL DEFAULT 6,"
            "bomb_mode TEXT NOT NULL DEFAULT 'auto',"
            "coop INTEGER NOT NULL DEFAULT 0,"
            "mines TEXT NOT NULL DEFAULT '[]',"
            "revealed TEXT NOT NULL DEFAULT '',"
            "starter_id INTEGER,"
            "starter_name TEXT,"
            "phase TEXT NOT NULL DEFAULT 'settings',"
            "message_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS guess_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "secret INTEGER NOT NULL,"
            "max_value INTEGER NOT NULL,"
            "attempts INTEGER NOT NULL DEFAULT 0,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS city_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "used_words TEXT NOT NULL DEFAULT '[]',"
            "next_letter TEXT,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS hangman_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "secret TEXT NOT NULL,"
            "guessed_letters TEXT NOT NULL DEFAULT '[]',"
            "mistakes INTEGER NOT NULL DEFAULT 0,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "message_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS g2048_games ("
            "connection_id TEXT NOT NULL,"
            "chat_id INTEGER NOT NULL,"
            "board TEXT NOT NULL,"
            "score INTEGER NOT NULL DEFAULT 0,"
            "status TEXT NOT NULL DEFAULT 'active',"
            "player_id INTEGER,"
            "message_id INTEGER,"
            "PRIMARY KEY (connection_id, chat_id)"
            ")"
        )
        await conn.commit()


async def upsert_connection(
    connection_id,
    owner_id,
    owner_chat_id,
    is_enabled,
    owner_name=None,
    owner_username=None,
    rights_json=None,
):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO connections "
            "(connection_id, owner_id, owner_chat_id, is_enabled, owner_name, owner_username, rights_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id) DO UPDATE SET "
            "owner_id=excluded.owner_id, "
            "owner_chat_id=excluded.owner_chat_id, "
            "is_enabled=excluded.is_enabled, "
            "owner_name=excluded.owner_name, "
            "owner_username=excluded.owner_username, "
            "rights_json=excluded.rights_json",
            (
                connection_id,
                owner_id,
                owner_chat_id,
                int(is_enabled),
                owner_name,
                owner_username,
                rights_json,
            ),
        )
        await conn.commit()


async def get_connection(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM connections WHERE connection_id = ?", (connection_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_connection_by_owner(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM connections WHERE owner_id = ? AND is_enabled = 1 "
            "ORDER BY rowid DESC LIMIT 1",
            (owner_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def set_prefix(connection_id, prefix):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE connections SET prefix = ? WHERE connection_id = ?",
            (prefix, connection_id),
        )
        await conn.commit()


async def disable_module(connection_id, module):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO disabled_modules (connection_id, module) VALUES (?, ?)",
            (connection_id, module),
        )
        await conn.commit()


async def enable_module(connection_id, module):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "DELETE FROM disabled_modules WHERE connection_id = ? AND module = ?",
            (connection_id, module),
        )
        await conn.commit()


async def list_disabled_modules(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT module FROM disabled_modules WHERE connection_id = ?",
            (connection_id,),
        )
        rows = await cursor.fetchall()
        return {row[0] for row in rows}


async def is_echo_enabled(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM echo_chats WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return row is not None


async def toggle_echo(connection_id, chat_id):
    enabled = await is_echo_enabled(connection_id, chat_id)
    async with aiosqlite.connect(DB_PATH) as conn:
        if enabled:
            await conn.execute(
                "DELETE FROM echo_chats WHERE connection_id = ? AND chat_id = ?",
                (connection_id, chat_id),
            )
        else:
            await conn.execute(
                "INSERT OR IGNORE INTO echo_chats (connection_id, chat_id) VALUES (?, ?)",
                (connection_id, chat_id),
            )
        await conn.commit()
    return not enabled


async def log_message(connection_id, chat_id, message_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO message_log (connection_id, chat_id, message_id) VALUES (?, ?, ?)",
            (connection_id, chat_id, message_id),
        )
        await conn.commit()


async def pop_recent_message_ids(connection_id, chat_id, count):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT log_id, message_id FROM message_log "
            "WHERE connection_id = ? AND chat_id = ? "
            "ORDER BY log_id DESC LIMIT ?",
            (connection_id, chat_id, count),
        )
        rows = await cursor.fetchall()
        log_ids = [row[0] for row in rows]
        message_ids = [row[1] for row in rows]
        if log_ids:
            placeholders = ",".join("?" * len(log_ids))
            await conn.execute(
                f"DELETE FROM message_log WHERE log_id IN ({placeholders})", log_ids
            )
            await conn.commit()
        return message_ids


async def get_mute(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM mutes WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def clear_mute(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "DELETE FROM mutes WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        await conn.commit()


async def set_timed_mute(connection_id, chat_id, until):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO mutes (connection_id, chat_id, active, until, warn_limit, warn_count, warn_duration) "
            "VALUES (?, ?, 1, ?, NULL, 0, NULL) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "active=1, until=excluded.until, warn_limit=NULL, warn_count=0, warn_duration=NULL",
            (connection_id, chat_id, until),
        )
        await conn.commit()


async def set_warn_mute(connection_id, chat_id, warn_limit, warn_duration):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO mutes (connection_id, chat_id, active, until, warn_limit, warn_count, warn_duration) "
            "VALUES (?, ?, 0, NULL, ?, 0, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "active=0, until=NULL, warn_limit=excluded.warn_limit, warn_count=0, warn_duration=excluded.warn_duration",
            (connection_id, chat_id, warn_limit, warn_duration),
        )
        await conn.commit()


async def bump_warn_count(connection_id, chat_id, new_count):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE mutes SET warn_count = ? WHERE connection_id = ? AND chat_id = ?",
            (new_count, connection_id, chat_id),
        )
        await conn.commit()


async def activate_from_warn(connection_id, chat_id, until):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE mutes SET active = 1, until = ?, warn_count = 0 "
            "WHERE connection_id = ? AND chat_id = ?",
            (until, connection_id, chat_id),
        )
        await conn.commit()


async def is_autopost_enabled(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT enabled FROM story_autopost WHERE connection_id = ?",
            (connection_id,),
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def toggle_autopost(connection_id):
    enabled = await is_autopost_enabled(connection_id)
    async with aiosqlite.connect(DB_PATH) as conn:
        if enabled:
            await conn.execute(
                "UPDATE story_autopost SET enabled = 0 WHERE connection_id = ?",
                (connection_id,),
            )
        else:
            await conn.execute(
                "INSERT INTO story_autopost (connection_id, enabled, last_post_date) "
                "VALUES (?, 1, NULL) "
                "ON CONFLICT(connection_id) DO UPDATE SET enabled = 1",
                (connection_id,),
            )
        await conn.commit()
    return not enabled


async def queue_story_tiles(connection_id, tiles):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.executemany(
            "INSERT INTO story_queue (connection_id, tile_data) VALUES (?, ?)",
            [(connection_id, tile) for tile in tiles],
        )
        await conn.commit()


async def pop_next_tile(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT queue_id, tile_data FROM story_queue "
            "WHERE connection_id = ? ORDER BY queue_id ASC LIMIT 1",
            (connection_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        await conn.execute("DELETE FROM story_queue WHERE queue_id = ?", (row[0],))
        await conn.commit()
        return row[1]


async def get_autopost_enabled_connections():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT connection_id FROM story_autopost WHERE enabled = 1"
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_last_post_date(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT last_post_date FROM story_autopost WHERE connection_id = ?",
            (connection_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_last_post_date(connection_id, date_str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE story_autopost SET last_post_date = ? WHERE connection_id = ?",
            (date_str, connection_id),
        )
        await conn.commit()


async def is_known_chat(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM known_chats WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return row is not None


async def mark_known_chat(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO known_chats (connection_id, chat_id) VALUES (?, ?)",
            (connection_id, chat_id),
        )
        await conn.commit()


async def save_history(connection_id, chat_id, message_id, is_owner, text, created_at):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO message_history "
            "(connection_id, chat_id, message_id, is_owner, text, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id, message_id) DO UPDATE SET "
            "text=excluded.text",
            (connection_id, chat_id, message_id, int(is_owner), text, created_at),
        )
        await conn.commit()


async def get_history_text(connection_id, chat_id, message_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT text FROM message_history "
            "WHERE connection_id = ? AND chat_id = ? AND message_id = ?",
            (connection_id, chat_id, message_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def delete_history(connection_id, chat_id, message_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "DELETE FROM message_history "
            "WHERE connection_id = ? AND chat_id = ? AND message_id = ?",
            (connection_id, chat_id, message_id),
        )
        await conn.commit()


async def get_recent_history(connection_id, chat_id, limit):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM message_history "
            "WHERE connection_id = ? AND chat_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (connection_id, chat_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]


async def log_archive_event(
    connection_id, chat_id, message_id, event, old_text, new_text, created_at
):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO archive_log "
            "(connection_id, chat_id, message_id, event, old_text, new_text, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (connection_id, chat_id, message_id, event, old_text, new_text, created_at),
        )
        await conn.commit()


async def get_recent_archive(connection_id, limit):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM archive_log WHERE connection_id = ? "
            "ORDER BY log_id DESC LIMIT ?",
            (connection_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def save_profile_backup(connection_id, bio, photo_data, saved_at):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO profile_backups (connection_id, bio, photo_data, saved_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(connection_id) DO UPDATE SET "
            "bio=excluded.bio, photo_data=excluded.photo_data, saved_at=excluded.saved_at",
            (connection_id, bio, photo_data, saved_at),
        )
        await conn.commit()


async def get_profile_backup(connection_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM profile_backups WHERE connection_id = ?",
            (connection_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_mirror(owner_id, token_encrypted, bot_id, bot_username, created_at):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO mirror_bots (owner_id, token_encrypted, bot_id, bot_username, created_at, is_active) "
            "VALUES (?, ?, ?, ?, ?, 1) "
            "ON CONFLICT(owner_id) DO UPDATE SET "
            "token_encrypted=excluded.token_encrypted, bot_id=excluded.bot_id, "
            "bot_username=excluded.bot_username, created_at=excluded.created_at, is_active=1",
            (owner_id, token_encrypted, bot_id, bot_username, created_at),
        )
        await conn.commit()


async def get_mirror(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM mirror_bots WHERE owner_id = ?", (owner_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_active_mirrors():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM mirror_bots WHERE is_active = 1")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_mirror(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM mirror_bots WHERE owner_id = ?", (owner_id,))
        await conn.commit()


async def get_clock_pack(pack_index):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM clock_packs WHERE pack_index = ?", (pack_index,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def upsert_clock_pack(pack_index, pack_name, uploaded_count, completed):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO clock_packs (pack_index, pack_name, uploaded_count, completed) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(pack_index) DO UPDATE SET "
            "pack_name=excluded.pack_name, uploaded_count=excluded.uploaded_count, "
            "completed=excluded.completed",
            (pack_index, pack_name, uploaded_count, int(completed)),
        )
        await conn.commit()


async def save_clock_emoji(time_key, pack_index, custom_emoji_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO clock_emojis (time_key, pack_index, custom_emoji_id) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(time_key) DO UPDATE SET "
            "pack_index=excluded.pack_index, custom_emoji_id=excluded.custom_emoji_id",
            (time_key, pack_index, custom_emoji_id),
        )
        await conn.commit()


async def get_clock_emoji(time_key):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT custom_emoji_id FROM clock_emojis WHERE time_key = ?", (time_key,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def count_clock_emojis():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM clock_emojis")
        row = await cursor.fetchone()
        return row[0]


async def set_emoji_status_granted(owner_id, granted):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO emoji_status_settings (owner_id, granted, enabled) "
            "VALUES (?, ?, 0) "
            "ON CONFLICT(owner_id) DO UPDATE SET granted=excluded.granted",
            (owner_id, int(granted)),
        )
        await conn.commit()


async def is_emoji_status_granted(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT granted FROM emoji_status_settings WHERE owner_id = ?", (owner_id,)
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def set_emoji_status_enabled(owner_id, enabled):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO emoji_status_settings (owner_id, granted, enabled) "
            "VALUES (?, 0, ?) "
            "ON CONFLICT(owner_id) DO UPDATE SET enabled=excluded.enabled",
            (owner_id, int(enabled)),
        )
        await conn.commit()


async def is_emoji_status_enabled(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT enabled FROM emoji_status_settings WHERE owner_id = ?", (owner_id,)
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def get_active_emoji_status_owners():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT owner_id FROM emoji_status_settings WHERE enabled = 1 AND granted = 1"
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_locale(owner_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT locale FROM user_locale WHERE owner_id = ?", (owner_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else "ru"


async def set_locale(owner_id, locale):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO user_locale (owner_id, locale) VALUES (?, ?) "
            "ON CONFLICT(owner_id) DO UPDATE SET locale=excluded.locale",
            (owner_id, locale),
        )
        await conn.commit()


async def get_voice_effect(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT effect FROM voice_effects WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_voice_effect(connection_id, chat_id, effect):
    async with aiosqlite.connect(DB_PATH) as conn:
        if effect is None:
            await conn.execute(
                "DELETE FROM voice_effects WHERE connection_id = ? AND chat_id = ?",
                (connection_id, chat_id),
            )
        else:
            await conn.execute(
                "INSERT INTO voice_effects (connection_id, chat_id, effect) VALUES (?, ?, ?) "
                "ON CONFLICT(connection_id, chat_id) DO UPDATE SET effect=excluded.effect",
                (connection_id, chat_id, effect),
            )
        await conn.commit()


async def save_ttt_game(connection_id, chat_id, **fields):
    existing = await get_ttt_game(connection_id, chat_id)
    merged = {
        "board": ".........",
        "turn": "X",
        "player_x_id": None,
        "player_x_name": None,
        "player_o_id": None,
        "player_o_name": None,
        "status": "active",
        "message_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO ttt_games "
            "(connection_id, chat_id, board, turn, player_x_id, player_x_name, "
            "player_o_id, player_o_name, status, message_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "board=excluded.board, turn=excluded.turn, "
            "player_x_id=excluded.player_x_id, player_x_name=excluded.player_x_name, "
            "player_o_id=excluded.player_o_id, player_o_name=excluded.player_o_name, "
            "status=excluded.status, message_id=excluded.message_id",
            (
                connection_id,
                chat_id,
                merged["board"],
                merged["turn"],
                merged["player_x_id"],
                merged["player_x_name"],
                merged["player_o_id"],
                merged["player_o_name"],
                merged["status"],
                merged["message_id"],
            ),
        )
        await conn.commit()


async def get_ttt_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM ttt_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_wordle_game(connection_id, chat_id, **fields):
    existing = await get_wordle_game(connection_id, chat_id)
    merged = {
        "secret": "",
        "guesses": "[]",
        "status": "active",
        "message_id": None,
        "starter_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO wordle_games "
            "(connection_id, chat_id, secret, guesses, status, message_id, starter_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "secret=excluded.secret, guesses=excluded.guesses, status=excluded.status, "
            "message_id=excluded.message_id, starter_id=excluded.starter_id",
            (
                connection_id,
                chat_id,
                merged["secret"],
                merged["guesses"],
                merged["status"],
                merged["message_id"],
                merged["starter_id"],
            ),
        )
        await conn.commit()


async def get_wordle_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM wordle_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_chk_game(connection_id, chat_id, **fields):
    existing = await get_chk_game(connection_id, chat_id)
    merged = {
        "board": "",
        "turn": "w",
        "player_w_id": None,
        "player_w_name": None,
        "player_b_id": None,
        "player_b_name": None,
        "selected": None,
        "status": "active",
        "message_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO chk_games "
            "(connection_id, chat_id, board, turn, player_w_id, player_w_name, "
            "player_b_id, player_b_name, selected, status, message_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "board=excluded.board, turn=excluded.turn, "
            "player_w_id=excluded.player_w_id, player_w_name=excluded.player_w_name, "
            "player_b_id=excluded.player_b_id, player_b_name=excluded.player_b_name, "
            "selected=excluded.selected, status=excluded.status, message_id=excluded.message_id",
            (
                connection_id,
                chat_id,
                merged["board"],
                merged["turn"],
                merged["player_w_id"],
                merged["player_w_name"],
                merged["player_b_id"],
                merged["player_b_name"],
                merged["selected"],
                merged["status"],
                merged["message_id"],
            ),
        )
        await conn.commit()


async def get_chk_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM chk_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_ms_game(connection_id, chat_id, **fields):
    existing = await get_ms_game(connection_id, chat_id)
    merged = {
        "size": 6,
        "bomb_mode": "auto",
        "coop": 0,
        "mines": "[]",
        "revealed": "",
        "starter_id": None,
        "starter_name": None,
        "phase": "settings",
        "message_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO ms_games "
            "(connection_id, chat_id, size, bomb_mode, coop, mines, revealed, "
            "starter_id, starter_name, phase, message_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "size=excluded.size, bomb_mode=excluded.bomb_mode, coop=excluded.coop, "
            "mines=excluded.mines, revealed=excluded.revealed, "
            "starter_id=excluded.starter_id, starter_name=excluded.starter_name, "
            "phase=excluded.phase, message_id=excluded.message_id",
            (
                connection_id,
                chat_id,
                merged["size"],
                merged["bomb_mode"],
                int(merged["coop"]),
                merged["mines"],
                merged["revealed"],
                merged["starter_id"],
                merged["starter_name"],
                merged["phase"],
                merged["message_id"],
            ),
        )
        await conn.commit()


async def get_ms_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM ms_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_guess_game(connection_id, chat_id, **fields):
    existing = await get_guess_game(connection_id, chat_id)
    merged = {"secret": 1, "max_value": 100, "attempts": 0, "status": "active"}
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO guess_games (connection_id, chat_id, secret, max_value, attempts, status) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "secret=excluded.secret, max_value=excluded.max_value, "
            "attempts=excluded.attempts, status=excluded.status",
            (
                connection_id,
                chat_id,
                merged["secret"],
                merged["max_value"],
                merged["attempts"],
                merged["status"],
            ),
        )
        await conn.commit()


async def get_guess_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM guess_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_city_game(connection_id, chat_id, **fields):
    existing = await get_city_game(connection_id, chat_id)
    merged = {"used_words": "[]", "next_letter": None, "status": "active"}
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO city_games (connection_id, chat_id, used_words, next_letter, status) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "used_words=excluded.used_words, next_letter=excluded.next_letter, status=excluded.status",
            (
                connection_id,
                chat_id,
                merged["used_words"],
                merged["next_letter"],
                merged["status"],
            ),
        )
        await conn.commit()


async def get_city_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM city_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_hangman_game(connection_id, chat_id, **fields):
    existing = await get_hangman_game(connection_id, chat_id)
    merged = {
        "secret": "",
        "guessed_letters": "[]",
        "mistakes": 0,
        "status": "active",
        "message_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO hangman_games "
            "(connection_id, chat_id, secret, guessed_letters, mistakes, status, message_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "secret=excluded.secret, guessed_letters=excluded.guessed_letters, "
            "mistakes=excluded.mistakes, status=excluded.status, message_id=excluded.message_id",
            (
                connection_id,
                chat_id,
                merged["secret"],
                merged["guessed_letters"],
                merged["mistakes"],
                merged["status"],
                merged["message_id"],
            ),
        )
        await conn.commit()


async def get_hangman_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM hangman_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def save_g2048_game(connection_id, chat_id, **fields):
    existing = await get_g2048_game(connection_id, chat_id)
    merged = {
        "board": "",
        "score": 0,
        "status": "active",
        "player_id": None,
        "message_id": None,
    }
    if existing:
        merged.update(existing)
    merged.update(fields)

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO g2048_games "
            "(connection_id, chat_id, board, score, status, player_id, message_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(connection_id, chat_id) DO UPDATE SET "
            "board=excluded.board, score=excluded.score, status=excluded.status, "
            "player_id=excluded.player_id, message_id=excluded.message_id",
            (
                connection_id,
                chat_id,
                merged["board"],
                merged["score"],
                merged["status"],
                merged["player_id"],
                merged["message_id"],
            ),
        )
        await conn.commit()


async def get_g2048_game(connection_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM g2048_games WHERE connection_id = ? AND chat_id = ?",
            (connection_id, chat_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
