ROLES_CHOICES = [
    ("peace", "👨🏼 Tinch axoli"),
    ("doc", "👨🏼‍⚕️ Shifokor"),
    ("daydi", "🧙🏼‍♂️ Daydi"),
    ("com", "🕵🏻‍♂️ Komissar katani"),
    ("kam", "💣 Kamikaze"),
    ("lover", "💃🏻 Mashuqa"),
    ("serg", "👮🏻‍♂️ Serjant"),
    ("killer", "🔪 Qotil"),
    ("kaldun", "⚡️ Kaldun"),
    ("mafia", "🤵🏼 Mafia"),
    ("don", "🤵🏻 Don"),
    ("adv", "👨🏻‍💻 Advokat"),
    ("spy", "🦇 Ayg'oqchi"),
    ("lab", "👨‍🔬 Labarant"),
    ("trap", "☠️ Minior"),
    ("snyper", "👨🏻‍🎤 Snayper"),
    ("arrow","🏹 Kamonchi"),
    ("traitor", "🦎 Sotqin"),
    ("snowball", "⛄️ Qorbola"),
    ("santa", "🎅 Santa"),
    ("pirate", "👺 Qaroqchi"),
    ("professor", "🎩 Professor"),
    ("hero", "🥷 Geroy"),
    ("back_main", "⬅️ Orqaga"),
]

LANGUAGE_CHOICES = [
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
        ('en', 'English'),
    ]

SHORT_DESCRIPTIONS = {
    "peace": "🧑🏻 Tinch aholi. Sizning vazifangiz — mafiani topish va kunduzgi ovoz berishda ularni osishga yordam berish.",
    "don": "🤵🏻 Don. Mafialar sardori. Har kecha qurbon tanlaysiz va butun mafia sizning qaroringizga bo'ysunadi.",
    "mafia": "🤵🏼 Mafia. Don bilan birga ishlaysiz, kechalari qurbon tanlaysiz. Don o'lsa uning o'rnini egallashingiz mumkin.",
    "com": "🕵🏻 Komissar. Har kecha o'yinchini tekshiradi, shubhali bo'lsa otishi ham mumkin. Tinch aholi himoyachisi.",
    "serg": "👮🏻 Serjant. Komissarning yordamchisi. Komissar o'lsa uning vazifasini davom ettiradi.",
    "doc": "🧑🏻‍⚕️ Doktor. Har kecha bitta o'yinchini o'limdan saqlab qolishi mumkin. Tinch aholi umidi.",
    "killer": "🔪 Qotil. Yakka rol. Maqsadingiz — boshqalarning hammasi o'lib, faqat siz tirik qolishingiz.",
    "lover": "💃🏻 Mashuqa. Tanlagan o'yinchini bir kechaga blok qiladi, u hech qanday harakat qila olmaydi.",
    "adv": "👨🏻‍💼 Advokat. Mafialar tarafdori. Tanlagan mafiani Komissar ko'ziga tinch aholi qilib ko'rsatadi.",
    "suid": "🤦🏻 Suidsid. Agar sizni kunduz osishsa, o'yin natijasidan qat’i nazar, darhol g'alaba qilasiz.",
    "daydi": "🧙🏻 Daydi. Kechasi bir uyga borib u yerda sodir bo'lgan voqealarning guvohi bo'lishi mumkin.",
    "lucky": "🫶🏻 Omadli. Tinch aholi orasida eng omadli rol, ba’zi xavflardan omon qolish ehtimoli yuqori.",
    "kam": "💣 Kamikaze. Agar sizni osishsa, xohlagan bitta o'yinchini o'zingiz bilan olib ketishingiz mumkin.",
    "kaldun": "⚡️ Kaldun. Tinch tomonda. Tanlagan tinchni himoya qiladi, boshqa tomonni esa o'ldiradi.",
    "spy": "🦇 Ayg'oqchi. Mafialar uchun ishlaydi. Kechasi o'yinchi rolini bilib, mafialarga yetkazadi.",
    "lab": "👨‍🔬 Labarant. Mafialar tarafida. Mafia bo'lsa davolaydi, bo'lmasa o'ldiradi.",
    "trap": "☠️ Minior. Yakka rol. Tanlangan uy oldiga mina qo'yadi, kelganlar halok bo'lishi mumkin.",
    "snyper": "🎯 Snayper. Yakka qotil. Himoyaga qaramay o'ldira oladi va ko'pchilik uni aniqlay olmaydi.",
    "arrow": "🏹 Kamonchi. Yashirin qotil. O'ldirganini Daydi ham sezmaydi.",
    "traitor": "🦎 Sotqin. Tashqi ko'rinishda tinch, aslida mafialar tarafida yashirin ishlaydi.",
    "snowball": "⛄️ Qorbola. Tinch tomonda turadi, lekin kechasi o'yinchini muzlatib o'ldirishi mumkin.",
    "pirate": "👺 Qaroqchi. Yakka rol. Pul talab qiladi, bermasa o'ldiradi.",
    "professor": "🎩 Professor. Yakka rol. O'yinchiga sirli qutilar taklif qiladi va taqdirini o'zi hal qiladi.",
    "santa": "🎅 Santa. Tinch tomonda. Kechasi sovg'a berib o'yinchini himoya qiladi.",
    "hero": "🥷 Geroy. Kunduz ham o'ldira oladi va ba’zi hujumlardan himoyalangan maxsus rol.",
}



