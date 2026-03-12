import random
from decouple import config
from django.utils import timezone
from mafia_bot.utils import games_state
from aiogram.utils.keyboard import InlineKeyboardBuilder
from mafia_bot.models import  PriceStones,  PremiumGroup, User, UserRole
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.constants import ROLE_PRICES_IN_MONEY,ROLE_PRICES_IN_STONES




def remove_prefix(text):
    return text.lstrip('@')

# Cart inline button
def group_profile_inline_btn(has_stone, chat_id,tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(chat_id)
    TEXTS = {
        "uz": {
            "premium": "💎 Olmosni premiumga o'tkazish",
            "buy_star": "⭐ evaziga 💎 sotib olish",
            "card": "💳 Kartadan 💳 kartaga",
            "manage": "🛠 O'yin boshqarish",
            "lang":"🌐 Tilni o'zgartirish",
            "close": "✖️ Yopish",
        },
        "ru": {
            "premium": "💎 Перевести алмазы в премиум",
            "buy_star": "⭐ Купить 💎 за звёзды",
            "card": "💳 С карты на карту",
            "manage": "🛠 Управление игрой",
            "lang":"🌐 Изменить язык",
            "close": "✖️ Закрыть",
        },
        "en": {
            "premium": "💎 Convert diamonds to premium",
            "buy_star": "⭐ Buy 💎 with stars",
            "card": "💳 Card to card transfer",
            "manage": "🛠 Game management",
            "lang":"🌐 Change language",
            "close": "✖️ Close",
        },
        "tr": {
            "premium": "💎 Elmasları premiuma çevir",
            "buy_star": "⭐ Yıldız ile 💎 satın al",
            "card": "💳 Karttan karta",
            "manage": "🛠 Oyun yönetimi",
            "lang":"🌐 Dili değiştir",
            "close": "✖️ Kapat",
        },
        "qz": {
            "premium": "💎 Алмастарды премиумға ауыстыру",
            "buy_star": "⭐ Жұлдыздармен 💎 сатып алу",
            "card": "💳 Карттан картаға",
            "manage": "🛠 Ойын басқару",
            "lang":"🌐 Тілді өзгерту",
            "close": "✖️ Жабу",
        }
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    keyboard4 = InlineKeyboardButton(
        text=t["premium"],
        url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start=stone_{chat_id}_{tg_id}"
    )
    keyboard1 = InlineKeyboardButton(text=t["buy_star"], callback_data=f"star_group_{tg_id}")
    keyboard2 = InlineKeyboardButton(text=t["card"], url="https://t.me/RedDon_Mafia")
    keyboard3 = InlineKeyboardButton(
        text=t["manage"],
        url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start=instance_{chat_id}_{tg_id}"
    )
    keyboard_lang = InlineKeyboardButton(text=t["lang"], callback_data=f"lange_{tg_id}")
    keyboard5 = InlineKeyboardButton(text=t["close"], style="danger", callback_data=f"close_{tg_id}")

    design = [
        [keyboard4] if has_stone else [],
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard_lang],
        [keyboard5],
    ]

    return InlineKeyboardMarkup(inline_keyboard=design)

def start_inline_btn(user_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(user_id)

    TEXTS = {
        "uz": {
            "roles_info": "ℹ️ Rollar haqida ma'lumot",
            "add_info": "☑️ Botni guruhga qo'shish haqida ma'lumot",
            "add_bot": "➕ Botni guruhga qo'shish",
            "premium": "⭐ Premium guruhlar",
            "profile": "👤 Profil",
            "roles": "🎭 Rollar",
        },
        "ru": {
            "roles_info": "ℹ️ Информация о ролях",
            "add_info": "☑️ Как добавить бота в группу",
            "add_bot": "➕ Добавить бота в группу",
            "premium": "⭐ Премиум группы",
            "profile": "👤 Профиль",
            "roles": "🎭 Роли",
        },
        "en": {
            "roles_info": "ℹ️ Role information",
            "add_info": "☑️ How to add the bot to a group",
            "add_bot": "➕ Add bot to group",
            "premium": "⭐ Premium groups",
            "profile": "👤 Profile",
            "roles": "🎭 Roles",
        },
        "tr": {
            "roles_info": "ℹ️ Roller hakkında bilgi",
            "add_info": "☑️ Botu gruba ekleme hakkında bilgi",
            "add_bot": "➕ Botu gruba ekle",
            "premium": "⭐ Premium gruplar",
            "profile": "👤 Profil",
            "roles": "🎭 Roller",
        },
        "qz": {
            "roles_info": "ℹ️ Ролдер туралы ақпарат",
            "add_info": "☑️ Ботты топқа қосу туралы ақпарат",
            "add_bot": "➕ Ботты топқа қосу",
            "premium": "⭐ Премиум топтар",
            "profile": "👤 Профиль",
            "roles": "🎭 Ролдер",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    keyboard1 = InlineKeyboardButton(text=t["roles_info"], url="https://t.me/MafiaRedDon_Roles/39")
    keyboard2 = InlineKeyboardButton(text=t["add_info"], url="https://t.me/MafiaRedDon_Roles/96")
    keyboard3 = InlineKeyboardButton(
        text=t["add_bot"],
        url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?startgroup=true"
    )
    keyboard4 = InlineKeyboardButton(text=t["premium"], callback_data="groups")
    keyboard5 = InlineKeyboardButton(text=t["profile"], callback_data="profile")
    keyboard6 = InlineKeyboardButton(text=t["roles"], callback_data="role_menu")

    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard4],
        [keyboard5],
        [keyboard6],
    ]

    return InlineKeyboardMarkup(inline_keyboard=design)


def take_stone_btn(chat_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(chat_id)

    TEXTS = {
        "uz": "💎 Olmosni olish",
        "ru": "💎 Забрать алмаз",
        "en": "💎 Take diamond",
        "tr": "💎 Elması al",
        "qz": "💎 Алмосты алу",
    }

    text = TEXTS.get(lang, TEXTS["uz"])

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=text,style="success", callback_data="take_stone"))
    return kb.as_markup()

def take_gsend_stone_btn(chat_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(chat_id)

    TEXTS = {
        "uz": "💎 Olmosni olish",
        "ru": "💎 Забрать алмаз",
        "en": "💎 Take diamond",
        "tr": "💎 Elması al",
        "qz": "💎 Алмосты алу",
    }

    text = TEXTS.get(lang, TEXTS["uz"])

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=text, style="success",callback_data="take_gsend_stone"))
    return kb.as_markup()

