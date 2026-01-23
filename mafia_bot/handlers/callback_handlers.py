import re
import json
import time
import datetime
from aiogram import F
from datetime import timedelta
from dispatcher import dp, bot
from django.db.models import Sum
from django.utils import timezone
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext 
from core.constants import DESCRIPTIONS,ACTIONS, ROLES_CHOICES
from django.contrib.auth.hashers import make_password
from mafia_bot.utils import stones_taken,gsend_taken,giveaways,games_state
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery,CallbackQuery
from mafia_bot.models import Game, MoneySendHistory, User,PremiumGroup,MostActiveUser,CasesOpened,GameSettings,GroupTrials,PriceStones, UserRole,BotCredentials
from mafia_bot.state import AddGroupState, BeginInstanceState,SendMoneyState,ChangeStoneCostState,ChangeMoneyCostState,ExtendGroupState,QuestionState,Register,CredentialsState
from mafia_bot.handlers.main_functions import (add_visit, get_mafia_members,get_first_name_from_players,
                                               mark_confirm_done, mark_hang_done,mark_night_action_done,get_week_range,get_month_range)
from mafia_bot.buttons.inline import (
    admin_inline_btn, answer_admin, back_btn, cart_inline_btn, change_money_cost, change_stones_cost, com_inline_btn, end_talk_keyboard,  giveaway_join_btn, group_profile_inline_btn,
    groupes_keyboard, groups_buy_stars, history_groupes_keyboard, money_case, pay_for_money_inline_btn, pay_using_stars_inline_btn, role_shop_inline_keyboard,
    shop_inline_btn, main_inline_btn, roles_inline_btn, com_inline_action_btn,pirate_steal_inline_btn,
    professor_gift_inline_btn,confirm_hang_inline_btn,groups_inline_btn,group_manage_btn,back_admin_btn,case_inline_btn,
    stone_case,begin_instance_inline_btn, take_gsend_stone_btn, take_gsend_stone_btn, take_stone_btn,trial_groupes_keyboard,trial_group_manage_btn,privacy_inline_btn
)


# Callbackdan kelganda
@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    user = User.objects.filter(telegram_id=callback.from_user.id).first()
    if not user:
        user = User.objects.create(
            telegram_id=callback.from_user.id,
            lang ='uz',
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )
        
    user_role = UserRole.objects.filter(user_id=user.id)
    text =""
    for user_r in user_role:
        role_name = dict(ROLES_CHOICES).get(user_r.role_key, "Noma'lum rol")
        text += f"🎭 {role_name} - Soni: {user_r.quantity}\n"
    await callback.message.edit_text(
        text=(
            f"👤 <code>{callback.from_user.first_name}</code>\n\n"
            f"💶 Pullar: {user.coin}\n"
            f"💎 Olmoslar: {user.stones}\n\n"
            f"🛡 Ximoya: {user.protection}\n"
            f"📂 Hujjatlar: {user.docs}\n"
            f"\n{ text }"
        ),
        parse_mode="HTML",reply_markup=cart_inline_btn()
    )

@dp.callback_query(F.data == "cart")
async def cart_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(
        reply_markup=shop_inline_btn()
    )


@dp.callback_query(F.data == ("roles_back_main"))
async def back_callback_special(callback: CallbackQuery):
    await callback.message.edit_text(
    text=f"Salom! <code>{callback.from_user.first_name}</code>\nMen 🤵🏻Mafia o'yinini rasmiy botiman.",
    parse_mode="HTML",
    reply_markup=main_inline_btn()
)
    
@dp.callback_query(F.data == ("language"))
async def language_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text = "Hozircha bu funksiya mavjud emas."
    )
    
   
# Callbackdan kelganda
@dp.callback_query(F.data.startswith("back_"))
async def back_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    place = callback.data.split("_")[1]
    if place== "profile":
        await profile_callback(callback)
    elif place == "admin":
        await callback.message.edit_text(
            text="⚙️ Admin paneli",
            reply_markup=admin_inline_btn()
        )
    elif place == "case":
        await callback.message.edit_text(
        text= ("📦 Quti bo'limi\n\n"
            "💰 Pulli sandiq – ichida turli xildagi pul xazinalari yashiringan\n"
            "(💶 900 dan 💶 2000 gacha). Narxi: 💎 1 \n\n"
            "💠 Olmosli sandiq – sirli olmoslar bilan to‘la, ichidan 4 dan 12 tagacha olmos chiqishi mumkin. Narxi: 💶 10 000 \n\n"
            "⭐️ Vip user – olmosli sandiqni cheklanmagan miqdorda ochish imkoniyati, oy oxirigacha amal qiladi. Eng so‘nggi darajadagi imkoniyat! Narxi: 💎 20 \n\n"
            "Oddiy userdan farqi: ⭐️ Vip user har bitta sandiq ochganiga 💶 10 000 to'laydi oddiy user 1 oyda faqat 1 marta 💶 10 000 sarflab ocha oladi"),
        parse_mode="HTML",
        reply_markup=case_inline_btn()
    )
    elif place == "money":
        button = pay_for_money_inline_btn(is_money=True)
        await callback.message.edit_text(
            text="Kerakli tolov tizimini tanlang:",
            reply_markup=button
        )
    elif place == "stone":
        button = pay_for_money_inline_btn(is_money=False)
        await callback.message.edit_text(
            text="Kerakli tolov tizimini tanlang:",
            reply_markup=button
        )
    elif place == "group":
        group_trial = GroupTrials.objects.filter(group_id=callback.message.chat.id).first()
        if not group_trial:
            link = callback.message.chat.username if callback.message.chat.username else ""
            if link == "":
                invite = await bot.create_chat_invite_link(
                chat_id=callback.message.chat.id,
                creates_join_request=False
            )   
                link = invite.invite_link
            group_trial = GroupTrials.objects.create(
                group_id=callback.message.chat.id,
                group_name=callback.message.chat.title if callback.message.chat.title else "",
                group_username=link
            )
        is_active = group_trial.end_date > timezone.now()
        has_stone = group_trial.stones >= 20
        await callback.message.edit_text(text=(
            f"Guruh hisobi: 🪙 {group_trial.coins if group_trial else 0}\n"
            f"Guruh holati: {'✅ Aktiv' if is_active else '❌ Aktiv emas'}\n\n"
            f"Keyingi aktivlashtirish vaqti: {group_trial.end_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Guruh hisobi: 💎 {group_trial.stones if group_trial else 0}\n"
            f"Premium hisobi: 💎 {group_trial.premium_stones if group_trial else 0}\n"
            f"Amal qilish muddati: 2026-01-26 03:51:35"
        ),
        reply_markup=group_profile_inline_btn(has_stone, callback.message.chat.id)
        )
    elif place == "groups":
        page = 1
        limit = 5
        offset = (page - 1) * limit
        groupes = GroupTrials.objects.all()[offset:offset + limit]
        total = GroupTrials.objects.count()
        total_pages = (total + limit - 1) // limit
        
        
        group_list = "\n".join([
        f"{i+1}. <a href='{group.group_username}'>{group.group_name}</a>"
        if group.group_username
        else f"{i+1}. {group.group_name}"
        for i, group in enumerate(groupes)
        ])

        await callback.message.edit_text(
            text=f"Obunadagi guruhlar (sahifa {page}/{total_pages}):\n\n{group_list}",
            reply_markup=trial_groupes_keyboard(questions=groupes, page=page, total=total, per_page=limit))
        
        
        


# Callbackdan kelganda
@dp.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: CallbackQuery):
    thing_to_buy = callback.data.split("y_")[1]
    user = User.objects.filter(telegram_id=callback.from_user.id).first()
    if not user:
        user = User.objects.create(
            telegram_id=callback.from_user.id,
            lang ='uz',
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )
    if thing_to_buy == "protection":
        if user.coin >= 100:
            user.coin -= 100
            user.protection += 1
            user.save()
            await callback.message.edit_text(
                text=(
                    f"Sotib olindi: 🛡 Ximoya\n\n"
                    f"👤 <code>{callback.from_user.first_name}</code>\n\n"
                    f"💶 Pullar: {user.coin}\n"
                    f"💎 Olmoslar: {user.stones}\n\n"
                    f"🛡 Ximoya: {user.protection}\n"
                    f"📂 Hujjatlar: {user.docs}\n\n"
                ),
                parse_mode="HTML",
                reply_markup=cart_inline_btn()
            )
        else:
            await callback.answer(text="❌ Sizda pullar yetarli emas!", show_alert=True)
    elif thing_to_buy == "docs":
        if user.coin >= 150:
            user.coin -= 150
            user.docs += 1
            user.save()
            await callback.message.edit_text(
                text=(
                    f"Sotib olindi: 📂 Hujjatlar\n\n"
                    f"👤 <code>{callback.from_user.first_name}</code>\n\n"
                    f"💶 Pullar: {user.coin}\n"
                    f"💎 Olmoslar: {user.stones}\n\n"
                    f"🛡 Ximoya: {user.protection}\n"
                    f"📂 Hujjatlar: {user.docs}\n\n"
                ),
                parse_mode="HTML",
                reply_markup=cart_inline_btn()
            )
        else:
            await callback.answer(text="❌ Sizda pullar yetarli emas!", show_alert=True)
    elif thing_to_buy == "active_role":
        await callback.message.edit_text(
            text="🎭 Rol sotib olish uchun quyidagi ro'llardan birini tanlang:",
            reply_markup=role_shop_inline_keyboard()
        )

@dp.callback_query(F.data.startswith("active_"))
async def buy_role_callback(call: CallbackQuery, state: FSMContext):
    
    role_key = call.data.split("_")[1]
    price = int(call.data.split("_")[2])
    
    if price<15:
        currency = "stones"
    else:
        currency = "money"

    user = User.objects.filter(telegram_id=call.from_user.id).first()
    if not user:
        user = User.objects.create(
            telegram_id=call.from_user.id,
            lang ='uz',
            first_name=call.from_user.first_name,
            username=call.from_user.username
        )
    if currency == "stones":
        if user.stones < price:
            return await call.answer("💎 Olmos yetarli emas!", show_alert=True)
        user.stones -= price

    if currency == "money":
        if user.coin < price:
            return await call.answer("💵 Pul yetarli emas!", show_alert=True)
        user.coin -= price

    await user.asave(update_fields=["stones", "coin"])
    user_role, created = UserRole.objects.get_or_create(user=user, role_key=role_key)
    if not created:
        user_role.quantity += 1
    user_role.save()

    await call.answer("✅ Rol sotib olindi!", show_alert=True)

    await call.message.edit_text(
        text="✅ Rol sotib olindi.\n\nBoshqa rol olasizmi?",
        reply_markup=role_shop_inline_keyboard()
    )

    

# Callbackdan kelganda
@dp.callback_query(F.data == ("role_menu"))
async def roles_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("🎎 Mavjud rollar ro'yxati\n\nUning tavsifini ko'rish uchun rol nomini bosing",reply_markup=roles_inline_btn())


@dp.callback_query(F.data.startswith("money_"))
async def buy_money_handler(callback: CallbackQuery):
    await callback.answer()
    if callback.data == "money_stone":
        button = pay_for_money_inline_btn(is_money=False)
    else:
        button = pay_for_money_inline_btn(is_money=True)
    await callback.message.edit_text(
        text="Kerakli tolov tizimini tanlang:",
        reply_markup=button
    )
    

@dp.callback_query(F.data.startswith("p2p_"))
async def p2p_callback(callback: CallbackQuery):
    await callback.answer()
    which = callback.data.split("_")[1]
    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()
    if which == "money":
        text = f"💶 Pulni naqd pul orqali olish\n\nNarxlar:\n\n{cost.money_in_money}\n\nTo'lovni amalga oshirish uchun @RedDon_Mafia ga yozing."
        await callback.message.edit_text(
        text=text,
        reply_markup=back_btn("money")
    )
    else:
        await callback.message.edit_text(
        text=f"💎 Olmosni naqd pul orqali olish\n\nNarxlar:\n\n{cost.stone_in_money}\n\nTo'lovni amalga oshirish uchun @RedDon_Mafia ga yozing.",
        reply_markup=back_btn("stone")
    )
        
