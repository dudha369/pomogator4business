from db.models import (
    ArchiveLog,
    ChkGame,
    CityGame,
    ClockEmoji,
    ClockPack,
    Connection,
    DisabledModule,
    EchoChat,
    EmojiStatusSetting,
    G2048Game,
    GuessGame,
    HangmanGame,
    KnownChat,
    MessageHistory,
    MessageLog,
    MirrorBot,
    MsGame,
    Mute,
    ProfileBackup,
    StoryAutopost,
    StoryQueue,
    TttGame,
    UserLocale,
    VoiceEffect,
    WordleGame,
)

# ---------------------------------------------------------------------------
# connections
# ---------------------------------------------------------------------------


async def upsert_connection(
    connection_id,
    owner_id,
    owner_chat_id,
    is_enabled,
    owner_name=None,
    owner_username=None,
    rights_json=None,
):
    await Connection.update_or_create(
        connection_id=connection_id,
        defaults={
            "owner_id": owner_id,
            "owner_chat_id": owner_chat_id,
            "is_enabled": bool(is_enabled),
            "owner_name": owner_name,
            "owner_username": owner_username,
            "rights_json": rights_json,
        },
    )


async def get_connection(connection_id):
    rows = await Connection.filter(connection_id=connection_id).values()
    return rows[0] if rows else None


async def get_connection_by_owner(owner_id):
    rows = (
        await Connection.filter(owner_id=owner_id, is_enabled=True)
        .order_by("-created_at")
        .limit(1)
        .values()
    )
    return rows[0] if rows else None


async def set_prefix(connection_id, prefix):
    await Connection.filter(connection_id=connection_id).update(prefix=prefix)


# ---------------------------------------------------------------------------
# disabled modules
# ---------------------------------------------------------------------------


async def disable_module(connection_id, module):
    await DisabledModule.get_or_create(connection_id=connection_id, module=module)


async def enable_module(connection_id, module):
    await DisabledModule.filter(connection_id=connection_id, module=module).delete()


async def list_disabled_modules(connection_id):
    modules = await DisabledModule.filter(connection_id=connection_id).values_list(
        "module", flat=True
    )
    return set(modules)


# ---------------------------------------------------------------------------
# echo
# ---------------------------------------------------------------------------


async def is_echo_enabled(connection_id, chat_id):
    return await EchoChat.filter(connection_id=connection_id, chat_id=chat_id).exists()


async def toggle_echo(connection_id, chat_id):
    enabled = await is_echo_enabled(connection_id, chat_id)
    if enabled:
        await EchoChat.filter(connection_id=connection_id, chat_id=chat_id).delete()
    else:
        await EchoChat.get_or_create(connection_id=connection_id, chat_id=chat_id)
    return not enabled


# ---------------------------------------------------------------------------
# message log (для "удалить последние N своих сообщений" и т.п.)
# ---------------------------------------------------------------------------


async def log_message(connection_id, chat_id, message_id):
    await MessageLog.create(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    )


async def pop_recent_message_ids(connection_id, chat_id, count):
    rows = (
        await MessageLog.filter(connection_id=connection_id, chat_id=chat_id)
        .order_by("-log_id")
        .limit(count)
        .values("log_id", "message_id")
    )
    log_ids = [row["log_id"] for row in rows]
    message_ids = [row["message_id"] for row in rows]
    if log_ids:
        await MessageLog.filter(log_id__in=log_ids).delete()
    return message_ids


# ---------------------------------------------------------------------------
# mute
# ---------------------------------------------------------------------------


async def get_mute(connection_id, chat_id):
    rows = await Mute.filter(connection_id=connection_id, chat_id=chat_id).values()
    return rows[0] if rows else None


async def clear_mute(connection_id, chat_id):
    await Mute.filter(connection_id=connection_id, chat_id=chat_id).delete()


async def set_timed_mute(connection_id, chat_id, until):
    await Mute.update_or_create(
        connection_id=connection_id,
        chat_id=chat_id,
        defaults={
            "active": True,
            "until": until,
            "warn_limit": None,
            "warn_count": 0,
            "warn_duration": None,
        },
    )


async def set_warn_mute(connection_id, chat_id, warn_limit, warn_duration):
    await Mute.update_or_create(
        connection_id=connection_id,
        chat_id=chat_id,
        defaults={
            "active": False,
            "until": None,
            "warn_limit": warn_limit,
            "warn_count": 0,
            "warn_duration": warn_duration,
        },
    )