def giveaway_join_btn(tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": "✅ Giveawayga qo‘shilish",
        "ru": "✅ Участвовать в розыгрыше",
        "en": "✅ Join giveaway",
        "tr": "✅ Çekilişe katıl",
        "qz": "✅ Giveawayға қосылу",
    }

    text = TEXTS.get(lang, TEXTS["uz"])

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=text, style="success", callback_data="giveaway_join"))
    return kb.as_markup()


def admin_inline_btn():
    keyboard1 = InlineKeyboardButton(text=" 💬 Guruhlar obunasi", callback_data="trial")
    keyboard2 = InlineKeyboardButton(text=" ⭐ Premium guruhlar", callback_data="premium_group")
    keyboard15 = InlineKeyboardButton(text="💎 Kanalga olmos jo'natish", callback_data="send_channel")
    keyboard3 = InlineKeyboardButton(text=" 👥 Foydalanuvchi bilan aloqa", callback_data="user_talk")
    keyboard4 = InlineKeyboardButton(text=" 📢 Botga habar jo'natish", callback_data="broadcast_message")
    keyboard5 = InlineKeyboardButton(text=" 📊 Statistika", callback_data="statistics")
    keyboard6 = InlineKeyboardButton(text=" 💶 Pul jo'natish", callback_data="send_pul")
    keyboard7 = InlineKeyboardButton(text=" 💎 Olmos jo'natish",callback_data="send_olmos")
    keyboard8 = InlineKeyboardButton(text=" 💶 Pul yechib olish", callback_data="remove_pul")
    keyboard9 = InlineKeyboardButton(text=" 💎 Olmos yechib olish",callback_data="remove_olmos")
    keyboard17 = InlineKeyboardButton(text=" ⚠️ Foydalanuvchini bloklash",callback_data="user_block")
    keyboard16 = InlineKeyboardButton(text=" ✅ Foydalanuvchini ochish",callback_data="user_unblock")
    keyboard10 = InlineKeyboardButton(text=" 💰 Pul narxini o'zgartirish",callback_data="change_money")
    keyboard11 = InlineKeyboardButton(text=" 💎 Olmos narxini o'zgartirish",callback_data="change_stone")
    keyboard12 = InlineKeyboardButton(text=" 💳 O'tkazmalar tarixi",callback_data="transfer_history")
    keyboard13 = InlineKeyboardButton(text="📥 Users Excel", callback_data="export_users_excel")
    keyboard14 = InlineKeyboardButton(text=" 🔒 Xavsizlik sozlamalari", callback_data="privacy")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard15],
        [keyboard3],
        [keyboard4],
        [keyboard5],
        [keyboard6,keyboard7],
        [keyboard8,keyboard9],
        [keyboard17,keyboard16],
        [keyboard10],
        [keyboard11],
        [keyboard12],
        [keyboard13],
        [keyboard14],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard



def answer_admin(tg_id, msg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": "✍️ Javob berish",
        "ru": "✍️ Ответить",
        "en": "✍️ Reply",
        "tr": "✍️ Yanıtla",
        "qz": "✍️ Жауап беру",
    }

    text = TEXTS.get(lang, TEXTS["uz"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=f"answer_admin_{tg_id}_{msg_id}"
            ),
        ],
    ])

    return keyboard



def end_talk_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛑 Suhbatni yakunlash", callback_data="end_talk"),
        ],
    ])
    return keyboard

def back_btn(tg_id, place="profile"):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
        "tr": "⬅️ Geri",
        "qz": "⬅️ Артқа",
    }

    text = TEXTS.get(lang, TEXTS["uz"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f"back_{place}")]
        ]
    )
    return keyboard


def back_admin_btn():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")]
        ]
    )
    return keyboard
