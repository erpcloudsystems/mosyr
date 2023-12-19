from datetime import datetime


def get_dates_different_in_minutes(date1: datetime, date2: datetime) -> float:
    return (date1 - date2).total_seconds() / 60


def get_subset_of_dict(dictionary: dict, keys_to_include: list[str]) -> dict:
    return {key: dictionary[key] for key in keys_to_include}
