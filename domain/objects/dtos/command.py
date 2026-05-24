from domain.objects.types import UsernameOrID, Reason, RelativeDateTime, ID, Text, SettingName, Word
from typing import Optional
from .base import BaseDTO


class BanCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class PreventivelyBanCommandDTO(BaseDTO):
    id: ID
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnbanCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class MuteCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnmuteCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class WarnCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None
    expires_at: Optional[RelativeDateTime] = None
    reason: Reason


class UnwarnCommandDTO(BaseDTO):
    id: ID


class ViolationsCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class SetSettingCommandDTO(BaseDTO):
    name: SettingName
    value: Text


class AddModeratorCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class RemoveModeratorCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class CheckCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class SetReputationCommandDTO(BaseDTO):
    username: Optional[UsernameOrID] = None


class AddBanWordCommandDTO(BaseDTO):
    word: Text


class RemoveBanWordCommandDTO(BaseDTO):
    word: Word