async def bump_warn_count(connection_id, chat_id, new_count):
    await Mute.filter(connection_id=connection_id, chat_id=chat_id).update(
        warn_count=new_count
    )


async def activate_from_warn(connection_id, chat_id, until):
    await Mute.filter(connection_id=connection_id, chat_id=chat_id).update(
        active=True, until=until, warn_count=0
    )


# ---------------------------------------------------------------------------
# stories (автопостинг)
# ---------------------------------------------------------------------------


async def is_autopost_enabled(connection_id):
    rows = await StoryAutopost.filter(connection_id=connection_id).values("enabled")
    return bool(rows and rows[0]["enabled"])


async def toggle_autopost(connection_id):
    enabled = await is_autopost_enabled(connection_id)
    if enabled:
        await StoryAutopost.filter(connection_id=connection_id).update(enabled=False)
    else:
        await StoryAutopost.update_or_create(
            connection_id=connection_id, defaults={"enabled": True}
        )
    return not enabled


async def queue_story_tiles(connection_id, tiles):
    await StoryQueue.bulk_create(
        [StoryQueue(connection_id=connection_id, tile_data=tile) for tile in tiles]
    )


async def pop_next_tile(connection_id):
    obj = (
        await StoryQueue.filter(connection_id=connection_id)
        .order_by("queue_id")
        .first()
    )
    if not obj:
        return None
    tile_data = obj.tile_data
    await obj.delete()
    return tile_data


async def get_autopost_enabled_connections():
    return await StoryAutopost.filter(enabled=True).values_list(
        "connection_id", flat=True
    )


async def get_last_post_date(connection_id):
    rows = await StoryAutopost.filter(connection_id=connection_id).values(
        "last_post_date"
    )
    return rows[0]["last_post_date"] if rows else None


async def set_last_post_date(connection_id, date_str):
    await StoryAutopost.filter(connection_id=connection_id).update(
        last_post_date=date_str
    )


# ---------------------------------------------------------------------------
# known chats
# ---------------------------------------------------------------------------


async def is_known_chat(connection_id, chat_id):
    return await KnownChat.filter(connection_id=connection_id, chat_id=chat_id).exists()


async def mark_known_chat(connection_id, chat_id):
    await KnownChat.get_or_create(connection_id=connection_id, chat_id=chat_id)


# ---------------------------------------------------------------------------
# message history (зеркало переписки для форматирования/восстановления)
# ---------------------------------------------------------------------------


async def save_history(connection_id, chat_id, message_id, is_owner, text, created_at):
    obj, created = await MessageHistory.get_or_create(
        connection_id=connection_id,
        chat_id=chat_id,
        message_id=message_id,
        defaults={
            "is_owner": bool(is_owner),
            "text": text,
            "created_at": created_at,
        },
    )
    if not created:
        obj.text = text
        await obj.save(update_fields=["text"])


async def get_history_text(connection_id, chat_id, message_id):
    rows = await MessageHistory.filter(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    ).values("text")
    return rows[0]["text"] if rows else None


async def delete_history(connection_id, chat_id, message_id):
    await MessageHistory.filter(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    ).delete()


async def get_recent_history(connection_id, chat_id, limit):
    rows = (
        await MessageHistory.filter(connection_id=connection_id, chat_id=chat_id)
        .order_by("-created_at")
        .limit(limit)
        .values()
    )
    return list(reversed(rows))


# ---------------------------------------------------------------------------
# archive log
# ---------------------------------------------------------------------------


async def log_archive_event(
    connection_id, chat_id, message_id, event, old_text, new_text, created_at
):
    await ArchiveLog.create(
        connection_id=connection_id,
        chat_id=chat_id,
        message_id=message_id,
        event=event,
        old_text=old_text,
        new_text=new_text,
        created_at=created_at,
    )


async def get_recent_archive(connection_id, limit):
    return (
        await ArchiveLog.filter(connection_id=connection_id)
        .order_by("-log_id")
        .limit(limit)
        .values()
    )


# ---------------------------------------------------------------------------
# profile backups
# ---------------------------------------------------------------------------


async def save_profile_backup(connection_id, bio, photo_data, saved_at):
    await ProfileBackup.update_or_create(
        connection_id=connection_id,
        defaults={"bio": bio, "photo_data": photo_data, "saved_at": saved_at},
    )


