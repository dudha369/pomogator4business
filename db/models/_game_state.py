"""Общая логика сохранения мини-игр — не модель, не импортируется напрямую
из handlers/modules (там используется core.database), только другими
файлами db/models/<игра>.py.

save_*_game(connection_id, chat_id, **fields) сохраняет ТОЛЬКО переданные
поля: сначала берутся значения по умолчанию, затем поверх накладывается
уже существующая запись (если есть), затем — явно переданные значения.
"""


async def get_game(model, connection_id, chat_id):
    rows = await model.filter(connection_id=connection_id, chat_id=chat_id).values()
    return rows[0] if rows else None


async def save_game(model, connection_id, chat_id, defaults, fields):
    existing = await get_game(model, connection_id, chat_id)
    merged = dict(defaults)
    if existing:
        merged.update({k: v for k, v in existing.items() if k in defaults})
    merged.update(fields)
    await model.update_or_create(
        connection_id=connection_id, chat_id=chat_id, defaults=merged
    )