def case_inline_btn(tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": {
            "money": "💰 Pulli sandiq",
            "stone": "💎 Olmosli sandiq",
            "vip": "⭐ Vip foydalanuvchi",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "money": "💰 Денежный сундук",
            "stone": "💎 Алмазный сундук",
            "vip": "⭐ VIP пользователь",
            "back": "⬅️ Назад",
        },
        "en": {
            "money": "💰 Money chest",
            "stone": "💎 Diamond chest",
            "vip": "⭐ VIP user",
            "back": "⬅️ Back",
        },
        "tr": {
            "money": "💰 Para sandığı",
            "stone": "💎 Elmas sandığı",
            "vip": "⭐ VIP kullanıcı",
            "back": "⬅️ Geri",
        },
        "qz": {
            "money": "💰 Ақша сандық",
            "stone": "💎 Алмас сандық",
            "vip": "⭐ VIP қолданушы",
            "back": "⬅️ Артқа",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["money"], callback_data="case_money")],
            [InlineKeyboardButton(text=t["stone"], callback_data="case_stone")],
            # [InlineKeyboardButton(text=t["vip"], callback_data="case_vip")],
            [InlineKeyboardButton(text=t["back"], callback_data="back_profile")],
        ]
    )

    return keyboard

def cart_inline_btn(tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)
    user = User.objects.filter(telegram_id=tg_id).first()

    TEXTS = {
        "uz": {
            "toggle_protection":f"🛡 - {'ON' if user.is_protected else 'OFF'}",
            "toggle_doc": f"📂 - {'ON' if user.is_doc else 'OFF'}",
            "toggle_hang":f"🎗️ - {'ON' if user.is_hang_protected else 'OFF'}",
            "toggle_geroy_protect":f"🔰 - {'ON' if user.is_geroy_protected else 'OFF'} ",
            "toggle_geroy_use":f"🥷 - {'ON' if user.is_geroy_use else 'OFF'} ",
            "toggle_active_role_use":f"🎭 - {'ON' if user.is_active_role_use else 'OFF'} ",
            "shop": "🛒 Do'kon",
            "buy_money": "💶 Sotib olish",
            "buy_stone": "💎 Sotib olish",
            "hero": "🥷 Mening Geroyim",
            "premium": "⭐ Premium guruhlar",
            "cases": "📦 Sandiqlar",
        },
        "ru": {
            "toggle_protection":f"🛡 - {'ВКЛ' if user.is_protected else 'ВЫКЛ'}",
            "toggle_doc": f"📂 - {'ВКЛ' if user.is_doc else 'ВЫКЛ'}",
            "toggle_hang":f"🎗️ - {'ВКЛ' if user.is_hang_protected else 'ВЫКЛ'}",
            "toggle_geroy_protect":f"🔰 - {'ВКЛ' if user.is_geroy_protected else 'ВЫКЛ'}",
            "toggle_geroy_use":f"🥷 - {'ВКЛ' if user.is_geroy_use else 'ВЫКЛ'}",
            "toggle_active_role_use":f"🎭 - {'ВКЛ' if user.is_active_role_use else 'ВЫКЛ'}",
            "shop": "🛒 Магазин",
            "buy_money": "💶 Купить",
            "buy_stone": "💎 Купить",
            "hero": "🥷 Мой Герой",
            "premium": "⭐ Премиум группы",
            "cases": "📦 Сундуки",
        },
        "en": {
            "toggle_protection":f"🛡 - {'ON' if user.is_protected else 'OFF'}",
            "toggle_doc": f"📂 - {'ON' if user.is_doc else 'OFF'}",
            "toggle_hang":f"🎗️ - {'ON' if user.is_hang_protected else 'OFF'}",
            "toggle_geroy_protect":f"🔰 - {'ON' if user.is_geroy_protected else 'OFF'}",
            "toggle_geroy_use":f"🥷 - {'ON' if user.is_geroy_use else 'OFF'}",
            "toggle_active_role_use":f"🎭 - {'ON' if user.is_active_role_use else 'OFF'}",
            "shop": "🛒 Shop",
            "buy_money": "💶 Buy",
            "buy_stone": "💎 Buy",
            "hero": "🥷 My Hero",
            "premium": "⭐ Premium groups",
            "cases": "📦 Chests",
        },
        "tr": {
            "toggle_protection":f"🛡 - {'ON' if user.is_protected else 'OFF'}",
            "toggle_doc": f"📂 - {'ON' if user.is_doc else 'OFF'}",
            "toggle_hang":f"🎗️ - {'ON' if user.is_hang_protected else 'OFF'}",
            "toggle_geroy_protect":f"🔰 - {'ON' if user.is_geroy_protected else 'OFF'}",
            "toggle_geroy_use":f"🥷 - {'ON' if user.is_geroy_use else 'OFF'}",
            "toggle_active_role_use":f"🎭 - {'ON' if user.is_active_role_use else 'OFF'}",
            "shop": "🛒 Mağaza",
            "buy_money": "💶 Satın al",
            "buy_stone": "💎 Satın al",
            "hero": "🥷 Kahramanım",
            "premium": "⭐ Premium gruplar",
            "cases": "📦 Sandıklar",
        },
        "qz": {
            "toggle_protection":f"🛡 - {'ВКЛ' if user.is_protected else 'ВЫКЛ'}",
            "toggle_doc": f"📂 - {'ВКЛ' if user.is_doc else 'ВЫКЛ'}",
            "toggle_hang":f"🎗️ - {'ВКЛ' if user.is_hang_protected else 'ВЫКЛ'}",
            "toggle_geroy_protect":f"🔰 - {'ВКЛ' if user.is_geroy_protected else 'ВЫКЛ'}",
            "toggle_geroy_use":f"🥷 - {'ВКЛ' if user.is_geroy_use else 'ВЫКЛ'}",
            "toggle_active_role_use":f"🎭 - {'ВКЛ' if user.is_active_role_use else 'ВЫКЛ'}",
            "shop": "🛒 Дүкен",
            "buy_money": "💶 Сатып алу",
            "buy_stone": "💎 Сатып алу",
            "hero": "🥷 Менің Кейіпкерім",
            "premium": "⭐ Премиум топтар",
            "cases": "📦 Сандықтар",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])
    if user.is_protected:
        style_protect="success"
    else:
        style_protect="danger"
    if user.is_doc:
        style_doc= "success"
    else:
        style_doc = "danger"
    if user.is_hang_protected:
        style_hang="success"
    else:
        style_hang = "danger"
    if user.is_geroy_protected:
        style_geroy = "success"
    else:
        style_geroy ="danger"
    if user.is_geroy_use:
        style_use = "success"
    else:
        style_use ="danger"
    if user.is_active_role_use:
        style_active = "success"
    else:
        style_active ="danger"
        

    rows = [
        [
            InlineKeyboardButton(text=t["toggle_protection"], style =style_protect, callback_data="toggle_protection"),
            InlineKeyboardButton(text=t["toggle_doc"], style =style_doc, callback_data="toggle_doc"),
        ],
        [
            InlineKeyboardButton(text=t["toggle_hang"],style =style_hang, callback_data="toggle_hang"),
            InlineKeyboardButton(text=t["toggle_geroy_protect"], style=style_geroy, callback_data="toggle_geroy"),
        ],
    ]

    conditional_row = []

    if user and user.is_hero:
        conditional_row.append(
            InlineKeyboardButton(text=t["toggle_geroy_use"],style=style_use, callback_data="toggle_geroyuse")
        )

    if user and UserRole.objects.filter(user_id=user.id, quantity__gt=0).exists():
        conditional_row.append(
            InlineKeyboardButton(text=t["toggle_active_role_use"], style=style_active, callback_data="toggle_activerole")
        )

    if conditional_row:
        rows.append(conditional_row)

    rows += [
        [InlineKeyboardButton(text=t["shop"], style="primary", callback_data="cart")],
        [
            InlineKeyboardButton(text=t["buy_money"], style="primary", callback_data="money_money"),
            InlineKeyboardButton(text=t["buy_stone"], style="primary",   callback_data="money_stone"),
        ],
        [InlineKeyboardButton(text=t["hero"], style="success", callback_data="geroy_no")],
        [InlineKeyboardButton(text=t["premium"], style="primary", callback_data="groups")],
        [InlineKeyboardButton(text=t["cases"], style="success", callback_data="cases")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    return keyboard

def shop_inline_btn(tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": {
            "protect": "🛡 Ximoya - 250 💵",
            "docs": "📂 Hujjatlar - 500 💵",
            "hang_money": "🎗️ Osilishdan ximoya - 20000 💵",
            "hang_stone": "🎗️ Osilishdan ximoya - 20 💎",
            "geroy_protect": "🔰 Geroy himoyasi - 10000 💵",
            "role": "🎭 Rol sotib olish",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "protect": "🛡 Защита - 250 💵",
            "docs": "📂 Документы - 500 💵",
            "hang_money": "🎗️ Защита от повешения - 20000 💵",
            "hang_stone": "🎗️ Защита от повешения - 20 💎",
            "geroy_protect": "🔰 Защита героя - 10000 💵",
            "role": "🎭 Купить роль",
            "back": "⬅️ Назад",
        },
        "en": {
            "protect": "🛡 Protection - 250 💵",
            "docs": "📂 Documents - 500 💵",
            "hang_money": "🎗️ Hanging protection - 20000 💵",
            "hang_stone": "🎗️ Hanging protection - 20 💎",
            "geroy_protect": "🔰 Hero protection - 10000 💵",
            "role": "🎭 Buy role",
            "back": "⬅️ Back",
        },
        "tr": {
            "protect": "🛡 Koruma - 250 💵",
            "docs": "📂 Belgeler - 500 💵",
            "hang_money": "🎗️ Asılmaya karşı koruma - 20000 💵",
            "hang_stone": "🎗️ Asılmaya karşı koruma - 20 💎",
            "geroy_protect": "🔰 Kahraman koruması - 10000 💵",
            "role": "🎭 Rol satın al",
            "back": "⬅️ Geri",
        },
        "qz": {
            "protect": "🛡 Қорғау - 250 💵",
            "docs": "📂 Құжаттар - 500 💵",
            "hang_money": "🎗️ Асудан қорғау - 20000 💵",
            "hang_stone": "🎗️ Асудан қорғау - 20 💎",
            "geroy_protect": "🔰 Герой қорғауы - 10000 💵",
            "role": "🎭 Роль сатып алу",
            "back": "⬅️ Артқа",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["protect"], callback_data="buy_protection_0")],
            [InlineKeyboardButton(text=t["docs"], callback_data="buy_docs_0")],
            [InlineKeyboardButton(text=t["hang_money"], callback_data="buy_hangprotect_1")],
            [InlineKeyboardButton(text=t["hang_stone"], callback_data="buy_hangprotect_2")],
            [InlineKeyboardButton(text=t["geroy_protect"], callback_data="buy_geroyprotect_0")],
            [InlineKeyboardButton(text=t["role"], callback_data="buy_activerole_0")],
            [InlineKeyboardButton(text=t["back"], callback_data="back_profile")],
        ]
    )

    return keyboard


