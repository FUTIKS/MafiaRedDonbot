from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from asgiref.sync import  sync_to_async,async_to_sync

from decouple import config
from mafia_bot.models import MostActiveUser, User
from aiogram import Bot
TOKEN = config("BOT_TOKEN")
@shared_task
def my_daily_task():
    async_to_sync(send_top)()


def get_top():
    now = timezone.now()
    since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    top = (
        MostActiveUser.objects
        .filter(created_datetime__gte=since)
        .values("user")
        .annotate(wins=Sum("games_win"))
        .order_by("-wins")[:30]
    )

    user_ids = [x["user"] for x in top]
    users = User.objects.filter(id__in=user_ids)
    users_map = {u.id: u for u in users}

    return list(top), users_map


async def send_top():
    top, users_map = await sync_to_async(get_top, thread_sensitive=True)()

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for idx, row in enumerate(top, start=1):
        user = users_map.get(row["user"])
        if not user:
            continue

        mention = user.first_name or "User"
        win = row["wins"] or 0

        if idx <= 3:
            lines.append(f"{medals[idx-1]} {mention} — {win * 5} ball")
        else:
            lines.append(f"{idx}. {mention} — {win * 5} ball")

    if not lines:
        text = "<tg-emoji emoji-id='5409008750893734809'>🏆</tg-emoji> Bu oy hali natijalar yo‘q"
    else:
        text = "<tg-emoji emoji-id='5409008750893734809'>🏆</tg-emoji> Oyning top 30 óyinchilari\n\n" + "\n".join(lines)
    
    bot = Bot(TOKEN)
    try:
        await bot.send_message(
            chat_id="@MafiaRedDonOfficial",
            text=text,
            parse_mode="HTML"
        )
    finally:
        await bot.session.close()