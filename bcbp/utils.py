from datetime import datetime, timedelta, timezone


def date_to_doy(
    date: datetime, add_year_prefix: bool = False
) -> str:  # calculate day of year (1-based)
    doy = date.timetuple().tm_yday
    year_prefix = ""
    if add_year_prefix:
        year_prefix = str(date.year)[-1]  # last digit of year
    return f"{year_prefix}{doy:03d}"


def doy_to_date(
    doy: str, has_year_prefix: bool, reference_year: int = None
) -> datetime:
    current_year = reference_year if reference_year is not None else datetime.now().year
    year = str(current_year)
    days_to_add = doy

    if has_year_prefix:
        # extract year prefix and remaining days
        year = year[:-1] + days_to_add[0]
        days_to_add = days_to_add[1:]

        if int(year) - current_year > 2:
            year = str(int(year) - 10)

    base_date = datetime(int(year), 1, 1, tzinfo=timezone.utc)
    target_date = base_date + timedelta(days=int(days_to_add) - 1)

    return target_date