async def get_profile_backup(connection_id):
    rows = await ProfileBackup.filter(connection_id=connection_id).values()
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# mirror bots
# ---------------------------------------------------------------------------


async def save_mirror(owner_id, token_encrypted, bot_id, bot_username, created_at):
    await MirrorBot.update_or_create(
        owner_id=owner_id,
        defaults={
            "token_encrypted": token_encrypted,
            "bot_id": bot_id,
            "bot_username": bot_username,
            "created_at": created_at,
            "is_active": True,
        },
    )


async def get_mirror(owner_id):
    rows = await MirrorBot.filter(owner_id=owner_id).values()
    return rows[0] if rows else None


async def get_all_active_mirrors():
    return await MirrorBot.filter(is_active=True).values()


async def delete_mirror(owner_id):
    await MirrorBot.filter(owner_id=owner_id).delete()


# ---------------------------------------------------------------------------
# emoji clock packs
# ---------------------------------------------------------------------------


async def get_clock_pack(pack_index):
    rows = await ClockPack.filter(pack_index=pack_index).values()
    return rows[0] if rows else None


async def upsert_clock_pack(pack_index, pack_name, uploaded_count, completed):
    await ClockPack.update_or_create(
        pack_index=pack_index,
        defaults={
            "pack_name": pack_name,
            "uploaded_count": uploaded_count,
            "completed": bool(completed),
        },
    )


async def save_clock_emoji(time_key, pack_index, custom_emoji_id):
    await ClockEmoji.update_or_create(
        time_key=time_key,
        defaults={"pack_index": pack_index, "custom_emoji_id": custom_emoji_id},
    )


async def get_clock_emoji(time_key):
    rows = await ClockEmoji.filter(time_key=time_key).values("custom_emoji_id")
    return rows[0]["custom_emoji_id"] if rows else None


async def count_clock_emojis():
    return await ClockEmoji.all().count()


# ---------------------------------------------------------------------------
# emoji status
# ---------------------------------------------------------------------------


async def set_emoji_status_granted(owner_id, granted):
    obj, created = await EmojiStatusSetting.get_or_create(
        owner_id=owner_id, defaults={"granted": bool(granted), "enabled": False}
    )
    if not created:
        obj.granted = bool(granted)
        await obj.save(update_fields=["granted"])


async def is_emoji_status_granted(owner_id):
    rows = await EmojiStatusSetting.filter(owner_id=owner_id).values("granted")
    return bool(rows and rows[0]["granted"])


async def set_emoji_status_enabled(owner_id, enabled):
    obj, created = await EmojiStatusSetting.get_or_create(
        owner_id=owner_id, defaults={"granted": False, "enabled": bool(enabled)}
    )
    if not created:
        obj.enabled = bool(enabled)
        await obj.save(update_fields=["enabled"])


async def is_emoji_status_enabled(owner_id):
    rows = await EmojiStatusSetting.filter(owner_id=owner_id).values("enabled")
    return bool(rows and rows[0]["enabled"])


async def get_active_emoji_status_owners():
    return await EmojiStatusSetting.filter(enabled=True, granted=True).values_list(
        "owner_id", flat=True
    )


# ---------------------------------------------------------------------------
# locale
# ---------------------------------------------------------------------------


async def get_locale(owner_id):
    rows = await UserLocale.filter(owner_id=owner_id).values("locale")
    return rows[0]["locale"] if rows else "ru"


async def set_locale(owner_id, locale):
    await UserLocale.update_or_create(owner_id=owner_id, defaults={"locale": locale})


# ---------------------------------------------------------------------------
# voice effects
# ---------------------------------------------------------------------------


async def get_voice_effect(connection_id, chat_id):
    rows = await VoiceEffect.filter(
        connection_id=connection_id, chat_id=chat_id
    ).values("effect")
    return rows[0]["effect"] if rows else None


async def set_voice_effect(connection_id, chat_id, effect):
    if effect is None:
        await VoiceEffect.filter(connection_id=connection_id, chat_id=chat_id).delete()
    else:
        await VoiceEffect.update_or_create(
            connection_id=connection_id, chat_id=chat_id, defaults={"effect": effect}
        )