def get_role_price(role_key: str):
    if role_key in ROLE_PRICES_IN_STONES:
        return "💎", ROLE_PRICES_IN_STONES[role_key]
    if role_key in ROLE_PRICES_IN_MONEY:
        return "💵", ROLE_PRICES_IN_MONEY[role_key]
    return "", 0

def role_shop_inline_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    from mafia_bot.handlers.main_functions import get_roles_choices_lang
    ROLES_CHOICES = get_roles_choices_lang(user_id)
    roles = ROLES_CHOICES[:-2]

    for role_key, role_name in roles:
        cur, price = get_role_price(role_key)

        builder.add(
            InlineKeyboardButton(
                text=f"{role_name} - {cur} {price}",
                callback_data=f"active_{role_key}_{price}",
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ ",
            callback_data="back_profile"
        )
    )

    builder.adjust(2, 2, 2, 2, 2, 2, 2, 2, 2, 1)
    return builder.as_markup()
def pay_for_money_inline_btn(tg_id, is_money):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": {
            "card": "💳 Kartadan 💳 kartaga",
            "stars": "⭐ Telegram yulduzlar evaziga",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "card": "💳 С карты на карту",
            "stars": "⭐ За Telegram звёзды",
            "back": "⬅️ Назад",
        },
        "en": {
            "card": "💳 Card to card",
            "stars": "⭐ Pay with Telegram Stars",
            "back": "⬅️ Back",
        },
        "tr": {
            "card": "💳 Karttan karta",
            "stars": "⭐ Telegram yıldızları ile",
            "back": "⬅️ Geri",
        },
        "qz": {
            "card": "💳 Карттан карта",
            "stars": "⭐ Telegram жұлдыздарымен",
            "back": "⬅️ Артқа",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    if is_money:
        callback1 = "p2p_money"
        callback2 = "star_money"
    else:
        callback1 = "p2p_stone"
        callback2 = "star_stone"

    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text=t["card"], callback_data=callback1)
    )
    builder.add(
        InlineKeyboardButton(text=t["stars"], callback_data=callback2)
    )
    builder.add(
        InlineKeyboardButton(text=t["back"], callback_data="back_profile")
    )

    builder.adjust(1)
    return builder.as_markup()