ROLES_BY_COUNT = {
    4:  ["peace", "peace", "don", "doc"],
    5:  ["peace", "peace", "don", "doc", "peace"],
    6:  ["peace", "don", "doc", "com", "peace", "mafia"],
    7:  ["peace", "don", "doc", "com", "peace", "mafia", "peace"],
    8:  ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "peace"],
    9:  ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "peace", "peace"],
    10: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia"],
    11: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "peace"],
    12: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "peace"],

    13: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "peace"],
    14: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "peace"],
    15: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "peace"],

    16: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "peace", "mafia"],
    17: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "peace", "mafia"],
    18: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "peace", "mafia"],

    19: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "peace", "mafia"],
    20: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "peace", "mafia"],

    21: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "peace", "mafia"],
    22: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "peace", "mafia"],
    23: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "peace", "mafia"],

    24: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "mafia"],

    25: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "santa", "mafia"],
    26: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "snowball", "peace", "mafia"],

    27: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "snowball", "professor", "santa", "mafia"],

    28: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "snowball", "professor", "santa", "mafia", "mafia"],

    29: ["peace", "don", "doc", "com", "peace", "mafia", "daydi", "kam", "peace", "mafia", "lover", "kaldun", "serg", "killer", "adv", "spy", "lab", "trap", "snyper", "arrow", "traitor", "pirate", "peace", "snowball", "professor", "santa", "mafia", "mafia", "peace"],

    30: ["peace", "peace", "peace", "peace", "peace", "santa", "doc", "daydi", "com", "serg", "lover", "kaldun", "kam", "kam", "don", "mafia", "mafia", "mafia", "mafia", "mafia", "mafia", "adv","spy", "lab", "killer", "killer", "snyper", "arrow", "trap", "pirate", "professor",],
}




ACTIONS = {
    # Mafia
    "don_kill": "🤵🏻 Mafia keyingi qurboni uchun ovoz berish o'tkazyapti: ",
    "mafia_vote": "🤵🏻 Bugun kechasi kimni o'limiga ovoz berasiz?",
    "adv_mask": "👨🏻‍💻 Qaysi mafiya a'zosini yashiramiz?",
    "spy_check": "🦇 Kimning rolini bilib kelamiz?",
    "lab_action": "👨‍🔬 Kimga dori qilamiz?",

    # Peace
    "doc_heal": "👨🏼‍⚕️ Bugun tunda kimni davolaymiz?",
    "com_deside":" 🕵🏻‍♂️ Bugun kechasi nima qilmoqchisiz?",
    "com_check": "🔍 Kimni tekshiramiz?",
    "com_shoot": "🔫 Kimni otamiz?",
    "daydi_watch": "🧙🏼‍♂️ Bugun kechasi kimning uyiga shisha olish uchun borasiz?",
    "lover_block": "💃🏻 Bugun kechani kim bilan o'tkazmoqchisiz?",
    "kaldun_spell": "⚡️ Bugun kechasi kimga sehr qilmoqchisiz?",
    "snowball_kill": "⛄️ Kimni qorbo'ron qilib nobud qilamiz?",
    "santa": "🎅 Kimga sovg'a beramiz?",

    # Solo
    "killer_kill": "🔪 Kimni yo'q qilamiz?",
    "hero":" 🥷 Geroydan foydalanasizmi?",
    "trap_place": "☠️ Kimning uyiga mina qo'yamiz?",
    "snyper_kill": "👨🏻‍🎤 Kimni yo'q qilamiz?",
    "kamikaze_blow": "💣 Kimni portlatamiz?",
    "arrow_kill": "🏹 Kimni yo'q qilamiz?",
    "traitor_choose": "🦎 Kimni tanlaysiz?",
    "pirate_rob": "👺 Kimdan pul undirib olamiz?",
    "professor_choose": "🎩 Kimga 3 ta sirli quti taklif qilamiz?",

    # Pirate response
    "pirate_pay": "👺 Sizdan pul so'rayapti! Pul berasizmi?",
    "pirate_pay_yes": "💰 Pul beraman",
    "pirate_pay_no": "❌ Pul bermayman",

    # Professor response
    "professor_box_pick": "3 ta sirli qutidan birini tanlang:",
    "professor_box_1": "📦 1-quti",
    "professor_box_2": "📦 2-quti",
    "professor_box_3": "📦 3-quti",
}


MONEY_FOR_STAR ={
    "1000": 7,
    "10000": 77,
    "50000": 340,
    "100000": 680,
}

STONE_FOR_STAR = {
    "1": 7,
    "10": 68,
    "30": 185,
    "50": 237,
    "70": 382,
    "100": 513,
}

ROLE_EMOJIS = {
    "peace": "👨🏼",
    "doc": "👨🏼‍⚕️",
    "daydi": "🧙🏼‍♂️",
    "com": "🕵🏻‍♂️",
    "kam": "💣",
    "lover": "💃🏻",
    "serg": "👮🏻‍♂️",
    "killer": "🔪",

    "kaldun": "⚡️",

    "mafia": "🤵🏼",
    "don": "🤵🏻",
    "adv": "👨🏻‍💻",
    "spy": "🦇",
    "lab": "👨‍🔬",

    "trap": "☠️",
    "snyper": "👨🏻‍🎤",
    "arrow": "🏹",
    "traitor": "🦎",

    "snowball": "⛄️",
    "santa": "🎅",

    "pirate": "👺",
    "professor": "🎩",

    "hero": "🥷",

    "back_main": "⬅️",
}

ROLE_PRICES_IN_STONES = {
    "snyper": 4,
    "trap": 3,
    "com":3,
    "don":3,
    "lab":2,
    "kaldun":2,
    "arrow":2,
    "kam": 2,
    "pirate":2,
    "professor":2,
    "santa":1,
    "snowball":1,
    "mafia":1,
    "serg":1,
    "killer":1,
    "traitor":1,
    "hero":50,}
ROLE_PRICES_IN_MONEY = {
    "lover": 400,
    "daydi": 400,
    "adv": 400,
    "spy": 350,
    "doc": 350,
    "peace": 200,
    "hero":50000,
}
    