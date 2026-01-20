from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from aiogram import Bot


games_state = {}
last_wishes = {}
team_chat_sessions = {} 
game_tasks = {}  # {uuid: asyncio.Task}
notify_users = {}
group_users = {}
stones_taken = {}
gsend_taken = {}
giveaways = {}


async def set_bot_commands(bot: Bot):
    group_commands = [
        BotCommand(command="profile", description="Guruh ma'lumotlarini ko'rish"),
        BotCommand(command="game", description="Yangi oyinni boshlash"),
        BotCommand(command="extend", description="O'yin vaqtini uzaytirish"),
        BotCommand(command="start", description="Registratsiyani tugatish va o'yinni boshlash"),
        BotCommand(command="stop", description="Registratsiyani to'xtatish"),
        BotCommand(command="next", description="Keyingi o'yin haqida eslatish"),
        BotCommand(command="top", description="Rating jadvalini ko'rish"),
        BotCommand(command="share", description="Do'stlarni chaqirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    
    # admin_commands = [
    #     BotCommand(command="settings", description="Bot sozlamalari"),
    #     BotCommand(command="cancel", description="O'yinni bekor qilish"),
    # ]
    private_commands = [
        BotCommand(command="profile", description="Profil ma'lumotlarini ko'rish"),
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="leave", description="oyindan chiqish"),
        BotCommand(command="language", description="Tilni o'zgartirish"),
        BotCommand(command="help", description="Yordam"),
    ]
     # Guruhlar uchun o‘rnatish
    await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

    # Private chatlar uchun o‘rnatish
    await bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
    
    # await bot.set_my_commands(admin_commands, scope=BotCommandScopeChatAdministrators())