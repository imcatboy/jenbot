import re

from pydantic import Field, BeforeValidator
from datetime import datetime, timedelta
from typing import Annotated, Any, Set, Union
from enum import StrEnum


class ViolationType(StrEnum):
    WARN = "warn"
    MUTE = "mute"
    BAN = "ban"


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class UserReputationRole(StrEnum):
    ADMIN = "admin"
    SMALL_GUARANTOR = "small_guarantor"
    GUARANTOR = "guarantor"
    BIG_GUARANTOR = "big_guarantor"
    DEPOSITOR = "depositor"
    SCAMMER = "scammer"


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REWARD = "reward"
    PENALTY = "penalty"


class ReportType(StrEnum):
    SCAM = "scam"
    UNBAN = "unban"
    VIOLATION = "violation"
    FEEDBACK = "feedback"
    OTHER = "other"


class ReportStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DealStatus(StrEnum):
    PENDING = "pending"
    EXPIRED = "expired"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DealType(StrEnum):
    MONEY = "money"
    TRADE = "trade"


class SortType(StrEnum):
    POPULARITY = "popularity"
    NEW = "new"
    OLD = "old"


def parse_username(v: Any) -> Union[str, int]:
    if isinstance(v, str) and re.match(r"^@[a-zA-Z0-9_]+$", v):
        return v.replace("@", "")
    elif isinstance(v, str) and v.isdigit():
        return int(v)

    raise ValueError("Username must be a string or ID must be an integer")


UsernameOrID = Annotated[
    Union[str, int],
    Field(description="@username / ID пользователя"),
    BeforeValidator(parse_username),
]

SettingName = Annotated[
    str,
    Field(
        description="Название настройки",
        min_length=3,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_]+$",
    ),
]

Name = Annotated[str, Field(description="Название", min_length=3, max_length=100)]

Username = Annotated[
    str,
    Field(
        description="@username",
        min_length=3,
        max_length=255,
        pattern=r"^@[a-zA-Z0-9_]+$",
    ),
]

Reason = Annotated[str, Field(max_length=255, description="Причина (до 255 символов)")]

ID = Annotated[int, Field(ge=0, le=2147483647, description="ID")]

IDSet = Annotated[
    Set[ID],
    Field(
        max_length=10,
        description="Набор ID в запросе (не более 10 значений)",
    ),
]

NoZeroInt = Annotated[
    int, Field(ge=1, le=2147483647, description="Целое число не равное 0")
]

NoZeroFloat = Annotated[
    float, Field(ge=0.01, le=2147483647, description="Число не равное 0")
]

Text = Annotated[str, Field(max_length=1024, description="Текст (до 1024 символов)")]

Rating = Annotated[int, Field(ge=1, le=5, description="Оценка (от 1 до 5)")]

Word = Annotated[
    str,
    Field(
        max_length=30,
        pattern=r"^[a-zA-ZА-Яа-я0-9_]+$",
        description="Слово (до 30 символов)",
    ),
]

Limit = Annotated[int, Field(ge=1, le=100, description="Ограничение")]

Offset = Annotated[int, Field(ge=0, description="Сдвиг")]


def parse_relative_time(v: Any) -> datetime:
    if isinstance(v, datetime):
        return v
    if not isinstance(v, str):
        raise ValueError("Format must be a string (e.g. '1d12h')")

    periods = {
        "days": r"(\d+)d",
        "hours": r"(\d+)h",
        "minutes": r"(\d+)m",
        "weeks": r"(\d+)w",
    }
    td_kwargs = {}

    for key, pattern in periods.items():
        match = re.search(pattern, v)

        if match:
            td_kwargs[key] = int(match.group(1))

    if not td_kwargs:
        raise ValueError("Invalid time format. Use 'd', 'h' or 'm'")

    return datetime.now() + timedelta(**td_kwargs)


RelativeDateTime = Annotated[
    datetime,
    Field(description='Время в формате "1d12h"'),
    BeforeValidator(parse_relative_time),
]
