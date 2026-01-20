from celery import shared_task
from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import MostActiveUser, PrizeHistory, User


def get_week_range(today):
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=7)
    return start, end


def get_month_range(today):
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def give_prize(user_ids, prizes):
    for idx, amount in enumerate(prizes):
        if len(user_ids) > idx:
            uid = user_ids[idx]
            u = User.objects.select_for_update().get(id=uid)
            u.coin += amount
            u.save(update_fields=["coin"])


def run_top_prize(period, start_date, end_date, prizes):
    try:
        with transaction.atomic():
            if PrizeHistory.objects.filter(
                group=0,
                period=period,
                start_date=start_date,
                end_date=end_date,
            ).exists():
                return False

            PrizeHistory.objects.create(
                group=0,
                period=period,
                start_date=start_date,
                end_date=end_date,
            )

            top = (
                MostActiveUser.objects
                .filter(
                    created_datetime__date__gte=start_date,
                    created_datetime__date__lt=end_date
                )
                .values("user")
                .annotate(total_win=Sum("games_win"))
                .order_by("-total_win")[:3]
            )

            user_ids = [row["user"] for row in top if (row["total_win"] or 0) > 0]

            if user_ids:
                give_prize(user_ids, prizes)

            return True

    except IntegrityError:
        return False


@shared_task
def daily_top_prizes():
    today = timezone.localdate()
    start = today
    end = today + timedelta(days=1)

    run_top_prize(
        period=PrizeHistory.PERIOD_DAILY,
        start_date=start,
        end_date=end,
        prizes=[5000, 3000, 2000],
    )


@shared_task
def weekly_top_prizes():
    today = timezone.localdate()
    start, end = get_week_range(today)

    run_top_prize(
        period=PrizeHistory.PERIOD_WEEKLY,
        start_date=start,
        end_date=end,
        prizes=[25000, 15000, 10000],
    )


@shared_task
def monthly_top_prizes():
    today = timezone.localdate()
    start, end = get_month_range(today)

    run_top_prize(
        period=PrizeHistory.PERIOD_MONTHLY,
        start_date=start,
        end_date=end,
        prizes=[100000, 50000, 30000],
    )