# ---------------------------------------------------------------------------
# мини-игры — общий помощник + тонкие обёртки на модель
#
# Семантика полностью повторяет прежнюю: сохраняются ТОЛЬКО переданные поля,
# остальные берутся из уже существующей записи, а если записи ещё нет — из
# значений по умолчанию.
# ---------------------------------------------------------------------------


async def _get_game(model, connection_id, chat_id):
    rows = await model.filter(connection_id=connection_id, chat_id=chat_id).values()
    return rows[0] if rows else None


async def _save_game(model, connection_id, chat_id, defaults, fields):
    existing = await _get_game(model, connection_id, chat_id)
    merged = dict(defaults)
    if existing:
        merged.update({k: v for k, v in existing.items() if k in defaults})
    merged.update(fields)
    await model.update_or_create(
        connection_id=connection_id, chat_id=chat_id, defaults=merged
    )


_TTT_DEFAULTS = {
    "board": ".........",
    "turn": "X",
    "player_x_id": None,
    "player_x_name": None,
    "player_o_id": None,
    "player_o_name": None,
    "status": "active",
    "message_id": None,
}


async def save_ttt_game(connection_id, chat_id, **fields):
    await _save_game(TttGame, connection_id, chat_id, _TTT_DEFAULTS, fields)


async def get_ttt_game(connection_id, chat_id):
    return await _get_game(TttGame, connection_id, chat_id)


_WORDLE_DEFAULTS = {
    "secret": "",
    "guesses": "[]",
    "status": "active",
    "message_id": None,
    "starter_id": None,
}


async def save_wordle_game(connection_id, chat_id, **fields):
    await _save_game(WordleGame, connection_id, chat_id, _WORDLE_DEFAULTS, fields)


async def get_wordle_game(connection_id, chat_id):
    return await _get_game(WordleGame, connection_id, chat_id)


_CHK_DEFAULTS = {
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


async def save_chk_game(connection_id, chat_id, **fields):
    await _save_game(ChkGame, connection_id, chat_id, _CHK_DEFAULTS, fields)


async def get_chk_game(connection_id, chat_id):
    return await _get_game(ChkGame, connection_id, chat_id)


_MS_DEFAULTS = {
    "size": 6,
    "bomb_mode": "auto",
    "coop": False,
    "mines": "[]",
    "revealed": "",
    "starter_id": None,
    "starter_name": None,
    "phase": "settings",
    "message_id": None,
}


async def save_ms_game(connection_id, chat_id, **fields):
    fields = dict(fields)
    if "coop" in fields:
        fields["coop"] = bool(fields["coop"])
    await _save_game(MsGame, connection_id, chat_id, _MS_DEFAULTS, fields)


async def get_ms_game(connection_id, chat_id):
    return await _get_game(MsGame, connection_id, chat_id)


_GUESS_DEFAULTS = {"secret": 1, "max_value": 100, "attempts": 0, "status": "active"}


async def save_guess_game(connection_id, chat_id, **fields):
    await _save_game(GuessGame, connection_id, chat_id, _GUESS_DEFAULTS, fields)


async def get_guess_game(connection_id, chat_id):
    return await _get_game(GuessGame, connection_id, chat_id)


_CITY_DEFAULTS = {"used_words": "[]", "next_letter": None, "status": "active"}


async def save_city_game(connection_id, chat_id, **fields):
    await _save_game(CityGame, connection_id, chat_id, _CITY_DEFAULTS, fields)


async def get_city_game(connection_id, chat_id):
    return await _get_game(CityGame, connection_id, chat_id)


_HANGMAN_DEFAULTS = {
    "secret": "",
    "guessed_letters": "[]",
    "mistakes": 0,
    "status": "active",
    "message_id": None,
}


async def save_hangman_game(connection_id, chat_id, **fields):
    await _save_game(HangmanGame, connection_id, chat_id, _HANGMAN_DEFAULTS, fields)


async def get_hangman_game(connection_id, chat_id):
    return await _get_game(HangmanGame, connection_id, chat_id)


_G2048_DEFAULTS = {
    "board": "",
    "score": 0,
    "status": "active",
    "player_id": None,
    "message_id": None,
}


async def save_g2048_game(connection_id, chat_id, **fields):
    await _save_game(G2048Game, connection_id, chat_id, _G2048_DEFAULTS, fields)


async def get_g2048_game(connection_id, chat_id):
    return await _get_game(G2048Game, connection_id, chat_id)