@dp.callback_query(F.data.startswith("star_"))
async def star_callback(callback: CallbackQuery):
    await callback.answer()
    which = callback.data.split("_")[1]
    if which == "money":
        await callback.message.edit_text(
            text = "💶 Pulni yulduzlar evaziga olish\nKerakli miqdorni tanlang:",
            reply_markup=pay_using_stars_inline_btn(is_money=True)
        )
    elif which == "stone":
        await callback.message.edit_text(
            text = "💎 Olmosni yulduzlar evaziga olish\nKerakli miqdorni tanlang:",
            reply_markup=pay_using_stars_inline_btn(is_money=False)
        )
    elif which == "group":
        await callback.message.edit_text(
            text = "Kerakli miqdorni tanlang:",
            reply_markup=groups_buy_stars(callback.message.chat.id)
        )
    
    


@dp.callback_query(F.data.startswith("roles_"))
async def roles_specific_callback(callback: CallbackQuery):
    role_name = callback.data.split("_")[1]

    if role_name in DESCRIPTIONS:
        await callback.answer(text=DESCRIPTIONS[role_name], show_alert=True)


@dp.callback_query(F.data.startswith("doc_"))
async def doc_heal_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")    
    target_id = parts[1]  
    chat_id = int(parts[3])
    day = parts[4]
    doctor_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('doc_heal')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not doctor_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('doc_heal')}\n\nSiz hech kimni davolamadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 👨🏼‍⚕️ Shifokor hech qayoqqa bormaslikni afzal ko'rdi."
        )
        return
    
    target_id = int(target_id)
    # doc o'zini 1 martadan ko'p heal qila olmaydi
    if target_id == doctor_id:
        used_self = game["limits"]["doc_self_heal_used"]
        if doctor_id in used_self:
            return
        used_self.add(doctor_id)

    # ✅ night action saqlash
    game["night_actions"]["doc_target"] = target_id
    add_visit(game=game, visitor_id=doctor_id, house_id=target_id, invisible=False)


    # username olish (players object bo'lsa)
    target_name = get_first_name_from_players(target_id)

    text = f"{ACTIONS.get('doc_heal')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni davoladingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")
    
    await bot.send_message(
            chat_id=chat_id,
            text="👨🏼‍⚕️ Shifokor tungi navbatchilikka ketdi..."
        )
    

@dp.callback_query(F.data.startswith("daydi_"))
async def daydi_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    house_id = parts[1]
    chat_id = int(parts[3])
    day = parts[4]

    daydi_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('daydi_watch')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not daydi_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if house_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('daydi_watch')}\n\nSiz hech kimning uyiga bormadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 🧙🏼‍♂️ Daydi hech qayoqqa bormaslikni afzal ko'rdi."
        )
        return
    house_id = int(house_id)

    # ✅ Daydi qayerga bordi
    game["night_actions"]["daydi_house"] = house_id
    

    # username topish (players object list bo‘lsa)
    target_name = get_first_name_from_players(house_id)
    await callback.message.edit_text(
        text=f"{ACTIONS.get('daydi_watch')}\n\nSiz <a href='tg://user?id={house_id}'>{target_name}</a> uyiga shisha olgani bordingiz.",
        parse_mode="HTML"
    )

    await bot.send_message(chat_id=chat_id, text="🧙🏼‍♂️ Daydi kimnikigadir shisha olish uchun ketdi...")

    


@dp.callback_query(F.data.startswith("com_"))
async def com_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    action = parts[1]     
    chat_id = int(parts[3])
    day = parts[4]
    com_id = callback.from_user.id
    game = games_state.get(int(parts[2]))
    if not game:
        return
    if not com_id in game["alive"]:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('com_deside')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    mark_night_action_done(game, callback.from_user.id)
    if action == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('com_deside')}\n\nSiz hech narsa qilmaslikni tanladingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 🕵️‍ Komissar bugun dam olishni xohladi."
        )
        return
    elif action == "back":
        await callback.message.edit_text(
            text=ACTIONS.get("com_deside"),
            reply_markup=com_inline_btn(game.id, game.chat_id,day=day)
        )
        return
    
    if action == "shoot":
        await bot.send_message(chat_id=chat_id, text="🕵️‍ Komissar Katani pistoletini o'qladi...")
        await callback.message.edit_text(
            text=ACTIONS.get("com_shoot"),
            reply_markup=com_inline_action_btn(action="shoot",chat_id=chat_id, game_id=int(parts[2]),com_id=com_id,day=day)
        )
        return

    await bot.send_message(chat_id=chat_id, text="🕵️‍ Komissar Katani yovuzlarni qidirishga ketdi...")
    await callback.message.edit_text(
        text=ACTIONS.get("com_check"),
        reply_markup=com_inline_action_btn(action="search",chat_id=chat_id, game_id=int(parts[2]),com_id=com_id,day=day)
    )


@dp.callback_query(F.data.startswith("shoot_"))
async def com_shoot_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = int(parts[1])

    com_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    day = parts[3]
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('com_shoot')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not com_id in game["alive"]:
        print("com not alive")
        return
    

    game["night_actions"]["com_shoot_target"] = target_id
    print("saved shoot target")
    add_visit(game, com_id, target_id, False)
    print("added visit")


    target_name = get_first_name_from_players( target_id)
    print("got target name")

    await callback.message.edit_text(
        text=f"{ACTIONS.get('com_shoot')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni otdingiz.",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("search_"))
async def com_protect_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = int(parts[1])
    day = parts[3]
    com_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('com_check')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not com_id in game["alive"]:
        return
   

    # ✅ Action saqlaymiz
    game["night_actions"]["com_check_target"] = target_id
    print("saved check target")
    add_visit(game, com_id, target_id, False)
    print("added visit")


    target_name = get_first_name_from_players( target_id)
    print("got target name")

    await callback.message.edit_text(
        text=f"{ACTIONS.get('com_check')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tekshirdingiz.",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("kami_"))
async def kamikaze_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = int(parts[1])  
    day = parts[4]

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('kamikaze_blow')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    game["day_actions"]["kamikaze_trigger"] = target_id
    mark_night_action_done(game, callback.from_user.id)



    # username olish (players object bo'lsa)
    target_name = get_first_name_from_players(target_id)

    text = f"{ACTIONS.get('kamikaze_blow')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni portlatdingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")

    
    
@dp.callback_query(F.data.startswith("lover_"))
async def lover_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = parts[1]
    chat_id = int(parts[3])
    day = parts[4]
    lover_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('lover_block')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not lover_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('lover_block')}\n\nSiz hech kimni tanlamadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 💃🏼 Ma'shuqa hech kimni kutmayapti."
        )
        return
    target_id = int(target_id)
    # ✅ lover action saqlash
    game["night_actions"]["lover_block_target"] = target_id
    add_visit(game=game, visitor_id=lover_id, house_id=target_id, invisible=False)

    target_name = get_first_name_from_players(target_id)

    text = f"{ACTIONS.get('lover_block')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a>ni tanladingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")

    await bot.send_message(
        chat_id=chat_id,
        text="💃🏼 Ma'shuqa qandaydir mehmonni kutayapti..."
    )
    return

@dp.callback_query(F.data.startswith("killer_"))
async def killer_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = parts[1]
    chat_id = int(parts[3])
    day = parts[4]
    killer_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('killer_kill')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not killer_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('killer_kill')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 🔪 Qotil hech kimni o'ldirmaslikni afzal ko'rdi."
        )
        return
    target_id = int(target_id)
    # ✅ killer action saqlash
    game["night_actions"]["killer_target"].append(target_id)

    target_name = get_first_name_from_players(target_id)
    add_visit(game=game, visitor_id=killer_id, house_id=target_id, invisible=False)

    text = f"{ACTIONS.get('killer_kill')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni o'ldirdingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")

    await bot.send_message(
        chat_id=chat_id,
        text="🔪 Qotil butalar orasiga yashirinib oldi..."
    )
    return

@dp.callback_query(F.data.startswith("santa_"))
async def santa_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = parts[1]
    chat_id = int(parts[3])
    day = parts[4]
    santa_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('santa')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not santa_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('santa')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 🎅 Santa hech kimga sovg'a bermaslikni afzal ko'rdi."
        )
        return
    target_id = int(target_id)
    # ✅ killer action saqlash
    user = User.objects.filter(telegram_id=target_id).first()
    if not user:
        user = User.objects.create(
            telegram_id=target_id,
            lang ='uz',
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )
    user.coin += 20
    user.save()
    target_name = get_first_name_from_players(target_id)
    add_visit(game=game, visitor_id=santa_id, house_id=target_id, invisible=False)

    text = f"{ACTIONS.get('santa')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ga sovg'a berdingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")
    await bot.send_message(
        chat_id=target_id,
        text="🎅 Sizga Santa tomonidan 20 ta pullar sovg'a qilindi!"
    )
    await bot.send_message(
        chat_id=chat_id,
        text="🎅 Santa sovg'alarini tarqatmoqda..."
    )
    return

@dp.callback_query(F.data.startswith("kaldun_"))
async def kaldun_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)

    parts = callback.data.split("_")
    target_id = parts[1]
    chat_id = int(parts[3])
    day = parts[4]
    kaldun_id = callback.from_user.id

    game = games_state.get(int(parts[2]))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('kaldun_spell')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not kaldun_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('kaldun_spell')}\n\nSiz hech kimni sehrlamadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="🚷 ⚡️ Koldun hech kimni sehrlamaslikni afzal ko'rdi."
        )
        return

    target_id = int(target_id)

    # ✅ kaldun action saqlash
    game["night_actions"]["kaldun_target"] = target_id
    
    add_visit(game=game, visitor_id=kaldun_id, house_id=target_id, invisible=False)
    target_name = get_first_name_from_players(target_id)

    text = f"{ACTIONS.get('kaldun_spell')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni sehrladingiz."

    await callback.message.edit_text(text=text, parse_mode="HTML")

    await bot.send_message(
        chat_id=chat_id,
        text="⚡️ Koldun o'z sehrini ishga soldi."
    )
    return



@dp.callback_query(F.data.startswith("don_"))
async def don_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    day = callback.data.split("_")[4]
    
    don_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('don_kill')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not don_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('don_kill')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        
        return
    
    # ✅ night action saqlash
    game["night_actions"]["don_kill_target"] = int(target_id)
    add_visit(game=game, visitor_id=don_id, house_id=target_id, invisible=False)
    
    
    target_name = get_first_name_from_players(int(target_id))
    mafia_name = get_first_name_from_players(don_id)
    mafia_members = get_mafia_members(int(game_id))
    

    text_for_mafia = (
        f"🤵🏻 Don <a href='tg://user?id={don_id}'>{mafia_name}</a> - <a href='tg://user?id={target_id}'>{target_name}</a> uchun ovoz berdi"
    )

    for member_id in mafia_members:
        if member_id == don_id:
            continue
        try:
            await bot.send_message(
                chat_id=member_id,
                text=text_for_mafia,
                parse_mode="HTML"
            )
        except Exception as e:
            print(e)
    
    await callback.message.edit_text(text=f"{ACTIONS.get('don_kill')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")
    