import json
MONEY_FOR_STAR = {
    1000: 7,
    10000: 77,
    50000: 340,
    100000: 680,
}

STONE_FOR_STAR = {
    1: 7,
    10: 68,
    30: 185,
    50: 237,
    70: 382,
    100: 513,
}


def pay_using_stars_inline_btn(is_money: bool):
    builder = InlineKeyboardBuilder()

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    money_map = json.loads(cost.money_in_star or "{}")
    stone_map = json.loads(cost.stone_in_star or "{}")

    if is_money:
        for money_amount, star_amount in money_map.items():
            builder.add(
                InlineKeyboardButton(
                    text=f"💶 {money_amount} - ⭐ {star_amount}",
                    callback_data=f"pul_{money_amount}_{star_amount}"
                )
            )
    else:
        for stone_amount, star_amount in stone_map.items():
            builder.add(
                InlineKeyboardButton(
                    text=f"💎 {stone_amount} - ⭐ {star_amount}",
                    callback_data=f"olmos_{stone_amount}_{star_amount}"
                )
            )

    builder.add(
        InlineKeyboardButton(
            text="⬅️",
            callback_data="back_profile"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


# Roles inline button
def roles_inline_btn(user_id):
    builder = InlineKeyboardBuilder()
    
    from mafia_bot.handlers.main_functions import get_roles_choices_lang
    ROLES_CHOICES = get_roles_choices_lang(user_id)
    for role in ROLES_CHOICES:
        button = InlineKeyboardButton(text=role[1], callback_data=f"roles_{role[0]}")
        builder.add(button)
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard   
        
# Join game button
def join_game_btn(uuid,chat_id):
    from mafia_bot.handlers.main_functions import get_lang_text
    t = get_lang_text(int(chat_id))
    text = t["join_game"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=text,
                style="success",
                url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start={uuid}"  # game.code yoki game.uuid
            )]
        ]
    )
    return keyboard
# Go to bot inline button
def go_to_bot_inline_btn(chat_id,number=1):
    from mafia_bot.handlers.main_functions import get_lang_text
    t = get_lang_text(int(chat_id))
    if number == 1:
        text = t["view_role"]
    elif number == 2:
        text = t["go_to_bot"]
    elif number == 3:
        text = t["vote"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=text,
                style="success",
                url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}"  
            )]
        ]
    )
    return keyboard

