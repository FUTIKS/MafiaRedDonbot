import time
import random
import asyncio
import traceback
from dispatcher import bot
from collections import Counter
from aiogram.types import FSInputFile
from mafia_bot.utils import game_tasks
from mafia_bot.models import Game,User
from mafia_bot.buttons.inline import confirm_hang_inline_btn, go_to_bot_inline_btn,action_inline_btn
from mafia_bot.handlers.main_functions import (can_hang, clean_name,games_state, get_most_voted_id,night_reset,day_reset, prepare_confirm_pending,
                                               prepare_hang_pending, prepare_night_pending, punish_afk_night_players,send_night_actions_to_all,
                                               apply_night_actions,ROLE_LABELS, stop_game_if_needed,PEACE_ROLES,MAFIA_ROLES_LAB,SOLO_ROLES)



def run_game_in_background(uuid: str):
    if uuid in game_tasks and not game_tasks[uuid].done():
        return False

    task = asyncio.create_task(start_game(uuid))
    game_tasks[uuid] = task
    return True



async def start_game(uuid):
    try:
        game = Game.objects.filter(uuid=uuid).first()
        if not game:
            return

        game.is_started = True
        game.save()
        game_data_bg = games_state.get(uuid)
        if not game_data_bg:
            return
        game_data_bg['meta']["chat_id"] = game.chat_id
        game_data_bg['meta']["uuid"] = str(game.uuid)
        game_data_bg['meta']['created_at'] = int(time.time())
        day = 1
        sunset = FSInputFile("mafia_bot/gifs/sunset.mp4")
        sunrise = FSInputFile("mafia_bot/gifs/sunrise.mp4")
        while True:
            # ================= NIGHT START =================
            uuid = str(game.uuid)
            night_reset(uuid)
            

            game_data = games_state.get(uuid, {})
            all_players = game_data.get("players", [])   # tg_id list
            alive_players = game_data.get("alive", [])   # tg_id list
            game_data['meta']['message_allowed'] = "no"
            alive_before_night = alive_players.copy()

            # alive ids join-order bilan
            alive_ids = [tg_id for tg_id in all_players if tg_id in alive_players]

            users_qs = User.objects.filter(telegram_id__in=alive_ids).only("telegram_id", "first_name")
            users_map = {u.telegram_id: u for u in users_qs}

            users_after_night = list(users_qs)  # object list keyboardlar uchun

            # night action buttonlar

            games_state[uuid]['meta']['day'] +=1
            games_state[uuid]["meta"]["team_chat_open"] = "yes"
            game_day = games_state[uuid].get("meta", {}).get("day", 0) 
            
            asyncio.create_task(send_night_actions_to_all( uuid, game, users_after_night,game_day))

            await bot.send_video(
                    chat_id=game.chat_id,
                    video=sunset,
                caption="🌃 Tun\nKo'chaga faqat jasur va qo'rqmas odamlar chiqishdi. Ertalab tirik qolganlarni sanaymiz..",
                reply_markup=go_to_bot_inline_btn(2)
            )

            await asyncio.sleep(2)

            msg = "Tirik o'yinchilar:\n\n"

            for idx, tg_id in enumerate(all_players, 1):
                if tg_id not in alive_players:
                    continue
                user = users_map.get(tg_id)
                if not user:
                    continue
                msg += f'{idx}. <a href="tg://user?id={user.telegram_id}">{clean_name(user.first_name)}</a>\n'

            msg += "\nTonggacha 1 daqiqa qoldii!"

            await bot.send_message(
                chat_id=game.chat_id,
                text=msg,
                reply_markup=go_to_bot_inline_btn(2),
                parse_mode="HTML"
            )

            prepare_night_pending(uuid)
    
            event = games_state[uuid]["runtime"]["night_event"]

            try:
                await asyncio.wait_for(event.wait(), timeout=60)
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(3)
            
            if games_state[uuid]['night_actions']['don_kill_target'] is not None:
                await bot.send_message(
                    chat_id=game.chat_id,
                    text="🤵🏻 Mafia navbatdagi o'ljasini tanladi..."
                )
            ended = await stop_game_if_needed(uuid)
            if ended:
                return
            games_state[uuid]["meta"]["team_chat_open"] = "no"


            # ================= MORNING =================

            await bot.send_video(
                chat_id=game.chat_id,
                video=sunrise,
                caption=f"🏙 {day}-kun \nQuyosh chiqdi, ammo tun orqasida nima bo‘lganini faqat bir necha kishi biladi..."
            )
            day += 1
            await asyncio.sleep(3)
            
            games_state[uuid]['meta']['day'] +=1
            await apply_night_actions(uuid)
            await punish_afk_night_players(uuid)
            ended = await stop_game_if_needed(uuid)
            if ended:
                return
            await asyncio.sleep(3)
            # ================= DAY RESET =================
            day_reset(uuid)

        

            alive_after_night = games_state.get(uuid, {}).get("alive", [])

            if len(alive_before_night) == len(alive_after_night):
                await bot.send_message(
                    chat_id=game.chat_id,
                    text="🧐 Ishonish qiyin tunda hech kim o'lmadi..."
                )

            await asyncio.sleep(3)

            # ================= ALIVE LIST AFTER NIGHT =================
            alive_ids_after_night = [tg_id for tg_id in all_players if tg_id in alive_after_night]

            users_after_night_qs = User.objects.filter(telegram_id__in=alive_ids_after_night).only("telegram_id", "first_name")
            users_map_after_night = {u.telegram_id: u for u in users_after_night_qs}

            msg += "\nUlardan:\n\n"

            roles_map = games_state.get(uuid, {}).get("roles", {})

            peace_labels = []
            mafia_labels = []
            solo_labels = []

            for tg_id in alive_ids_after_night:
                role_key = roles_map.get(tg_id)
                label = ROLE_LABELS.get(role_key, "Unknown")

                if role_key in PEACE_ROLES:
                    peace_labels.append(label)
                elif role_key in MAFIA_ROLES_LAB:
                    mafia_labels.append(label)
                elif role_key in SOLO_ROLES:
                    solo_labels.append(label)
                else:
                    peace_labels.append(label)

            def format_role_list(labels: list):
                c = Counter(labels)
                result = []
                for role_label, count in c.items():
                    if count > 1:
                        result.append(f"{role_label} - {count}")
                    else:
                        result.append(role_label)
                random.shuffle(result)
                return ", ".join(result) if result else "—"

            msg += f"Tinch axolilar - {len(peace_labels)}\n {format_role_list(peace_labels)}\n\n"
            msg += f"Mafialar - {len(mafia_labels)}\n {format_role_list(mafia_labels)}\n\n"
            msg += f"Yakka rollar - {len(solo_labels)}\n {format_role_list(solo_labels)}\n"

            msg += "\n\nTunda bo'lgan xodisalarni muxokama qilishning ayni vaqti..."


            await bot.send_message(
                chat_id=game.chat_id,
                text=msg,
                parse_mode="HTML"
            )
            games_state[uuid]['meta']['message_allowed'] = "yes"
            # ================= DISCUSSION =================
            await asyncio.sleep(45)
            ended = await stop_game_if_needed(uuid)
            if ended:
                return
            # ================= START VOTING =================
            await bot.send_message(
                chat_id=game.chat_id,
                text="Aybdorlarni aniqlash va jazolash vaqti keldi.\nOvoz berish uchun 45 sekund",
                reply_markup=go_to_bot_inline_btn(3)
            )
            game_day = games_state.get(uuid, {}).get("meta", {}).get("day", 0)
            # har bir tirikka osish keyboard yuboramiz
            for tg_id in alive_ids_after_night:
                game_data = games_state.get(uuid, {})
                night_action = game_data.get("night_actions", {})
                lover_block_target = night_action.get("lover_block_target")
                if lover_block_target == tg_id:
                    continue
                try:
                    await bot.send_message(
                        chat_id=tg_id,
                        text="Aybdorlarni izlash vaqti keldi!\nKimni osishni xohlaysiz?",
                        reply_markup=action_inline_btn(
                            action="hang",
                            own_id=tg_id,
                            players=users_after_night_qs,
                            game_id=game.id,
                            chat_id=game.chat_id,
                            day=game_day,
                        )
                    )
                except Exception:
                    pass

            prepare_hang_pending(uuid)

            games_state[uuid]['meta']['message_allowed'] = "no"
            event = games_state[uuid]["runtime"]["hang_event"]
            try:
                await asyncio.wait_for(event.wait(), timeout=45)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(2)
            games_state[uuid]["meta"]["day"] +=1

            ended = await stop_game_if_needed(uuid)
            if ended:
                return

            # ================= MOST VOTED =================
            top_voted = get_most_voted_id(uuid)  # siz yozgan function: tie bo'lsa False
            if not top_voted:
                await bot.send_message(
                    chat_id=game.chat_id,
                    text="Ovoz berish yakunlandi.\nOvoz berish janjalga aylanib ketdi... Xamma uy-uyiga tarqaldi..."
                )
                continue

            voted_user = users_map_after_night.get(top_voted)
            if not voted_user:
                await bot.send_message(chat_id=game.chat_id, text="❗ Ovoz berilgan o'yinchi topilmadi.")
                continue

            # ================= CONFIRM HANG =================
            msg_obj = await bot.send_message(
                chat_id=game.chat_id,
                text=f"Rostandan ham <a href='tg://user?id={voted_user.telegram_id}'>{clean_name(voted_user.first_name)}</a> ni osmoqchimisiz?",
                reply_markup=confirm_hang_inline_btn(
                    voted_user_id=voted_user.telegram_id,
                    game_id=game.id,
                    chat_id=game.chat_id,
                    yes=0,
                    no=0
                ),
                parse_mode="HTML"
            )

            games_state[uuid]["day_actions"]["hang_confirm_msg_id"] = msg_obj.message_id
            games_state[uuid]["day_actions"]["hang_target_id"] = voted_user.telegram_id

            prepare_confirm_pending(uuid,voted_user.telegram_id)

            event = games_state[uuid]["runtime"]["confirm_event"]
            try:
                await asyncio.wait_for(event.wait(), timeout=45)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(2)

            ended = await stop_game_if_needed(uuid)
            if ended:
                return

            try:
                await msg_obj.edit_text(
                    text=(
                        f"Rostandan ham <a href='tg://user?id={voted_user.telegram_id}'>{clean_name(voted_user.first_name)}</a> ni osmoqchimisiz?\n\n"
                        "Ovoz berish tugadi."
                    ),
                    reply_markup=None,
                    parse_mode="HTML"
                )
            except Exception:
                pass

            await asyncio.sleep(3)

            # ================= FINAL CONFIRM RESULT =================
            final_vote, yes, no = can_hang(uuid)

            if final_vote == "no":
                await bot.send_message(
                    chat_id=game.chat_id,
                    text=f"Aholi kelisha olmadi ({yes} 👍 | {no} 👎 )...\nKelisha olmaslik oqibatida hech kim osilmadi..."
                )
                continue

            await bot.send_message(
                chat_id=game.chat_id,
                text=(
                    f"Ovoz berish natijalari:\n\n"
                    f"{yes} 👍  |  {no} 👎\n\n"
                    f"<a href='tg://user?id={voted_user.telegram_id}'>{clean_name(voted_user.first_name)}</a> - ni osamiz! :)"
                ),
                parse_mode="HTML"
            )

            # ================= HANG PLAYER =================
            target_id = voted_user.telegram_id

            if target_id in games_state[uuid]["alive"]:
                games_state[uuid]["alive"].remove(target_id)

            if target_id not in games_state[uuid]["dead"]:
                games_state[uuid]["dead"].append(target_id)

            games_state[uuid]["day_actions"]["last_hanged"] = target_id
            

            await asyncio.sleep(2)
            await bot.send_message(
                chat_id=game.chat_id,
                text = f"<a href='tg://user?id={voted_user.telegram_id}'>{clean_name(voted_user.first_name)}</a> - {ROLE_LABELS.get(roles_map.get(voted_user.telegram_id))} edi!!"
            )
            
            await asyncio.sleep(2)
            ended = await stop_game_if_needed(uuid)
            if ended:
                return

            # loop davom etadi
            continue

            
    except asyncio.CancelledError:
        print(f"Game {uuid} cancelled.")
        return
    except Exception as e:
        traceback.print_exc()
        return