@dp.callback_query(F.data.startswith("mafia_"))
async def mafia_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    day = callback.data.split("_")[3]
    
    mafia_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('mafia_vote')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not mafia_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('mafia_vote')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        return
    # ✅ night action saqlash
    game["night_actions"]["mafia_vote"].append(int(target_id))
    add_visit(game=game, visitor_id=mafia_id, house_id=target_id, invisible=False)
    
    
    target_name = get_first_name_from_players(int(target_id))
    mafia_name = get_first_name_from_players(mafia_id)
    mafia_members = get_mafia_members(int(game_id))
    

    text_for_mafia = (
        f"🤵🏼 Mafiya a'zosi <a href='tg://user?id={mafia_id}'>{mafia_name}</a> - <a href='tg://user?id={target_id}'>{target_name}</a> uchun ovoz berdi"
    )

    for member_id in mafia_members:
        if member_id == mafia_id:
            continue

        try:
            await bot.send_message(
                chat_id=member_id,
                text=text_for_mafia,
                parse_mode="HTML"
            )
        except Exception as e:
            print(e)
    
    await callback.message.edit_text(text=f"{ACTIONS.get('mafia_vote')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("adv_"))
async def adv_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = int(callback.data.split("_")[1])
    game_id = int(callback.data.split("_")[2])
    chat_id = int(callback.data.split("_")[3])
    day = callback.data.split("_")[4]
    adv_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('adv_mask')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not adv_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('adv_mask')}\n\nSiz hech kimni ximoya qilmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 ⚖️ Advokat hech kimni ximoya qilmaslikni afzal ko'rdi."
        )
        return
    # ✅ night action saqlash
    game["night_actions"]["advokat_target"] = int(target_id)
    add_visit(game=game, visitor_id=adv_id, house_id=target_id, invisible=False)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"👨🏼‍💼 Advokat ximoya qiluvchi Mafiani tanladi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    adv_name = get_first_name_from_players(adv_id)
    mafia_members = get_mafia_members(int(game_id))
    

    text_for_mafia = (
        f"👨🏼‍💼 Advokat {adv_name} tanlovi: <a href='tg://user?id={target_id}'>{target_name}</a>"
    )

    for member_id in mafia_members:
        if member_id == adv_id:
            continue

        try:
            await bot.send_message(
                chat_id=member_id,
                text=text_for_mafia,
                parse_mode="HTML"
            )
        except Exception as e:
            print(e)
    

    await callback.message.edit_text(text=f"{ACTIONS.get('adv_mask')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("spy_"))
async def spy_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    spy_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('spy_check')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not spy_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('spy_check')}\n\nSiz hech kimni tekshirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 🦇 Ayg'oqchi hech kimni tekshirmaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["spy_target"] = int(target_id)
    add_visit(game=game, visitor_id=spy_id, house_id=target_id, invisible=False)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"🦇 Ayg'oqchi o'z harakatini boshladi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    spy_name = get_first_name_from_players(spy_id)
    mafia_members = get_mafia_members(int(game_id))
    text_for_mafia = (
        f"🦇 Ayg'oqchi {spy_name} tanlovi: <a href='tg://user?id={target_id}'>{target_name}</a>"
    )
    for member_id in mafia_members:
        if member_id == spy_id:
            continue

        try:
            await bot.send_message(
                chat_id=member_id,
                text=text_for_mafia,
                parse_mode="HTML"
            )
        except Exception as e:
            print(e)
    
    
    await callback.message.edit_text(text=f"{ACTIONS.get('spy_check')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("lab_"))
async def lab_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = int(callback.data.split("_")[1])
    game_id = int(callback.data.split("_")[2])
    chat_id = int(callback.data.split("_")[3])
    day = callback.data.split("_")[4]
    
    lab_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('lab_action')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not lab_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('lab_action')}\n\nSiz hech kimga o'lim eleksirini bermadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 👨‍🔬 Labarant hech kimga o'lim eleksirini bermaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["lab_target"] = int(target_id)
    add_visit(game=game, visitor_id=lab_id, house_id=target_id, invisible=False)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"👨‍🔬 Labarant o'lim eleksirini ishga soldi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    
    await callback.message.edit_text(text=f"{ACTIONS.get('lab_action')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("arrow_"))
async def arrow_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    
    arrow_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('arrow_kill')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not arrow_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('arrow_kill')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 🏹 Kamonchi hech kimni o'ldirmaslikni afzal ko'rdi."
        )   
        return
    # ✅ night action saqlash
    game["night_actions"]["arrow_target"] = int(target_id)
    add_visit(game=game, visitor_id=arrow_id, house_id=target_id, invisible=True)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"🏹 Kamonchi o'z nishonini tanlab oldi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    
    await callback.message.edit_text(text=f"{ACTIONS.get('arrow_kill')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("trap_"))
async def trap_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    
    trap_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('trap_action')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not trap_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('trap_action')}\n\nSiz hech kimning uyiga mina joylashtirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 ☠️ Minior hech kimning uyiga mina joylashtirmaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["trap_house"] = int(target_id)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"☠️ Minior o'z 🧨 minasini joylashtirdi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    
    await callback.message.edit_text(text=f"{ACTIONS.get('trap_action')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("snyper_"))
async def snyper_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    
    snyper_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('snyper_kill')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not snyper_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('snyper_kill')}\n\nSiz hech kimni o'ldirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 👨🏻‍🎤 Snayper hech kimni o'ldirmaslikni afzal ko'rdi."
        )   
        return
    
    # ✅ night action saqlash
    game["night_actions"]["snyper_target"] = int(target_id)
    add_visit(game=game, visitor_id=snyper_id, house_id=target_id, invisible=True)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"👨🏻‍🎤 Snayper nishonini tanladi va tepkini bosdi",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    
    await callback.message.edit_text(text=f"{ACTIONS.get('snyper_kill')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")



@dp.callback_query(F.data.startswith("traitor_"))
async def spy_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    
    traitor_id = callback.from_user.id
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('traitor_choose')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not traitor_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('traitor_choose')}\n\nSiz hech kimning rolini o'zlashtirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 🦎 Sotqin hech kimning rolini o'zlashtirmaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["traitor_target"] = int(target_id)
    add_visit(game=game, visitor_id=traitor_id, house_id=target_id, invisible=False)
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"🦎 Sotqin kimningdir rolini o'zlashtirdi",
    )
    target_name = get_first_name_from_players(int(target_id))
    await callback.message.edit_text(text=f"{ACTIONS.get('traitor_choose')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")
    


@dp.callback_query(F.data.startswith("snowball_"))
async def snowball_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    
    snowball_id = callback.from_user.id
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('snowball_kill')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not snowball_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('snowball_kill')}\n\nSiz hech kimni qor bilan to'ldirmadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 ❄️ Qorbola hech kimni qor bilan to'ldirmaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["snowball_target"] = int(target_id)
    add_visit(game=game, visitor_id=snowball_id, house_id=target_id, invisible=False)
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"❄️ Qorbola kimnidir qor bilan to'ldirdi",
    )
    target_name = get_first_name_from_players(int(target_id))
    await callback.message.edit_text(text=f"{ACTIONS.get('snowball_kill')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("pirate_"))
async def pirate_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    pirate_id = callback.from_user.id
    day = callback.data.split("_")[4]
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('pirate_steal')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if not pirate_id in game["alive"]:
        return
    
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('pirate_steal')}\n\nSiz hech kimni o'g'irlamangiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 👺 Qaroqchi hech kimni o'g'irlashni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["pirate"]['target_id'] = int(target_id)
    game["night_actions"]["pirate"]['pirate_id'] = int(pirate_id)
    add_visit(game=game, visitor_id=pirate_id, house_id=target_id, invisible=False)

    await bot.send_message(
        chat_id=int(target_id),
        text=f"👺 Qaroqchi sizning narsalaringizni o'g'irlash uchun keldi\nUnga 10💶 pul berasizmi!!!",
        reply_markup=pirate_steal_inline_btn(pirate_id=pirate_id,game_id=int(game_id),day=day)
    )
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"👺 Qaroqchi kimnidir tunash uchun ovga chiqdi...",
    )
    target_name = get_first_name_from_players(int(target_id))
    await callback.message.edit_text(text=f"{ACTIONS.get('pirate_steal')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("pirpay_"))
async def pirpay_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    parts = callback.data.split("_")
    confirmation = str(parts[1])
    pirate_id = int(parts[2])
    game_id = int(parts[3])
    day = parts[4]
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text="👺 Siz kechikdingiz.", parse_mode="HTML")
        return
    if not pirate_id in game["alive"]:
        return
    target_id = callback.from_user.id
    if not target_id in game["alive"]:
        return
    target_name = get_first_name_from_players(int(target_id))
    if confirmation == "no":
        await callback.message.edit_text(text="👺 Siz Qaroqchiga pul bermadingiz va u endi sizni o'ldirishi mumkin!!!")
        await bot.send_message(
            chat_id=pirate_id,
            text=f"<a href='tg://user?id={target_id}'>{target_name}</a> sizga 10💶 berishdan bosh tortdi!"
        )
        game['night_actions']['pirate']['result'] = "no"
        return
    target_player = User.objects.filter(telegram_id=int(target_id)).first()
    if not target_player:
        target_player = User.objects.create(
            telegram_id=target_id,
            lang ='uz',
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )
    if target_player.coin < 10:
        await callback.message.edit_text(text="👺 Sizda Qaroqchiga berish uchun 10💶 pulingiz yetarli emas va u endi sizni o'ldirishi mumkin!!!")
        await bot.send_message(
            chat_id=pirate_id,
            text=f"<a href='tg://user?id={target_id}'>{target_name}</a> sizga 10💶 berish uchun puli yetarli emas!"
        )
        game['night_actions']['pirate']['result'] = "no_money"
        return
    target_player.coin -= 10
    target_player.save()
    pirate_player = User.objects.filter(telegram_id=int(pirate_id)).first()
    pirate_player.coin += 10
    pirate_player.save()
    game['night_actions']['pirate']['result'] = "success"
    await callback.message.edit_text(text=f"👺 Qaroqchi sizdan 10💶 pul so'radi va siz berdingiz")
    

@dp.callback_query(F.data.startswith("professor_"))
async def professor_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = int(callback.data.split("_")[2])
    chat_id = int(callback.data.split("_")[3])
    day = callback.data.split("_")[4]
    
    professor_id = callback.from_user.id
    
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"{ACTIONS.get('professor_action')}\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    
    if not professor_id in game["alive"]:
        return
    mark_night_action_done(game, callback.from_user.id)
    if target_id == "no":
        # hech narsa qilmaslik
        await callback.message.edit_text(
            text=f"{ACTIONS.get('professor_action')}\n\nSiz hech kimni tanlamadingiz.",
            parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=int(chat_id),
            text="🚷 🎩 Professor hech kimga quti bermaslikni afzal ko'rdi."
        )
        return
    
    # ✅ night action saqlash
    game["night_actions"]["professor"]['target_id'] = int(target_id)
    add_visit(game=game, visitor_id=professor_id, house_id=target_id, invisible=False)
    
    await bot.send_message(
        chat_id=int(chat_id),
        text=f"🎩 Professor manzilini aniqlab yo‘lga otlandi...",
    )
    
    target_name = get_first_name_from_players(int(target_id))
    await bot.send_message(
        chat_id=int(target_id),
        text=f"🎩 Professor sizga 3 ta quticha bilan keldi!",
        reply_markup=professor_gift_inline_btn(game_id=int(game_id),day=day)
    )
    
    await callback.message.edit_text(text=f"{ACTIONS.get('professor_action')}\n\nSiz <a href='tg://user?id={target_id}'>{target_name}</a> ni tanladingiz")


