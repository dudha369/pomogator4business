from dataclasses import dataclass

from aiogram import Bot
from aiogram.types import Message

from core import database as db
from core.i18n import t


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

    async def reply(self, text, **kwargs):
        sent = await self.bot.send_message(
            business_connection_id=self.connection_id,
            chat_id=self.chat_id,
            text=text,
            **kwargs,
        )
        await db.log_message(self.connection_id, self.chat_id, sent.message_id)
        return sent

    async def delete_command_message(self):
        try:
            await self.bot.delete_business_messages(
                business_connection_id=self.connection_id,
                message_ids=[self.message.message_id],
            )
        except Exception:
            pass
