# filename: app/models/time_period.py

from enum import Enum


class TimePeriodModel(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