# Doctor inline button
def doc_btn(players,doctor_id=None,game_id=None,chat_id=None,day=None):
    builder = InlineKeyboardBuilder()
    game = games_state.get(int(game_id), {})
    used_self = game.get("limits", {}).get("doc_self_heal_used", set())
    for player in players :
        first_name = player.get("first_name")
        tg_id = player.get("tg_id")
        if tg_id == doctor_id and doctor_id in used_self:
            continue
        callback=f"doc_{tg_id}_{game_id}_{chat_id}_{day}"
    
        button = InlineKeyboardButton(
            text=first_name,
            callback_data=callback
        )
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="🚷",
            callback_data=f"doc_no_{game_id}_{chat_id}_{day}"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


# Commander inline button
def com_inline_btn(game_id,chat_id,day=None):
    builder = InlineKeyboardBuilder()
    button1 = InlineKeyboardButton(text="🔫", callback_data=f"com_shoot_{game_id}_{chat_id}_{day}")
    button2 = InlineKeyboardButton(text="🔍", callback_data=f"com_protect_{game_id}_{chat_id}_{day}")
    builder.add(button1)
    builder.add(button2)
    builder.add(
        InlineKeyboardButton(
            text="🚷",
            callback_data=f"com_no_{game_id}_{chat_id}_{day}"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

# Com inline action button
def com_inline_action_btn(action,game_id,chat_id,day=None,com_id=None):
    builder = InlineKeyboardBuilder()
    game = games_state.get(int(game_id), {})
    alive_players = game.get("alive", [])
    users_map = game.get("users_map", {})
    alive_users_qs = [users_map[tg_id] for tg_id in alive_players if tg_id in users_map]
    for user in alive_users_qs:
        
        if user.get("tg_id") == com_id:
            continue
        button = InlineKeyboardButton(
            text=f"{user.get("first_name")}",
            callback_data=f"{action}_{user.get("tg_id")}_{game_id}_{day}"
        )
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="🔙",
            callback_data=f"com_back_{game_id}_{chat_id}_{day}"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

# Kamikaze inline button

def action_inline_btn(action,own_id,players,game_id,chat_id,day=None):
    builder = InlineKeyboardBuilder()

    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        if tg_id == own_id:
            continue
        text = first_name 
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"{action}_{tg_id}_{game_id}_{chat_id}_{day}"
        )
        builder.add(button)
    
    button = InlineKeyboardButton(
        text="🚷 ",
        callback_data=f"{action}_no_{game_id}_{chat_id}_{day}"
    )
    builder.add(button)

    builder.adjust(1)
    return builder.as_markup()

def confirm_hang_inline_btn(voted_user_id,game_id,chat_id,yes=0, no=0):
    builder = InlineKeyboardBuilder()
    button_yes = InlineKeyboardButton(
        text=f"👍 {yes}",
        callback_data=f"con_yes_{voted_user_id}_{game_id}_{chat_id}"
    )
    button_no = InlineKeyboardButton(
        text=f"👎 {no}",
        callback_data=f"con_no_{voted_user_id}_{game_id}_{chat_id}"
    )
    builder.add(button_yes)
    builder.add(button_no)
    builder.adjust(2)
    return builder.as_markup()


    


def don_inline_btn(players,  game_id, chat_id, don_id,day=None):
    builder = InlineKeyboardBuilder()

    roles_map = games_state.get(int(game_id), {}).get("roles", {})

    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)

        if tg_id == don_id:
            continue
        
        if role == "mafia":
            continue
        elif role == "spy":
            text = f"🦇 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name

        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"don_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"don_no_{game_id}_{chat_id}_{day}"
    ))

    builder.adjust(1)
    return builder.as_markup()


def mafia_inline_btn(players, game_id,day=None):
    builder = InlineKeyboardBuilder()

    roles_map = games_state.get(int(game_id), {}).get("roles", {})

    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)

        
        
        if role == "mafia":
            continue
        elif role == "don":
            continue
        elif role == "spy":
            text = f"🦇 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name

        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"mafia_{tg_id}_{game_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"mafia_no_{game_id}_{day}"
    ))
    builder.adjust(1)
    return builder.as_markup()


def adv_inline_btn(players,  game_id, chat_id,day=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)
        if role not in ["don", "mafia"]:
            continue
        if role == "don":
            text = f"🤵🏻 {first_name}"
        else:
            text = f"🤵🏼 {first_name}"
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"adv_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"adv_no_{game_id}_{chat_id}_{day}"
    ))

    builder.adjust(1)
    return builder.as_markup()


def spy_inline_btn(players,  game_id, chat_id,day=None,spy_id=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)
        
        if tg_id == spy_id:
            continue
        
        if role == "don":
            text = f"🤵🏻 {first_name}"
        elif role == "mafia":
            text = f"🤵🏼 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"spy_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"spy_no_{game_id}_{chat_id}_{day}"
    ))
    builder.adjust(1)
    return builder.as_markup()


def lab_inline_btn(players, lab_id, game_id, chat_id,day=None):
    builder = InlineKeyboardBuilder()
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        if tg_id == lab_id:
            continue
        
        builder.add(
            InlineKeyboardButton(
                text=first_name,
                callback_data=f"lab_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"lab_no_{game_id}_{chat_id}_{day}"
    ))

    builder.adjust(1)
    return builder.as_markup()



def pirate_steal_inline_btn( pirate_id,game_id,day=None):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="10💶 ",
            callback_data=f"pirpay_yes_{pirate_id}_{game_id}_{day}"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="🚷 ",
            callback_data=f"pirpay_no_{pirate_id}_{game_id}_{day}"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


