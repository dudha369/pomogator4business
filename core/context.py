from dataclasses import dataclass

from aiogram import Bot
from aiogram.types import Message

from core import database as db
from core.i18n import t
from core.self_actions import delete_own_messages


@dataclass
class CommandContext:
    bot: Bot
    message: Message
    connection: dict
    args: str
    locale: str = "ru"

    @property
    def connection_id(self):
        return self.connection["connection_id"]

    @property
    def chat_id(self):
        return self.message.chat.id

    def t(self, key, **kwargs):
        return t(key, self.locale, **kwargs)

    async def reply(self, text: str, **kwargs):
        msg = await self.bot.send_message(
            business_connection_id=self.connection_id,
            chat_id=self.chat_id,
            text=text,
            **kwargs,
        )
        await db.log_message(self.connection_id, self.chat_id, msg.message_id)
        return msg

    async def delete_command_message(self):
        await delete_own_messages(
            self.bot, self.connection_id, self.chat_id, [self.message.message_id]
        )

    async def edit_command_message(self, text: str, **kwargs):
        try:
            await self.bot.edit_message_text(
                business_connection_id=self.connection_id,
                chat_id=self.chat_id,
                message_id=self.message.message_id,
                text=text,
                **kwargs,
            )
        except Exception:
            pass

    async def usage_error(self, text: str, **kwargs):
        await self.delete_command_message()
        try:
            await self.bot.send_message(
                chat_id=self.connection["owner_chat_id"],
                text=text,
                **kwargs,
            )
        except Exception:
            pass
