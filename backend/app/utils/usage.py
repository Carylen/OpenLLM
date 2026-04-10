from calendar import monthrange
from datetime import date


def get_month_period(target: date | None = None) -> tuple[date, date]:
    d = target or date.today()
    first_day = date(d.year, d.month, 1)
    last_day = date(d.year, d.month, monthrange(d.year, d.month)[1])
    return first_day, last_day
