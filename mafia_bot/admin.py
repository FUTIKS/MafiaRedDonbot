from django.contrib import admin
from mafia_bot.models import *



admin.site.register(User)
admin.site.register(Game)
admin.site.register(BotMessages)
admin.site.register(PremiumGroup)
admin.site.register(MostActiveUser)
admin.site.register(CasesOpened)
admin.site.register(PrizeHistory)
admin.site.register(GameSettings)
admin.site.register(GroupTrials)