def professor_gift_inline_btn(game_id,day=None,professor_id=None,chat_id=None):
    bulider = InlineKeyboardBuilder()
    callbacks = ["die", "empty", "geroy"]
    random.shuffle(callbacks)
    bulider.add(
        InlineKeyboardButton(
            text="📦",
            callback_data=f"prof_{callbacks[0]}_{game_id}_{day}_{professor_id}_{chat_id}"
        )
        
    )
    bulider.add(
        InlineKeyboardButton(
            text="📦",
            callback_data=f"prof_{callbacks[1]}_{game_id}_{day}_{professor_id}_{chat_id}"
        )
        
    )
    bulider.add(
        InlineKeyboardButton(
            text="📦",
            callback_data=f"prof_{callbacks[2]}_{game_id}_{day}_{professor_id}_{chat_id}"
        )
        
    )
    
    bulider.adjust(1)
    return bulider.as_markup()
    
def hang_inline_btn(players, own_id, game_id, chat_id,day=None):
    builder = InlineKeyboardBuilder()

    for tg_id, first_name in players.values():
        if tg_id == own_id:
            continue
        text = first_name
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"hang_{tg_id}_{game_id}_{chat_id}_{day}"
        )
        builder.add(button)

    builder.adjust(1)
    return builder.as_markup()


def groups_inline_btn():
    builder = InlineKeyboardBuilder()
    premium_groups = PremiumGroup.objects.all().order_by("-stones_for")
    for group in premium_groups:
        if group.link is None or group.name is None:
            continue
        if group.ends_date and group.ends_date < timezone.now():
            group.delete()
            continue
        if "@"  in group.link:
            url = f"https://t.me/{remove_prefix(group.link)}"
        elif "http" in group.link or "https" in group.link:
            url = group.link
        button = InlineKeyboardButton(
            text=f"{group.name} - {group.stones_for} 💎",
            url=url
        )
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_profile"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def groupes_keyboard(questions, page: int, total: int, per_page: int, all=False) :
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"quiz_select:{q.id}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"quiz_page:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"quiz_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text="Guruh qo'shish ➕",
            callback_data="add_group"
        ),
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        ),
    )

    return builder.as_markup()

def trial_groupes_keyboard(questions, page: int, total: int, per_page: int, all=False) :
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"olga_select:{q.id}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"olga_page:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"olga_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        ),
    )

    return builder.as_markup()

def group_manage_btn(quiz_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="📝 Tahrirlash",
            callback_data=f"manage_edit:{quiz_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ O'chirish",
            callback_data=f"manage_delete:{quiz_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def change_money_cost():
    keyboard = InlineKeyboardButton(
        text="💳 Puldagi narxni o'zgartirish", callback_data="aziz_money")
    keyboard1 = InlineKeyboardButton(
        text="⭐ Starsdagi narxni o'zgartirish", callback_data="aziz_star")
    keyboard2 = InlineKeyboardButton(
        text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard],
        [keyboard1],
        [keyboard2],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def change_stones_cost():
    keyboard = InlineKeyboardButton(
        text="💳 Puldagi narxni o'zgartirish", callback_data="ozgar_money")
    keyboard1 = InlineKeyboardButton(
        text="⭐ Starsdagi narxni o'zgartirish", callback_data="ozgar_star")
    keyboard2 = InlineKeyboardButton(
        text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard],
        [keyboard1],
        [keyboard2],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard


def money_case():
    builder = InlineKeyboardBuilder()
    
    for i in range(0,10):
        number = random.randint(899,2000)
        button = InlineKeyboardButton(
            text=f"{i+1}",
            callback_data=f"open_money_{number}"
        )
        builder.add(button)
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_case"
        )
    )
    return builder.as_markup()
        
def stone_case():
    builder = InlineKeyboardBuilder()
    
    for i in range(0,10):
        number = random.randint(3,12)
        button = InlineKeyboardButton(
            text=f"{i+1}",
            callback_data=f"open_stone_{number}"
        )
        builder.add(button)
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_case"
        )
    )
    return builder.as_markup()

def begin_instance_inline_btn(chat_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔢 O'yinchilar to'lganda boshlash",
                callback_data=f"begin_instance_{chat_id}"
            )],
            [InlineKeyboardButton(
                text="⏱ Belgilangan vaqtdan so'ng boshlash",
            callback_data=f"begin_time_{chat_id}"
            )],
            [
                InlineKeyboardButton(
                text="🔁 O'yin tugagach auto boshlash",
                callback_data=f"begin_auto_{chat_id}"
            )],
            [InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data="back_profile"
            )]
        ]
    )
    return keyboard

def trial_group_manage_btn(group_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Obunani uzaytish 🔄",
            callback_data=f"extend:{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Guruh hisobiga coin qo'shish ➕",
            callback_data=f"add_pul_{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Guruh hisobiga olmos qo'shish ➕",
            callback_data=f"add_stone_{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_groups"
        )
    )
    builder.adjust(1)
    return builder.as_markup()



def history_groupes_keyboard(page: int, total: int, per_page: int):
    builder = InlineKeyboardBuilder()

    total_pages = (total + per_page - 1) // per_page

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"history_page:{page - 1}"
            )
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"history_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        )
    )

    return builder.as_markup()

