from domain.objects.types import (
    UsernameOrTelegramID,
    Reason,
    RelativeDateTime,
    ID,
    Text,
    SettingName,
    Word,
    TelegramID,
)
from typing import Optional
from .base import BaseDTO


class BanCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class PreventivelyBanCommandDTO(BaseDTO):
    id: TelegramID
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnbanCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class MuteCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnmuteCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class WarnCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnwarnCommandDTO(BaseDTO):
    id: ID


class ViolationsCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class SetSettingCommandDTO(BaseDTO):
    name: SettingName
    value: Text


class AddModeratorCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class RemoveModeratorCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class CheckCommandDTO(BaseDTO):
    username: UsernameOrTelegramID


class SetReputationCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None


class AddBanWordCommandDTO(BaseDTO):
    word: Word


class RemoveBanWordCommandDTO(BaseDTO):
    word: Word


class GetViolationsCountCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
    start_date: Optional[RelativeDateTime] = None


class AddTrackerCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
    expires_at: Optional[RelativeDateTime] = None


class RemoveTrackerCommandDTO(BaseDTO):
    username: Optional[UsernameOrTelegramID] = None