@dp.callback_query(F.data.startswith("prof_"))
async def prof_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    parts = callback.data.split("_")
    choose = str(parts[1])
    game_id = int(parts[2])
    day = parts[3]
    professor_id = callback.from_user.id
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text="🎩 Siz kechikdingiz.", parse_mode="HTML")
        return
    if not professor_id in game["alive"]:
        return
    if choose == "die":
        reward = "⚰️ O'lim"
        game["night_actions"]["professor"]['chosen'] = "die"
        mark_night_action_done(game, callback.from_user.id)
    elif choose == "empty":
        reward = "🥡 Bo'sh quti"
        game["night_actions"]["professor"]['chosen'] = "empty"
        mark_night_action_done(game, callback.from_user.id)
        
    else:
        reward = "🥷 Geroydan foydalanish"
        game["night_actions"]["professor"]['chosen'] = "hero"
        mark_night_action_done(game, callback.from_user.id)
    
    await callback.message.edit_text(text=f"🎩 Professor sizga {reward}ni sovg'a qutisidan berdi!")

@dp.callback_query(F.data.startswith("hang_"))
async def hang_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    target_id = callback.data.split("_")[1]
    game_id = callback.data.split("_")[2]
    chat_id = callback.data.split("_")[3]
    day = callback.data.split("_")[4]
    shooter_id = callback.from_user.id
    shooter_name = callback.from_user.first_name
    game = games_state.get(int(game_id))
    if not game:
        return
    game_day = game['meta']['day']
    if not day == str(game_day):
        await callback.message.edit_text(text=f"Aybdorlarni izlash vaqti keldi!\nKimni osishni xohlaysiz?\n\nSiz kechikdingiz.", parse_mode="HTML")
        return
    if target_id == "no":
        await callback.message.edit_text(text=f"Aybdorlarni izlash vaqti keldi!\nKimni osishni xohlaysiz?\n\nSiz hech kimni osmadingiz.")
        await bot.send_message(
            chat_id=chat_id,
            text=f"🚷 <a href='tg://user?id={shooter_id}'>{shooter_name}</a> hech kimni osmaslikni taklif qildi"
        )
        return
    game["day_actions"]['votes'].append(int(target_id))
    mark_hang_done(int(game_id), callback.from_user.id)
    
    
    user_map = game.get("users_map",{})
    user = user_map.get(int(target_id))
    await callback.message.edit_text(text=f"Aybdorlarni izlash vaqti keldi!\nKimni osishni xohlaysiz?\n\nSiz <a href='tg://user?id={target_id}'>{user.get('first_name')}</a> ni tanladingiz")
    await bot.send_message(
        chat_id=chat_id,
        text=f"<a href='tg://user?id={shooter_id}'>{shooter_name}</a> -> <a href='tg://user?id={target_id}'>{user.get('first_name')}</a> ga ovoz berdi"
    )

        
@dp.callback_query(F.data.startswith("con_"))
async def confirm_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    confirmation = str(parts[1])
    target_id = int(parts[2])
    game_id = int(parts[3])
    chat_id = int(parts[4])
    voter_id = callback.from_user.id
    game = games_state.get(int(game_id))
    if not game:
        return
    if not voter_id in game["alive"]:
        if voter_id in game["dead"]:
            await callback.answer(text="❌ O'liklar ovoz bera olmaydi!")
            return
        if voter_id not in game["players"]:
            await callback.answer(text="❌ Siz ushbu o'yinda ishtirok etmayapsiz!")
        return
    if target_id == voter_id:
        await callback.answer(text="❌ O'zingizga ovoz bera olmaysiz!")
        return
    if voter_id == game["night_actions"]["lover_block_target"]:
        await callback.answer(text="❌ Sizni sevgilingiz kutmoqda, ovoz bera olmaysiz!")
        return
    
    if not target_id in game["alive"]:
        return
    if confirmation == "yes":
        if voter_id not in game["day_actions"]["hang_yes"]:
            game["day_actions"]["hang_yes"].append(voter_id)
        else:
            game["day_actions"]["hang_yes"].remove(voter_id)
        if voter_id in game["day_actions"]["hang_no"]:
            game["day_actions"]["hang_no"].remove(voter_id)
        
    else:
        if voter_id not in game["day_actions"]["hang_no"]:
            game["day_actions"]["hang_no"].append(voter_id)
        else:
            game["day_actions"]["hang_no"].remove(voter_id)
        if voter_id in game["day_actions"]["hang_yes"]:
            game["day_actions"]["hang_yes"].remove(voter_id)
    
    mark_confirm_done(int(game_id), voter_id)
    
    
    await callback.answer(text="👍 Ovozingiz qabul qilindi.")
    yes = len(game["day_actions"]["hang_yes"])
    no = len(game["day_actions"]["hang_no"])
    
    await update_hang_votes(voter_id=target_id,game_id=int(game_id),chat_id=chat_id,yes=yes,no=no)
    
    
async def update_hang_votes(voter_id,game_id: int, chat_id: int, yes: int, no: int):
    game = games_state.get(int(game_id))
    if not game:
        return
    msg_id = game['day_actions']['hang_confirm_msg_id']
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=msg_id,
        reply_markup=confirm_hang_inline_btn(voted_user_id=voter_id,game_id=int(game_id),chat_id=chat_id,yes=yes,no=no)
    )
    
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@dp.callback_query(F.data.startswith("pul_"))
async def pul_star_callback(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split("_")
    money_amount = int(parts[1])
    star_amount = int(parts[2])
    user_id = callback.from_user.id

    prices = [
        LabeledPrice(label=f"💶 {money_amount} sotib olish", amount=star_amount)
    ]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="💶 Pul sotib olish",
        description="Sotib olishdan avval hisobingizda yetarlicha stars mavjudligini tekshiring.",
        payload=f"pul_{money_amount}_{star_amount}_{user_id}",
        currency="XTR",
        prices=prices
    )

@dp.callback_query(F.data.startswith("olmos_"))
async def olmos_star_callback(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split("_")
    olmos_amount = int(parts[1])
    star_amount = int(parts[2])
    user_id = callback.from_user.id

    prices = [
        LabeledPrice(label=f"💎 {olmos_amount} sotib olish", amount=star_amount)
    ]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="💎 Olmos sotib olish",
        description="Sotib olishdan avval hisobingizda yetarlicha stars mavjudligini tekshiring.",
        payload=f"olmos_{olmos_amount}_{star_amount}_{user_id}",
        currency="XTR",
        prices=prices
    )
    


    
    
@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    sp = message.successful_payment

    payload = sp.invoice_payload
    total_amount = sp.total_amount
    currency = sp.currency

    try:
        parts = payload.split("_")
        if len(parts) != 4:
            await message.answer("❌ Noto‘g‘ri invoice payload.")
            return

        prefix = parts[0]  # pul yoki olmos
        item_amount = int(parts[1])   # pul/olmos amount
        star_amount = int(parts[2])
        user_id = int(parts[3])
    except:
        await message.answer("❌ Payload parse error.")
        return
    
    if int(user_id)<0:
        group_trials = GroupTrials.objects.filter(group_id=int(user_id)).first()
        if group_trials:
            group_trials.stones += item_amount
            group_trials.save()
        await message.answer(
            f"✅ Olmos xarid qilindi!\n\n"
            f"💎 Olmos: {item_amount}\n"
        )
        return

    # ✅ xavfsizlik
    if message.from_user.id != user_id:
        await message.answer("❌ To‘lov user mos kelmadi.")
        return

    # ✅ real to'lov va kutilgan star amount mos kelishi kerak
    if total_amount != star_amount:
        await message.answer("❌ To‘lov summasi mos kelmadi.")
        return
    
    

    user = User.objects.filter(telegram_id=user_id).first()
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        return
    if prefix == "pul":
        
        await message.answer(
            f"✅ Pul xarid qilindi!\n\n"
            f"💶 Pul: {item_amount}\n"
            f"⭐ Stars: {total_amount} {currency}"
        )
        user.coin += item_amount
        user.save()

    elif prefix == "olmos":
        # add_olmos_user(user_id, item_amount)
        await message.answer(
            f"✅ Olmos xarid qilindi!\n\n"
            f"💎 Olmos: {item_amount}\n"
            f"⭐ Stars: {total_amount} {currency}"
        )
        user.stones += item_amount
        user.save()

    else:
        await message.answer("❌ Noma’lum invoice turi.")
        return
    
    
@dp.callback_query(F.data.startswith("groups"))
async def groups_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    await callback.message.edit_text(
        text="🌐 Guruhlar bo'limi\n\n"
             "Bu yerda siz botimiz qo'llab-quvvatlaydigan rasmiy guruhlar va kanallar ro'yxatini topishingiz mumkin. "
             "Ushbu guruhlar orqali siz yangiliklardan xabardor bo'lishingiz, boshqa foydalanuvchilar bilan muloqot qilishingiz va yordam olishingiz mumkin.",
        parse_mode="HTML",
        reply_markup=groups_inline_btn()
    )
    
    
@dp.callback_query(F.data == "premium_group")
async def premium_group_callback(callback: CallbackQuery):
    await callback.answer()
    page = 1
    limit = 5
    offset = (page - 1) * limit
    total = PremiumGroup.objects.count()
    premium_groups = PremiumGroup.objects.all()[offset:offset + limit]

    total_pages = (total + limit - 1) // limit

    quiz_list = "\n\n".join([
        f"{i + 1}. <a href='{group.link}'>{group.name}</a>\n"
        for i, group in enumerate(premium_groups)
    ])

    await callback.message.edit_text(
        text=f"Premium guruhlar (sahifa {page}/{total_pages}):\n\n{quiz_list}",
        reply_markup=groupes_keyboard(questions=premium_groups, page=page, total=total, per_page=limit)
    )

@dp.callback_query(F.data.startswith("quiz_page:"))
async def quizzes_page_callback(callback_query):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])
    limit = 5
    offset = (page - 1) * limit

    total = PremiumGroup.objects.count()
    total_pages = (total + limit - 1) // limit

    groups = PremiumGroup.objects.all()[offset:offset + limit]

    quiz_list = "\n\n".join([
        f"{i + 1}. <a href='{group.link}'>{group.name}</a>\n"
        for i, group in enumerate(groups)
    ])

    await callback_query.message.edit_text(
        text=f"Mavjud viktorinalar (sahifa {page}/{total_pages}):\n\n{quiz_list}",
        reply_markup=groupes_keyboard(questions=groups, page=page, total=total, per_page=limit)
    )

@dp.callback_query(F.data.startswith("quiz_select:"))
async def quiz_select(callback):
    await callback.answer()
    group_id = callback.data.split(":")[1]
    group = PremiumGroup.objects.get(id=group_id)

    await callback.message.edit_text(
        text=f"🌟 Premium guruhni boshqarish\n\n"
             f"Nomi: {group.name}\n"
             f"Link: {group.link}",
        reply_markup=group_manage_btn(group.id)
    )