def groups_buy_stars(chat_id):
    builder = InlineKeyboardBuilder()

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    stone_map = json.loads(cost.stone_in_star or "{}")

    for stone_amount, star_amount in stone_map.items():
        builder.add(
            InlineKeyboardButton(
                text=f"💎 {stone_amount} - ⭐ {star_amount}",
                url=f"https://t.me/{remove_prefix(config("BOT_USERNAME"))}?start=paym_{chat_id}_{stone_amount}_{star_amount}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_group"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def stones_to_premium_inline_btn(stones: int, chat_id: int):
    builder = InlineKeyboardBuilder()

    amounts = [20, 25, 30, 50, 100, 150, 200, 300]

    for amount in amounts:
        if stones >= amount:
            builder.add(
                InlineKeyboardButton(
                    text=f"⭐ Premium ({amount} 💎)",
                    callback_data=f"prem_{amount}_{chat_id}"
                )
            )

    builder.add(
        InlineKeyboardButton(
            text="✖️ Yopish",
            callback_data="close"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


def privacy_inline_btn():
    keyboard1 = InlineKeyboardButton(text=" 🔑 Parolni o'zgartirish", callback_data="credentials_password")
    keyboard2 = InlineKeyboardButton(text=" 👤 Username o'zgartirish", callback_data="credentials_username")
    keyboard3 = InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard


def use_hero_inline_btn(attack,game_id, chat_id, tg_id, day=None):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)

    TEXTS = {
        "uz": {
            "attack": "🥷 Hujum qilish",
            "protect": "🛡 Himoyalanish",
        },
        "ru": {
            "attack": "🥷 Атаковать",
            "protect": "🛡 Защититься",
        },
        "en": {
            "attack": "🥷 Attack",
            "protect": "🛡 Defend",
        },
        "tr": {
            "attack": "🥷 Saldır",
            "protect": "🛡 Savun",
        },
        "qz": {
            "attack": "🥷 Hujum",
            "protect": "🛡 Qorğau",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    builder = InlineKeyboardBuilder()
    if attack:
        builder.add(
            InlineKeyboardButton(
                text=t["attack"],
                callback_data=f"hero_attack_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text=t["protect"],
            callback_data=f"hero_protect_{game_id}_{chat_id}_{day}"
        )
    )

    builder.adjust(1)
    return builder.as_markup()



def geroy_inline_btn(tg_id):
    from mafia_bot.handlers.main_functions import get_lang

    lang = get_lang(tg_id)
    user = User.objects.filter(telegram_id=tg_id).first()
    is_geroy = user and user.is_hero
    price = 100+ user.hero_level * 10 if user else 110
    is_hero_max = user.hero_level >= 17 if user else False

    TEXTS = {
        "uz": {
            "buy_stone": "🥷 Sotib olish 💎 100",
            "upgrade_geroy":f"➕ Geroyni kuchaytirish 💎 {price}",
            "remove": "✖️ Geroyni olib tashlash",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "buy_stone": "🥷 Купить 💎 100",
            "upgrade_geroy":f"➕ Улучшить Героя 💎 {price}",
            "remove": "✖️ Убрать Героя",
            "back": "⬅️ Назад",
        },
        "en": {
            "buy_stone": "🥷 Buy for 💎 100",
            "upgrade_geroy":f"➕ Upgrade Hero 💎 {price}",
            "remove": "✖️ Remove Hero",
            "back": "⬅️ Back",
        },
        "tr": {
            "buy_stone": "🥷 💎 100 ile satın al",
            "upgrade_geroy":f"➕ Kahramanı yükselt 💎 {price}",
            "remove": "✖️ Kahramanı kaldır",
            "back": "⬅️ Geri",
        },
        "qz": {
            "buy_stone": "🥷 Сатып алу 💎 100",
            "upgrade_geroy":f"➕ Кейіпкерді күшейту 💎 {price}",
            "remove": "✖️ Кейіпкерді алып тастау",
            "back": "⬅️ Артқа",
        },
    }

    t = TEXTS.get(lang, TEXTS["uz"])

    keyboard1 = InlineKeyboardButton(text=t["buy_stone"], callback_data="geroy_buy")
    keyboard2 = InlineKeyboardButton(text=t["upgrade_geroy"], callback_data="geroy_upgrade")
    keyboard3 = InlineKeyboardButton(text=t["remove"], callback_data="geroy_sold")
    keyboard4 = InlineKeyboardButton(text=t["back"], callback_data="back_profile")

    if is_geroy:
        if is_hero_max:
            design = [
                [keyboard3],
                [keyboard4],
            ]
        else:
            design = [
            [keyboard2],
            [keyboard3],
            [keyboard4],
        ]
    else:
        design = [
            [keyboard1],
            [keyboard4],
        ]

    return InlineKeyboardMarkup(inline_keyboard=design)


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
        ],
        [
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_qz"),
            
        ]
    ])


def confirm_channel_olmos_inline_btn(channel_username, amount):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✅ Tasdiqlash",
            callback_data=f"send_confirm_{channel_username}_{amount}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data="send_no"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def claim_chanel_olmos_inline_btn(username):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💎 Olmosni olish",
                url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start=claim_{username}"      
                )
        ]
    ])