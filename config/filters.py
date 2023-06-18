from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from config.config_bot import admin_id


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        """
        admin_id -> list[str] - список id админов из конфига
        """
        if str(message.from_user.id) in admin_id:
            return True
        else:
            return False