@dp.callback_query(F.data == "add_group")
async def add_group(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    await callback.message.edit_text(
        text="⭐ Premium guruh nomini kiriting:",
        reply_markup=back_admin_btn()
    )
    await state.set_state(AddGroupState.waiting_for_group_name)
    
    

@dp.message(AddGroupState.waiting_for_group_name)
async def process_group_name(message: Message, state: FSMContext) -> None:
    group_name = message.text.strip()
    await state.update_data(group_name=group_name)
    await message.answer(
        text="🔗 Premium guruh linkini kiriting:",
        reply_markup=back_admin_btn()
    )
    await state.set_state(AddGroupState.waiting_for_group_link)

@dp.message(AddGroupState.waiting_for_group_link)
async def process_group_link(message: Message, state: FSMContext) -> None:
    group_link = message.text.strip()
    if not group_link.startswith("https://t.me/") and not group_link.startswith("http://t.me/"):
        await message.answer(
            text="❌ Iltimos, to'g'ri guruh linkini kiriting (https://t.me/...)",
            reply_markup=back_admin_btn()
        )
        return
    
    await state.update_data(group_link=group_link)
    
    await message.answer(
        text="💎 Nechta olmos evaziga",
        reply_markup=back_admin_btn()
    )
    await state.set_state(AddGroupState.waiting_for_olmos_amount)
    
    
@dp.message(AddGroupState.waiting_for_olmos_amount)
async def process_olmos_amount(message: Message, state: FSMContext) -> None:
    olmos_amount_text = message.text.strip()
    if not olmos_amount_text.isdigit():
        await message.answer(
            text="❌ Iltimos, to'g'ri olmos miqdorini kiriting (faqat raqamlar)",
            reply_markup=back_admin_btn()
        )
        return
    data = await state.get_data()
    group_name = data.get("group_name")
    group_link = data.get("group_link")
    olmos_amount = int(olmos_amount_text)
    group_id = data.get("group_id")
    
    if group_id:
        group = PremiumGroup.objects.filter(id=group_id).first()
        if group:
            group.name = group_name
            group.link = group_link
            group.stones_for = olmos_amount
            group.save()
            await message.answer(
                text=f"✅ Premium guruh muvaffaqiyatli yangilandi!\n\n"
                     f"Nomi: {group_name}\n"
                     f"Link: {group_link}",
                reply_markup=admin_inline_btn()
            )
            await state.clear()
            return

    PremiumGroup.objects.create(
        name=group_name,
        link=group_link,
        stones_for=olmos_amount
    )

    await message.answer(
        text=f"✅ Premium guruh muvaffaqiyatli qo'shildi!\n\n"
             f"Nomi: {group_name}\n"
             f"Link: {group_link}\n"
             f"Olmos evaziga: {olmos_amount}",
        reply_markup=admin_inline_btn()
    )
    await state.clear()
    

@dp.callback_query(F.data.startswith("manage_"))
async def manage_group(callback: CallbackQuery,state : FSMContext) -> None:
    await callback.answer()
    splited_text = callback.data.split("_")[1]
    group_id = int(splited_text.split(":")[1])
    action = splited_text.split(":")[0]
    
    if action == "edit":
        await state.update_data(group_id=group_id)
        await callback.message.edit_text(
            text="⭐ Yangi premium guruh nomini kiriting:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(AddGroupState.waiting_for_group_name)
        return
    elif action == "delete":
        group = PremiumGroup.objects.filter(id=group_id).first()
        if group:
            group.delete()
            await callback.message.edit_text(
                text="✅ Premium guruh muvaffaqiyatli o'chirildi.",
                reply_markup=admin_inline_btn()
            )
        else:
            await callback.message.edit_text(
                text="❌ Premium guruh topilmadi.",
                reply_markup=admin_inline_btn()
            )
    

@dp.callback_query(F.data.startswith("remove_"))
async def remove_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    action = callback.data.split("_")[1]
    if action == "pul":
        await callback.message.edit_text(
            text="💶 Foydalanuvchidan pul yechib olish uchun telegram id va pulni yonma-yon kiriting:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(SendMoneyState.waiting_money_to_remove)
    elif action == "olmos":
        await callback.message.edit_text(
            text="💎 Foydalanuvchidan olmos yechib olish uchun telegram id va olmosni yonma-yon kiriting:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(SendMoneyState.waiting_olmos_to_remove)
        
@dp.message(SendMoneyState.waiting_money_to_remove)
async def process_send_money(message: Message, state: FSMContext) -> None:
    try:
        telegram_id, amount_str = message.text.strip().split()
        amount = int(amount_str)
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri formatda kiriting: telegram_id pul_miqdori",
            reply_markup=back_admin_btn()
        )
        return
    
        

    user = User.objects.filter(telegram_id=int(telegram_id)).first()
    if not user:
        await message.answer(
            text="❌ Foydalanuvchi topilmadi.",
            reply_markup=back_admin_btn()
        )
        return

    sender = User.objects.filter(telegram_id=message.from_user.id).first()
    if not sender:
        sender = User.objects.create(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name or "NoName",
            username=message.from_user.username or "",
            role="admin"
        )
    user.coin -= amount
    user.save()
    MoneySendHistory.objects.create(
        sender_id = sender.id,
        receiver_id = user.id,
        amount = f"- {amount} 💶"
    )
        

    await message.answer(
        text=f"✅ <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a> foydalanuvchisidan {amount}💶 muvaffaqiyatli yechib olindi.",
        reply_markup=admin_inline_btn(),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=user.telegram_id,
        text=f"Sizdan admin  💶 {amount} pullar yechib oldi."
    )   
    await state.clear()
    

@dp.message(SendMoneyState.waiting_olmos_to_remove)
async def process_send_olmos(message: Message, state: FSMContext) -> None:
    try:
        telegram_id, amount_str = message.text.strip().split()
        amount = int(amount_str)
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri formatda kiriting: telegram_id pul_miqdori",
            reply_markup=back_admin_btn()
        )
        return
    
    
    user = User.objects.filter(telegram_id=int(telegram_id)).first()
    if not user:
        await message.answer(
            text="❌ Foydalanuvchi topilmadi.",
            reply_markup=back_admin_btn()
        )
        return

    user.stones -= amount
    user.save()
    sender = User.objects.filter(telegram_id=message.from_user.id).first()
    if not sender:
        sender = User.objects.create(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name or "NoName",
            username=message.from_user.username or "",
            role="admin"
        )
    MoneySendHistory.objects.create(
        sender_id = sender.id,
        receiver_id = user.id,
        amount = f"- {amount} 💎"
    )

    await message.answer(
        text=f"✅ <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a> foydalanuvchisidan {amount}💎 muvaffaqiyatli yechib olindi.",
        reply_markup=admin_inline_btn(),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=user.telegram_id,
        text= f"Sizdan admin tomonidan 💎 {amount} olmoslar yechib olindi."
    )
    await state.clear()
    
    
        
@dp.callback_query(F.data.startswith("send_"))
async def send_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    action = callback.data.split("_")[1]
    if action == "pul":
        await callback.message.edit_text(
            text="💶 Foydalanuvchiga pul yuborish uchun telegram id va pulni yonma-yon kiriting:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(SendMoneyState.waiting_for_money)
        
        
    elif action == "olmos":
        await callback.message.edit_text(
            text="💎 Foydalanuvchiga olmos yuborish uchun telegram id va olmosni yonma-yon kiriting:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(SendMoneyState.waiting_for_olmos)

@dp.message(SendMoneyState.waiting_for_money)
async def process_send_money(message: Message, state: FSMContext) -> None:
    try:
        telegram_id, amount_str = message.text.strip().split()
        amount = int(amount_str)
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri formatda kiriting: telegram_id pul_miqdori",
            reply_markup=back_admin_btn()
        )
        return
    
        

    user = User.objects.filter(telegram_id=int(telegram_id)).first()
    if not user:
        await message.answer(
            text="❌ Foydalanuvchi topilmadi.",
            reply_markup=back_admin_btn()
        )
        return

    sender = User.objects.filter(telegram_id=message.from_user.id).first()
    if not sender:
        sender = User.objects.create(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name or "NoName",
            username=message.from_user.username or "",
            role="admin"
        )
    user.coin += amount
    user.save()
    MoneySendHistory.objects.create(
        sender_id = sender.id,
        receiver_id = user.id,
        amount = f"{amount} 💶"
    )
        

    await message.answer(
        text=f"✅ <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a> foydalanuvchisiga {amount}💶 muvaffaqiyatli yuborildi.",
        reply_markup=admin_inline_btn(),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=user.telegram_id,
        text=f"Sizga admin tomonidan 💶 {amount} pullar yuborildi."
    )   
    await state.clear()
    
@dp.message(SendMoneyState.waiting_for_olmos)
async def process_send_olmos(message: Message, state: FSMContext) -> None:
    try:
        telegram_id, amount_str = message.text.strip().split()
        amount = int(amount_str)
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri formatda kiriting: telegram_id pul_miqdori",
            reply_markup=back_admin_btn()
        )
        return
    
    
    user = User.objects.filter(telegram_id=int(telegram_id)).first()
    if not user:
        await message.answer(
            text="❌ Foydalanuvchi topilmadi.",
            reply_markup=back_admin_btn()
        )
        return

    user.stones += amount
    user.save()
    sender = User.objects.filter(telegram_id=message.from_user.id).first()
    MoneySendHistory.objects.create(
        sender_id = sender.id,
        receiver_id = user.id,
        amount = f"{amount} 💎"
    )

    await message.answer(
        text=f"✅ <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a> foydalanuvchisiga {amount}💎 muvaffaqiyatli yuborildi.",
        reply_markup=admin_inline_btn(),
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=user.telegram_id,
        text= f"Sizga admin tomonidan 💎 {amount} olmoslar yuborildi."
    )
    await state.clear()
    
    
@dp.callback_query(F.data == "statistics")
async def statistics_callback(callback: CallbackQuery):
    await callback.answer()

    total_users = User.objects.count()
    total_admins = User.objects.filter(role='admin').count()
    total_premium_groups = PremiumGroup.objects.count()
    total_games = Game.objects.count()
    bot_working_in_groups = GroupTrials.objects.count()

    today = timezone.localdate()
    week_start, week_end = get_week_range(today)
    month_start, month_end = get_month_range(today)

    active_player_row = (
        MostActiveUser.objects
        .values("user")
        .annotate(total_played=Sum("games_played"))
        .order_by("-total_played")
        .first()
    )

    most_wins_all_time_row = (
        MostActiveUser.objects
        .values("user")
        .annotate(total_win=Sum("games_win"))
        .order_by("-total_win")
        .first()
    )

    daily_top_row = (
        MostActiveUser.objects
        .filter(created_datetime__date=today)
        .values("user")
        .annotate(total_win=Sum("games_win"))
        .order_by("-total_win")
        .first()
    )

    weekly_top_row = (
        MostActiveUser.objects
        .filter(created_datetime__date__gte=week_start, created_datetime__date__lt=week_end)
        .values("user")
        .annotate(total_win=Sum("games_win"))
        .order_by("-total_win")
        .first()
    )

    monthly_top_row = (
        MostActiveUser.objects
        .filter(created_datetime__date__gte=month_start, created_datetime__date__lt=month_end)
        .values("user")
        .annotate(total_win=Sum("games_win"))
        .order_by("-total_win")
        .first()
    )

    user_ids = set()
    for row in [active_player_row, most_wins_all_time_row, daily_top_row, weekly_top_row, monthly_top_row]:
        if row:
            user_ids.add(row["user"])

    users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    active = ""
    if active_player_row and active_player_row.get("total_played"):
        u = users_map.get(active_player_row["user"])
        if u:
            active = (
                f"\n🏅 Eng faol o'yinchi: "
                f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"
                f" ({active_player_row['total_played']} o'yin)"
            )

    most_wins_text = ""
    if most_wins_all_time_row and most_wins_all_time_row.get("total_win"):
        u = users_map.get(most_wins_all_time_row["user"])
        if u:
            most_wins_text = (
                f"🏆 Eng ko'p g'alaba (umumiy): "
                f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"
                f" ({most_wins_all_time_row['total_win']} g'alaba)\n"
            )

    daily_text = ""
    if daily_top_row and daily_top_row.get("total_win"):
        u = users_map.get(daily_top_row["user"])
        if u:
            daily_text = (
                f"📅 Kunlik top: "
                f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"
                f" ({daily_top_row['total_win']} g'alaba)\n"
            )

    weekly_text = ""
    if weekly_top_row and weekly_top_row.get("total_win"):
        u = users_map.get(weekly_top_row["user"])
        if u:
            weekly_text = (
                f"🗓 Haftalik top: "
                f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"
                f" ({weekly_top_row['total_win']} g'alaba)\n"
            )

    monthly_text = ""
    if monthly_top_row and monthly_top_row.get("total_win"):
        u = users_map.get(monthly_top_row["user"])
        if u:
            monthly_text = (
                f"🗓 Oylik top: "
                f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"
                f" ({monthly_top_row['total_win']} g'alaba)\n"
            )

    await callback.message.edit_text(
        text=(
            f"📊 Bot Statistikasi\n\n"
            f"👥 Foydalanuvchilar soni: {total_users}\n"
            f"🛡️ Adminlar soni: {total_admins}\n"
            f"🌟 Premium guruhlar soni: {total_premium_groups}\n"
            f"🤖 Bot ishlayotgan guruhlar soni: {bot_working_in_groups}\n"
            f"🎲 O'yinlar soni: {total_games}\n\n"
            f"{most_wins_text}"
            f"{daily_text}"
            f"{weekly_text}"
            f"{monthly_text}"
            f"{active}"
        ),
        parse_mode="HTML",
        reply_markup=admin_inline_btn(),
    )    
@dp.callback_query(F.data.startswith("change_"))
async def change_money_cost_handler(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    action = callback.data.split("_")[1]
    if action == "money":
        await callback.message.edit_text(
            text="💶 Yangi pul sotib olish narxini kiriting:",
            reply_markup=change_money_cost()
        )
        
    elif action == "stone":
        await callback.message.edit_text(
            text="💎 Yangi olmos sotib olish narxini kiriting:",
            reply_markup=change_stones_cost()
        )
        

def format_money_prices(json_text: str) -> str:
    data = json.loads(json_text)
    items = sorted(((int(k), int(v)) for k, v in data.items()), key=lambda x: x[0])

    text = "💶 Pul → ⭐ Stars narxlari\n\n"
    for money, stars in items:
        text += f"• {money:,} so'm  →  ⭐ {stars}\n"
    return text


def format_stone_prices(json_text: str) -> str:
    data = json.loads(json_text)
    items = sorted(((int(k), int(v)) for k, v in data.items()), key=lambda x: x[0])

    text = "💎 Olmos → ⭐ Stars narxlari\n\n"
    for stone, stars in items:
        text += f"• {stone:,} 💎  →  ⭐ {stars}\n"
    return text


@dp.callback_query(F.data.startswith("aziz_"))
async def ozgar_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    action = callback.data.split("_")[1]
    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    if action == "money":
        await callback.message.edit_text(
            text=(
                "💶 Yangi pul sotib olish narxini kiriting:\n\n"
                f"📌 Oldingi narxlar:\n\n{cost.money_in_money}"
            ),
            reply_markup=back_admin_btn()
        )
        await state.set_state(ChangeMoneyCostState.waiting_for_money_cost)

    elif action == "star":
        try:
            formatted = format_money_prices(cost.money_in_star)
        except Exception:
            formatted = cost.money_in_star or "—"

        await callback.message.edit_text(
            text=(
                "💶 Yangi pul sotib olish narxini ⭐ starsda kiriting:\n\n"
                f"📌 Oldingi narxlar:\n{formatted}\n\n"
                "✍️ Namuna (JSON format):\n"
                '{"1000":7,"10000":77,"50000":340,"100000":680}'
            ),
            reply_markup=back_admin_btn(),
            parse_mode="Markdown"
        )
        await state.set_state(ChangeMoneyCostState.waiting_for_star_cost)


@dp.callback_query(F.data.startswith("ozgar_"))
async def aziz_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    action = callback.data.split("_")[1]
    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    if action == "money":
        await callback.message.edit_text(
            text=(
                "💎 Yangi olmos sotib olish narxini kiriting\n\n"
                f"📌 Eski narxlar:\n\n{cost.stone_in_money}"
            ),
            reply_markup=back_admin_btn()
        )
        await state.set_state(ChangeStoneCostState.waiting_for_money_cost)

    elif action == "star":
        try:
            formatted = format_stone_prices(cost.stone_in_star)
        except Exception:
            formatted = cost.stone_in_star or "—"

        await callback.message.edit_text(
            text=(
                "💎 Yangi olmos sotib olish narxini ⭐ starsda kiriting\n\n"
                f"📌 Oldingi narxlar:\n{formatted}\n\n"
                "✍️ Namuna (JSON format):\n"
                '{"1":7,"10":68,"30":185,"50":237,"70":382,"100":513}'
            ),
            reply_markup=back_admin_btn(),
            parse_mode="Markdown"
        )
        await state.set_state(ChangeStoneCostState.waiting_for_star_cost)


@dp.message(ChangeMoneyCostState.waiting_for_money_cost)
async def process_change_money_cost(message: Message, state: FSMContext) -> None:
    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    cost.money_in_money = message.text.strip()
    cost.save()

    await message.answer(
        text=(
            "✅ Pul sotib olish narxi muvaffaqiyatli o'zgartirildi.\n\n"
            f"Yangi narxlar:\n\n{cost.money_in_money}"
        ),
        reply_markup=admin_inline_btn()
    )
    await state.clear()


@dp.message(ChangeMoneyCostState.waiting_for_star_cost)
async def process_change_money_star_cost(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()

    try:
        formatted = format_money_prices(raw)
    except Exception:
        await message.answer(
            "❌ Format xato!\n\nJSON ko‘rinishda yuboring.\nMasalan:\n"
            '{"1000":7,"10000":77,"50000":340,"100000":680}'
        )
        return

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    cost.money_in_star = raw
    cost.save()

    await message.answer(
        text=f"✅ Pul sotib olish narxi muvaffaqiyatli o'zgartirildi.\n\n{formatted}",
        reply_markup=admin_inline_btn(),
        parse_mode="Markdown"
    )
    await state.clear()


@dp.message(ChangeStoneCostState.waiting_for_money_cost)
async def process_change_stone_money_cost(message: Message, state: FSMContext) -> None:
    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    cost.stone_in_money = message.text.strip()
    cost.save()

    await message.answer(
        text=(
            "✅ Olmos sotib olish narxi muvaffaqiyatli o'zgartirildi.\n\n"
            f"Yangi narxlar:\n\n{cost.stone_in_money}"
        ),
        reply_markup=admin_inline_btn()
    )
    await state.clear()


@dp.message(ChangeStoneCostState.waiting_for_star_cost)
async def process_change_stone_star_cost(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()

    try:
        data = json.loads(raw)

        if not isinstance(data, dict):
            await message.answer(
                "❌ Noto'g'ri format!\n\nJSON object yuborishingiz kerak.\nNamuna:\n"
                '{"1":7,"10":68,"30":185,"50":237,"70":382,"100":513}'
            )
            return

        for k, v in data.items():
            int(k)
            int(v)

        formatted = format_stone_prices(raw)

    except Exception:
        await message.answer(
            "❌ JSON format xato!\n\nNamuna:\n"
            '{"1":7,"10":68,"30":185,"50":237,"70":382,"100":513}'
        )
        return

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    cost.stone_in_star = raw
    cost.save()

    await message.answer(
        text=(
            "✅ Olmos sotib olish narxi muvaffaqiyatli (⭐ starslarda) o'zgartirildi.\n\n"
            f"{formatted}"
        ),
        reply_markup=admin_inline_btn(),
        parse_mode="Markdown"
    )
    await state.clear()


@dp.callback_query(F.data == "cases")
async def case_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(None)
    await callback.message.edit_text(
        text= ("📦 Quti bo'limi\n\n"
            "💰 Pulli sandiq – ichida turli xildagi pul xazinalari yashiringan\n"
            "(💶 900 dan 💶 2000 gacha). Narxi: 💎 1 \n\n"
            "💠 Olmosli sandiq – sirli olmoslar bilan to‘la, ichidan 4 dan 12 tagacha olmos chiqishi mumkin. Narxi: 💶 10 000 \n\n"
            "⭐️ Vip user – olmosli sandiqni cheklanmagan miqdorda ochish imkoniyati, oy oxirigacha amal qiladi. Eng so‘nggi darajadagi imkoniyat! Narxi: 💎 20 \n\n"
            "Oddiy userdan farqi: ⭐️ Vip user har bitta sandiq ochganiga 💶 10 000 to'laydi oddiy user 1 oyda faqat 1 marta 💶 10 000 sarflab ocha oladi"),
        parse_mode="HTML",
        reply_markup=case_inline_btn()
    )
    
    
@dp.callback_query(F.data.startswith("case_"))
async def case_buy_callback(callback: CallbackQuery):
    case_type = callback.data.split("_")[1]
    user = User.objects.filter(telegram_id=callback.from_user.id).first()
    if not user:
        user = User.objects.create(
            telegram_id=callback.from_user.id,
            first_name=callback.from_user.first_name or "NoName",
            username=callback.from_user.username or "",
            role="user"
        )
    case_opened = CasesOpened.objects.filter(user_id=user.id).first()
    if case_type == "money":
        await callback.message.edit_text(
            text="💰 Pulli sandiq – ichidan turli miqdordagi pul tushishi mumkin (💶 900 dan 💶 2000 gacha). Narxi: 💎 1\n\n1 dan 10 gacha bo‘lgan sonlardan birini tanlang – har birida o‘ziga xos yutuq sizni kutmoqda!",
            reply_markup=money_case()
        )
    elif case_type == "stone":
        if not user.is_vip:
            if case_opened:
                last_opened = case_opened.modified_datetime

                # timezone muammosiz bo'lishi uchun UTC ishlatamiz
                now = datetime.datetime.utcnow()

                # ✅ month check
                if last_opened.year == now.year and last_opened.month == now.month:
                    await callback.answer(
                        "❌ Siz bu oy pulli sandiqni ochib bo'lgansiz. Keyingi oy yana urinib ko'ring."
                    )
                    return
        await callback.message.edit_text(
            text="💠 Olmosli sandiq — ichidan 4 dan 12 gacha bo‘lgan turli miqdordagi olmoslar tushishi mumkin.\nNarxi: 💶 10 000\n\n1 dan 10 gacha bo‘lgan sonlardan bittasini tanlashingiz mumkin, har birida yutuq bor:",
            reply_markup=stone_case()
        )
    elif case_type == "vip":
        if user.is_vip:
            await callback.answer("❌ Siz allaqachon VIP usersiz.")
            return
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.")
            return
        if user.stones < 20:
            await callback.answer("❌ Sizda yetarli olmos yo'q.")
            return
        user.stones -= 20
        user.is_vip = True
        user.save()
        await callback.message.edit_text("✅ Siz muvaffaqiyatli VIP user bo'ldingiz! Endi siz cheklanmagan miqdorda olmosli sandiq ochishingiz mumkin.",reply_markup=back_btn())
        
        
@dp.callback_query(F.data.startswith("open_"))
async def open_case_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    case_type = parts[1]
    reward = int(parts[2])
    user_id = callback.from_user.id
    user = User.objects.filter(telegram_id=user_id).first()
    if not user:
        user = User.objects.create(
            telegram_id=user_id,
            first_name=callback.from_user.first_name or "NoName",
            username=callback.from_user.username or "",
            role="user"
        )
    if case_type == "money":
        if user.stones < 1:
            await callback.answer("❌ Sizda yetarli olmos yo'q.")
            return
        user.stones -= 1
        user.coin += reward
        user.save()
        await callback.message.edit_text(f"✅ Siz pulli sandiqni ochdingiz va ichidan 💶 {reward} chiqdi!",reply_markup=back_btn())
    elif case_type == "stone":
        if user.coin < 10000:
            await callback.answer("❌ Sizda yetarli pul yo'q.")
            return
        user.coin -= 10000
        user.stones += reward
        user.save()
        await callback.message.edit_text(f"✅ Siz olmosli sandiqni ochdingiz va ichidan 💎 {reward} chiqdi!",reply_markup=back_btn())
        case_opened = CasesOpened.objects.filter(user_id=user.id).first()
        if not case_opened:
            case_opened = CasesOpened.objects.create(user_id=user.id)
            return
        case_opened.modified_datetime = datetime.datetime.utcnow()
        case_opened.save()
        

async def begin_instance_callback(message: Message,chat_id):
    await message.answer(
        text="🛠️ Yangi o'yinni sozlash uchun quyidagi tugmalardan foydalaning.\n\n🔢 O'yinchilar to'lganda boshlash - qachonki ro'yxatdan o'tganlar siz kiritgan songa yetsagina o'yin boshlanadi\nMasalan 20,25,30 guruh activiga qarab\n\n⏱ Belgilangan vaqtdan so'ng boshlash - O'yin belgilangan vaqtdan so'ng avtomatik boshlanadi\nVaqtni sekundlarda yozing\n\n🔁 O'yin tugagach auto boshlash - Eski o'yin tugagandan so'ng avtomatik boshlanadi",
        reply_markup=begin_instance_inline_btn(chat_id=chat_id)
    )
    
@dp.callback_query(F.data.startswith("begin_"))
async def begin_new_instance_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    action = parts[1]
    chat_id = int(parts[2])
    if action == "instance":
        await state.update_data(action = "instance")
        await state.update_data(chat_id=chat_id)
        await callback.message.edit_text(
            text="🚀 Yangi o'yinni ishtirokchilar to'lganda boshlash uchun sonini kiriting:",
            reply_markup=back_btn()
        )
    elif action == "time":
        await state.update_data(action = "time")
        await state.update_data(chat_id=chat_id)
        await callback.message.edit_text(
            text="🚀 Yangi o'yinni boshlash vaqtini kiriting (soniyalarda):",
            reply_markup=back_btn()
        )
    elif action == "auto":
        game_settings = GameSettings.objects.filter(group_id=chat_id).first()
        if game_settings and not game_settings.begin_after_end:
            await callback.message.edit_text(
                text="✅ O'yin avtomatik ravishda oldingi o'yin tugagandan so'ng boshlanishi yoqildi.",   
                reply_markup=main_inline_btn()
            )
            game_settings.begin_after_end = True
        else:
            game_settings.begin_after_end = False
            await callback.message.edit_text(
                text="❌ O'yin avtomatik ravishda oldingi o'yin tugagandan so'ng boshlanishi o'chirildi.",   
                reply_markup=main_inline_btn()
            )
        game_settings.save()
        return
    await state.set_state(BeginInstanceState.waiting_for_instant_time)
        
        
@dp.message(BeginInstanceState.waiting_for_instant_time)
async def process_begin_instant_count(message: Message, state: FSMContext) -> None:
    try:
        count = int(message.text.strip())
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri son kiriting:",
            reply_markup=back_btn()
        )
        return
    data = await state.get_data()
    action = data.get("action")
    chat_id = data.get("chat_id")
    game_settings = GameSettings.objects.filter(group_id=chat_id).first()
    if action == "instance":
        if count < 4 or count > 30:
            await message.answer(
                text="❌ Iltimos, 4 dan 30 gacha bo'lgan son kiriting:",
                reply_markup=back_btn()
            )
            return
        game_settings.begin_instance = True
        game_settings.number_of_players = count
        await message.answer(f"✅ Yangi o'yin ishtirokchilar soni {count} ga o'rnatildi.",reply_markup=main_inline_btn())
    elif action == "time":
        game_settings.begin_instance = False
        game_settings.begin_instance_time = count
        await message.answer(f"✅ Yangi o'yin boshlanish vaqti {count} soniyaga o'rnatildi.",reply_markup=main_inline_btn())
    game_settings.save()
    await state.clear()
    

    
@dp.callback_query(F.data == "trial")
async def trial_callback(callback: CallbackQuery):
    await callback.answer()
    page = 1
    limit = 5
    offset = (page - 1) * limit
    groupes = GroupTrials.objects.all()[offset:offset + limit]
    total = GroupTrials.objects.count()
    total_pages = (total + limit - 1) // limit
    
    
    group_list = "\n".join([
    f"{i+1}. <a href='{group.group_username}'>{group.group_name}</a>"
    if group.group_username
    else f"{i+1}. {group.group_name}"
    for i, group in enumerate(groupes)
])

    \
    await callback.message.edit_text(
        text=f"Obunadagi guruhlar (sahifa {page}/{total_pages}):\n\n{group_list}",
        reply_markup=trial_groupes_keyboard(questions=groupes, page=page, total=total, per_page=limit))
    
@dp.callback_query(F.data.startswith("olga_page:"))
async def quizzes_page_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])
    limit = 5
    offset = (page - 1) * limit

    total = PremiumGroup.objects.count()
    total_pages = (total + limit - 1) // limit

    groups = GroupTrials.objects.all()[offset:offset + limit]

    group_list = "\n".join([
    f"{i+1}. <a href='{group.group_username}'>{group.group_name}</a>"
    if group.group_username
    else f"{i+1}. {group.group_name}"
    for i, group in enumerate(groups)
])

    
    await callback_query.message.edit_text(
        text=f"Obunadagi guruhlar (sahifa {page}/{total_pages}):\n\n{group_list}",
        reply_markup=trial_groupes_keyboard(questions=groups, page=page, total=total, per_page=limit))
    
@dp.callback_query(F.data.startswith("olga_select:"))
async def quiz_select(callback):
    await callback.answer()
    group_id = callback.data.split(":")[1]
    group = GroupTrials.objects.get(id=group_id)

    link_text = f"{group.group_username}" if group.group_username else "Link mavjud emas"

    await callback.message.edit_text(
    text=(
        f"🌟 Obunadagi guruhni boshqarish\n\n"
        f"Nomi: {group.group_name}\n"
        f"Link: {link_text}\n"
        f"Obuna tugash sanasi: {group.end_date.strftime('%Y-%m-%d')}\n"
    ),
    reply_markup=trial_group_manage_btn(group.id)
)

@dp.callback_query(F.data.startswith("add_"))
async def group_money_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    currency = callback.data.split("_")[1]
    group_id = int(callback.data.split("_")[2])
    if currency == "pul":
        await state.update_data(action = "pul", group_id=group_id)
        await callback.message.edit_text(
        text="Guruhga jo'natmoqchi bo'lgan pulingiz miqdorini kiriting:",
        reply_markup=back_btn("groups")
        )
    elif currency == "stone":
        await state.update_data(action = "stone", group_id=group_id)
        await callback.message.edit_text(
        text="Guruhga jo'natmoqchi bo'lgan olmosingiz miqdorini kiriting:",
        reply_markup=back_btn("groups")
        )
    
    await state.set_state(ExtendGroupState.waiting_for_amount)
    
@dp.message(ExtendGroupState.waiting_for_amount)
async def process_group_money(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    action = data.get("action")
    group_id = int(data.get("group_id"))
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer(
            text="❌ Iltimos, to'g'ri son kiriting:",
            reply_markup=back_btn("groups")
        )
        return
    group = GroupTrials.objects.filter(id=group_id).first()
    if not group:
        await message.answer(
            text="❌ Guruh topilmadi.",
            reply_markup=admin_inline_btn()
        )
        await state.clear()
        return
    if action == "pul":
        group.coins += amount
        group.save()
        await message.answer(
            text=f"✅ Guruhga hisobiga 💶 {amount} qo'shildi.",
            reply_markup=admin_inline_btn()
        )
    elif action == "stone":
        group.stones += amount
        group.save()
        await message.answer(
            text=f"✅ Guruhga hisobiga 💎 {amount} qo'shildi.",
            reply_markup=admin_inline_btn()
        )
    await state.clear()
            
@dp.callback_query(F.data.startswith("extend:"))
async def extend_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    group_id = callback.data.split(":")[1]
    await callback.message.edit_text(
        text="⏳ Obuna muddatini uzaytirish uchun obuna tugash sanasini (YYYY-MM-DD) kiriting:",
        reply_markup=back_btn("groups")
    )
    await state.update_data(group_id=group_id)
    await state.set_state(ExtendGroupState.waiting_for_extend_info)
    

@dp.message(ExtendGroupState.waiting_for_extend_info)
async def process_extend_info(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    group_id = data.get("group_id")
    text = message.text.strip()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        await message.answer(
            text="❌ Iltimos, sanani to'g'ri formatda kiriting (YYYY-MM-DD):",
            reply_markup=back_btn("groups")
        )
        return
    extend_date = datetime.datetime.strptime(text, '%Y-%m-%d').date()
    group = GroupTrials.objects.filter(id=group_id).first()
    if not group:
        await message.answer(
            text="❌ Guruh topilmadi.",
            reply_markup=back_btn("groups")
        )
        await state.clear()
        return
    group.trial_end_date = extend_date
    group.save()
    await message.answer(
        text=f"✅ Obuna muddati muvaffaqiyatli uzaytirildi. Yangi tugash sanasi: {extend_date}",
        reply_markup=admin_inline_btn()
    )
    
@dp.callback_query(F.data == "transfer_history")
async def transfer_history_callback(callback: CallbackQuery):
    await callback.answer()
    page = 1
    limit = 10
    offset = (page - 1) * limit
    transfers = MoneySendHistory.objects.all().order_by('-created_datetime')[offset:offset + limit]
    total = MoneySendHistory.objects.count()
    total_pages = (total + limit - 1) // limit

    if transfers:
        history_text = f"💼 Pul o'tkazmalari (sahifa {page}/{total_pages}):\n\n"
        for transfer in transfers:
            history_text += (
                f"👮 Jonatuvchi Admin: <a href='tg://user?id={transfer.sender.telegram_id}'>{transfer.sender.first_name}</a>\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={transfer.receiver.telegram_id}'>{transfer.receiver.first_name}</a>\n"
                f"💶 Miqdor: {transfer.amount} \n"
                f"🕒 Sana: {transfer.created_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

        await callback.message.edit_text(
            text=history_text,
            reply_markup=history_groupes_keyboard(page=page, total=total, per_page=limit)
        )
    else:
        await callback.message.edit_text("❌ Hech qanday o'tkazmalar topilmadi.", reply_markup=admin_inline_btn())
        return
    
    
@dp.callback_query(F.data.startswith("history_page:"))
async def quizzes_page_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])
    limit = 10
    offset = (page - 1) * limit
    transfers = MoneySendHistory.objects.all().order_by('-created_datetime')[offset:offset + limit]
    total = MoneySendHistory.objects.count()
    total_pages = (total + limit - 1) // limit

    if transfers:
        history_text = f"💼 Pul o'tkazmalari (sahifa {page}/{total_pages}):\n\n"
        for transfer in transfers:
            history_text += (
                f"👮 Jonatuvchi Admin: <a href='tg://user?id={transfer.sender.telegram_id}'>{transfer.sender.first_name}</a>\n"
                f"👤 Foydalanuvchi: <a href='tg://user?id={transfer.receiver.telegram_id}'>{transfer.receiver.first_name}</a>\n"
                f"💶 Miqdor: {transfer.amount} \n"
                f"🕒 Sana: {transfer.created_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

        await callback_query.message.edit_text(
            text=history_text,
            reply_markup=history_groupes_keyboard(page=page, total=total, per_page=limit)
        )
    else:
        await callback_query.message.edit_text("❌ Hech qanday o'tkazmalar topilmadi.", reply_markup=admin_inline_btn())
        return
    
@dp.callback_query(F.data == "take_stone")
async def take_stone(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    data = stones_taken.get(chat_id)
    if not data:
        await callback.answer("❌ Hozir tarqatish yo'q.", show_alert=True)
        return

    limit = data["limit"]
    taken = data["taken"]
    sender = data["creator"]

    if user_id in taken:
        await callback.answer("⚠️ Siz allaqachon olgansiz!", show_alert=True)
        return

    if len(taken) >= limit:
        await callback.answer("❌ Olmos tugadi!", show_alert=True)
        return

    taken.append(user_id)
    user_taker = User.objects.filter(telegram_id=user_id).first()
    sender = User.objects.filter(telegram_id=int(sender)).first()
    if not user_taker:
        user_taker = User.objects.create(
            telegram_id=user_id, 
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )
    users_qs = User.objects.filter(telegram_id__in=taken)
    
    
    taken_text = ""
    for i, user in enumerate(users_qs, start=1):
        taken_text += f"\n{i}. 💎 <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a>"

    text = (
         f"💎 <a href='tg://user?id={sender.telegram_id}'>{sender.first_name}</a> tomonidan {limit} ta olmos guruhga jo'natildi!\n"
        f"{taken_text}"
    )

    if len(taken) >= limit:
        await callback.message.edit_text(text, reply_markup=None, parse_mode="HTML")
        stones_taken.pop(chat_id, None)
    else:
        await callback.message.edit_text(text, reply_markup=take_stone_btn(), parse_mode="HTML")
    user_taker.stones += 1
    user_taker.save()
    await callback.answer("✅ 1 ta olmos oldingiz!")


@dp.callback_query(F.data == "take_gsend_stone")
async def take_gsend_stone(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    data = gsend_taken.get(chat_id)
    if not data:
        await callback.answer("❌ Hozir tarqatish yo'q.", show_alert=True)
        return
    
    game_db = Game.objects.filter(chat_id=chat_id, is_active=True).first()
    if not game_db:
        return
    
    game = games_state.get(game_db.id)
    players = game.get("players") if game else None

    if not players:
        await callback.answer("❌ O‘yin topilmadi.", show_alert=True)
        return

    if str(user_id) not in players and user_id not in players:
        await callback.answer("❌ Siz o‘yinda yo‘qsiz. Faqat o'yindagilar oladi!", show_alert=True)
        return

    limit = data["limit"]
    taken = data["taken"]
    sender = data["creator"]
    sender = User.objects.filter(telegram_id=int(sender)).first()
    

    if user_id in taken:
        await callback.answer("⚠️ Siz allaqachon olgansiz!", show_alert=True)
        return

    if len(taken) >= limit:
        await callback.answer("❌ Olmos tugadi!", show_alert=True)
        return

    taken.append(user_id)
    user_taker = User.objects.filter(telegram_id=user_id).first()
    if not user_taker:
        user_taker = User.objects.create(
            telegram_id=user_id, 
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )

    users_qs = User.objects.filter(telegram_id__in=taken)
    taken_text = ""
    for i, user in enumerate(users_qs, start=1):
        taken_text += f"\n {i}. 💎 <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a>"

    text = (
        f"💎 <a href='tg://user?id={sender.telegram_id}'>{sender.first_name}</a> tomonidan {limit} ta olmos o‘yindagilarga jo'natildi!\n"
        f"{taken_text}"
    )

    if len(taken) >= limit:
        await callback.message.edit_text(text, reply_markup=None, parse_mode="HTML")
        gsend_taken.pop(chat_id, None)
    else:
        await callback.message.edit_text(text, reply_markup=take_gsend_stone_btn(), parse_mode="HTML")
    user_taker.stones += 1
    user_taker.save()
    await callback.answer("✅ 1 ta olmos oldingiz!")
    

@dp.callback_query(F.data == "giveaway_join")
async def giveaway_join(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    gw = giveaways.get(chat_id)
    if not gw:
        await callback.answer("❌ Giveaway yo'q yoki tugagan.", show_alert=True)
        return

    if time.time() >= gw["end_at"]:
        await callback.answer("❌ Giveaway tugagan.", show_alert=True)
        return

    if user_id in gw["members"]:
        await callback.answer("⚠️ Siz allaqachon qo‘shilgansiz!", show_alert=True)
        return
    user_taker = User.objects.filter(telegram_id=user_id).first()
    if not user_taker:
        user_taker = User.objects.create(
            telegram_id=user_id, 
            first_name=callback.from_user.first_name,
            username=callback.from_user.username
        )

    gw["members"].add(user_id)
    users_qs = User.objects.filter(telegram_id__in=gw["members"])
    end_at = gw["end_at"] - time.time()
    minut = int(end_at // 60)
    second = int(end_at % 60)
    text = (
        f"💎 <b>Giveaway davom etmoqda!</b>\n\n"
        f"💎 Mukofot: <b>{gw['amount']} olmos</b>\n"
        f"⏳ Tugash vaqti: <b>{minut} minut {second} sekund</b>\n\n"
        f"✅ <b>Qatnashchilar:</b>\n\n"
        + "\n".join([
            f"{i + 1}. <a href='tg://user?id={user.telegram_id}'>{user.first_name}</a>"
            for i, user in enumerate(users_qs)
        ]
    )
    )
    await callback.message.edit_text(text, reply_markup=giveaway_join_btn(), parse_mode="HTML")
    await callback.answer("✅ Giveawayga qo‘shildingiz!")




@dp.callback_query(F.data == "user_talk")
async def user_talk(callback_query: CallbackQuery,state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer(text="💬 Suhbat uchun foydalanuvchi ID sini yuboring:",reply_markup=back_admin_btn())
    await state.set_state(QuestionState.user_id)
    
    

@dp.message(StateFilter(QuestionState.user_id))
async def process_user_id(message: Message, state: FSMContext) -> None:
    tg_id_text = message.text.strip() if message.text else None
    if not tg_id_text or not tg_id_text.isdigit():
        await message.answer("❗️ Iltimos, foydalanuvchi ID sini to'g'ri formatda yuboring.",reply_markup=back_admin_btn())
        return

    tg_id = int(tg_id_text)
    await state.update_data(user_talk_id=tg_id)
    if not User.objects.filter(telegram_id=tg_id).exists():
        await message.answer("❗️ Bunday ID li foydalanuvchi topilmadi. Iltimos, to'g'ri ID ni kiriting.",reply_markup=back_admin_btn())
        return
    await message.answer(
        text=f"💬 Foydalanuvchi (ID: {tg_id}) bilan suhbatni boshlang. Sizning xabaringiz ushbu foydalanuvchiga yuboriladi.",reply_markup=back_admin_btn()
    )
    await state.set_state(QuestionState.user_talk)

@dp.message(StateFilter(QuestionState.user_talk))
async def process_user_talk(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("user_talk_id")
    msg_id = message.message_id

    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"💬 Admindan xabar:\n\n{message.text}",
            reply_markup=answer_admin(message.from_user.id, msg_id)
        )
        await message.answer("✅ Xabaringiz foydalanuvchiga yuborildi.\nYana gapingiz bolsa yozing",reply_markup=end_talk_keyboard())
    except Exception as e:
        await message.answer(f"❗️ Xatolik yuz berdi: {str(e)}")



@dp.callback_query(F.data.startswith("answer_admin_"))
async def answer_from_admin(callback_query: CallbackQuery,state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(None)
    tg_id = int(callback_query.data.split("_")[-2])
    msg_id = int(callback_query.data.split("_")[-1])
    await callback_query.message.answer(
        text=f"💬 Javobingizni yozing. Sizning habaringiz adminga yetkaziladi"
    )
    await state.update_data(answer_to_admin_id=tg_id, answer_to_admin_msg_id=msg_id)
    
    await state.set_state(QuestionState.user_answer)
    
    
@dp.message(StateFilter(QuestionState.user_answer))
async def process_answer_to_admin(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("answer_to_admin_id")
    msg_id = data.get("answer_to_admin_msg_id")

    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"💬 Foydalanuvchidan javob:\n\n{message.text}",
            reply_to_message_id=msg_id
        )
        await message.answer("✅ Javobingiz adminga yuborildi.")
    except Exception as e:
        await message.answer(f"❗️ Xatolik yuz berdi: {str(e)}")
    await state.clear()
    
    
@dp.callback_query(F.data == "end_talk")
async def end_talk(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer("💬 Suhbat yakunlandi.",reply_markup=admin_inline_btn())
    
    
    
@dp.callback_query(F.data == "broadcast_message")
async def broadcast_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer("📢 Iltimos, bot foydalanuvchilariga jo'natiladigan xabar matnini kiriting:",reply_markup=back_admin_btn())
    await state.set_state(Register.every_one)
    
@dp.message(StateFilter(Register.every_one))
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else None
    if not text:
        await message.answer("❗️ Iltimos, xabar matnini kiriting.")
        return

    users = User.objects.all()
    success_count = 0
    fail_count = 0

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"📢 Botdan umumiy xabar:\n\n{text}"
            )
            success_count += 1
        except Exception:
            fail_count += 1

    await message.answer(f"📢 Xabar yuborildi.\nMuvaffaqiyatli: {success_count}\nMuvaffaqiyatsiz: {fail_count}",reply_markup=admin_inline_btn())
    await state.clear()


@dp.callback_query(F.data == "close")
async def close_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    
    
@dp.callback_query(F.data.startswith("prem_"))
async def premium_manage_callback(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])
    chat_id = int(callback.data.split("_")[2])
    game_trial = GroupTrials.objects.filter(group_id=chat_id).first()
    if not game_trial:
        await callback.answer("❌ Guruh topilmadi.")
        return
    game_trial.premium_stones = amount
    game_trial.stones -= amount
    game_trial.prem_ends_date = timezone.now() + timedelta(days=14)
    game_trial.save()
    await callback.answer(text=f"✅ Guruhga {amount} olmosli premium berildi.", show_alert=True)
    PremiumGroup.objects.update_or_create(
        name = game_trial.group_name,
        group_id = chat_id,
        defaults={
            "link": game_trial.group_username,
            "ends_date": timezone.now() + timedelta(days=14),
            "stones_for": amount
        }
    )
        
        
    

@dp.callback_query(F.data == "privacy")
async def privacy_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Kirish so'zlarni o'zgartirish uchun quyidagi tugmalardan foydalaning:",
        reply_markup=privacy_inline_btn()
    )
    
@dp.callback_query(F.data.startswith("credentials_"))
async def credentials_callback(callback: CallbackQuery,state: FSMContext) -> None:
    await callback.answer()
    action = callback.data.split("_")[1]
    await state.update_data(action=action)
    if action == "password":
        await callback.message.edit_text(
            text="🔐 Iltimos, yangi parolini so'zlarni yuboring:",
            reply_markup=back_admin_btn()
        )
        await state.set_state(CredentialsState.waiting_for_new_password)
    elif action == "username":
        await callback.message.edit_text(
            text="🔐 Iltimos, yangi foydalanuvchi nomini yuboring:",
            reply_markup=back_btn()
        )
        await state.set_state(CredentialsState.waiting_for_new_username)
        
        
@dp.message(CredentialsState.waiting_for_new_password)
async def process_new_password(message: Message, state: FSMContext) -> None:
    new_password = message.text.strip() if message.text else None
    if not new_password:
        await message.answer(
            text="❌ Iltimos, yangi parolini so'zlarni yuboring:",
            reply_markup=back_admin_btn()
        )
        return

    cred = BotCredentials.objects.first()
    if not cred:
        cred = BotCredentials.objects.create()

    new_pass = make_password(new_password)
    cred.password = new_pass
    cred.save()

    await message.answer(
        text="✅ Bot paroli muvaffaqiyatli o'zgartirildi.",
        reply_markup=admin_inline_btn()
    )
    await state.clear()
    
@dp.message(CredentialsState.waiting_for_new_username)
async def process_new_username(message: Message, state: FSMContext) -> None:
    new_username = message.text.strip() if message.text else None
    if not new_username:
        await message.answer(
            text="❌ Iltimos, yangi foydalanuvchi nomini yuboring:",
            reply_markup=back_btn()
        )
        return

    cred = BotCredentials.objects.first()
    if not cred:
        cred = BotCredentials.objects.create()

    cred.username = new_username
    cred.save()

    await message.answer(
        text="✅ Bot foydalanuvchi nomi muvaffaqiyatli o'zgartirildi.",
        reply_markup=admin_inline_btn()
    )
    await state.clear()