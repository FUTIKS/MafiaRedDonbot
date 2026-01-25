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


DESCRIPTIONS = {
        "peace": "👨🏼 Tinch aholi! Sizning vazifangiz mafiani topish va ovoz berish jarayonida ularni osish.",
        "don": "🤵🏻 Don (Mafialar sardori)! Bu tunda kim o'lishini siz xal qilasiz.",
        "mafia": "🤵🏼 Mafia Sizning donga bo'ysinasiz va sizga qarshilik qilganlarni o'dirasiz. Don o'lsa siz yangi Don bo'lishingiz mumkin.",
        "com": "🕵🏻‍♂️ Komissar katani! Shaharning asosiy himoyachisi va mafia kushandasi...",
        "serg": "👮🏻‍♂️ Serjant! 🕵🏻‍♂Komissarga yordam berish.  U sizni o'z harakatlaringiz to'g'risida xabardor qiladi va sizni voqealar to'g'risida xabardor qiladi.  Agar komissar vafot etsa, uning o'rnini egallaysiz.",
        "doc": "👨🏼‍⚕️ Shifokor! Siz aholining birdan-bir umidisiz...",
        "killer": "🔪 Qotil! Shaharda hamma o'lishi kerak...",
        "lover": "💃🏻 Mashuqa! Bu shavqatsiz shaharda tirik qolishingiz kerak...",
        "adv": "👨🏻‍💻 Advokat! Mafialar tarafdori. Advokat tanlagan mafiani 🕵️‍ Komissar Katani taniy olmaydi va unga 👨🏼 Tinch axoli bo'lib ko'rinadi.",
        "suid": "🤦🏻‍♂️ Suidsid! Sizni osishsa siz yutasiz 😵",
        "daydi": "🧙🏼‍♂️ Daydi! Siz shishsa olishga borganda qotillik guvohi bo'lishingiz mumkin.",
        "lucky": "🫶🏻 Omadli! Tinch aholi orasida eng omadlisisiz...",
        "kam": "💣 Kamikaze! Agar sizni osishsa bir kishini ozingiz bilan olib ketsangiz bo'ladi.",
        "kaldun": "⚡️ Kaldun!  tinch axolilar tarafdori. Tunda tanlagan o'yinchi tinch axolilar tarafida bo'lsa uni tongda osilishdan saqlab qoladi.  agar u boshqa taraf o'yinchisi bo'lsa uni o'ldiradi.",
        "spy": "🦇 Ayg'oqchi! Mafialar tarafdori. Tunda u xohlagan bitta o'yinchining ro'lini bilishi va uni mafialar uchun oshkor qilishi mumkin.",
        "lab": "👨‍🔬 Labarant! Mafialar tarafdori. Tunda u tanlagan odam mafialar tarafida bo'lsa uni davolaydi agar mafia bo'lmasa uni o'ldiradi",
        "trap": "☠️ Minior! Yakka rol. Tunda tanlagan odamini eshigi oldiga mina qo'yadi va u uyga o'sha tunda kelgan Miniordan boshqalar o'ladi.",
        "snyper": "👨🏻‍🎤 Snayper! Yakka rol.\nU tunda tanlagan odamda himoya bo'lsa ham u o'ladi daydi ham snayperni ko'ra olmaydi va uni yakka taraf odamlari o'ldira olmaydi. \nEng kuchli ro'llardan biri.",
        "arrow": "🏹 Kamonchi! Yakka rol. Kamonchi maxfiy qotil. Tunda u kimnidir o'ldirganini daydi sezmaydi.",
        "traitor": "🦎 Sotqin! Yakka rol. U tinch axolilar tarafida bo'lib ko'rinadi lekin mafialar tarafdori. U har kecha bir marta mafialar bilan maslahatlashishi mumkin va ular bilan birga ovoz berishi mumkin.",
        "snowball":"⛄️ Qorbola Tinch axolilar tarafida. \nSiz tunda istagan ishtirokchini qorbo'ron qilib nobud qilishingiz mumkin.",
        "pirate":"👺 Qaroqchi Siz Yakka rollar tarafdasiz.\nSiz tunda istalgan foydalanuvchini uyiga borip undan pul undirishingiz mumkin, agarda pul berishdan bosh tortsa shu zahoti uni o'ldirishingiz mumkin.",
        "professor":"🎩 Professor Siz Yakka rollar tarafdasiz. Siz tunda tanlagan ishtirokchiga 3 ta sirli quti taklif qilasiz ularning ichida:\n⚰️ O'lim, 🥡 Bo'sh quti hamda 🥷 Geroydan foydalanish berkitilgan bo'ladi va u ishtirokchi o'z taqdirini o'zi xal qiladi.",
        "santa":"🎅 Santa Tinch axolilar tarafida. Siz har kecha bitta ishtirokchiga sovg'a berishingiz mumkin bu sovg'a unga himoya beradi va uni osilishdan saqlab qoladi.",
        "hero":"🥷 Geroy - bu o‘yinda kun vaqtida ham o‘yinchilarni o‘ldirishga imkon beradigan, boshqa geroylar xujumidan ximoya qiladigan yordamchi personaj.",
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
    "pirate_pay": "👺 Sizdan pul so‘rayapti! Pul berasizmi?",
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
    