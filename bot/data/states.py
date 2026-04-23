from aiogram.fsm.state import State, StatesGroup


class ReportState(StatesGroup):
    reason = State()
    attachments = State()
    report_type = State()
    accused_user_id = State()
    username = State()


class AdminReportState(StatesGroup):
    report_message_id = State()
    admin_comment = State()
    report_status = State()
    report_id = State()


class AdminScamReportState(StatesGroup):
    accused_user_id = State()
    description = State()


class AdminSetReputationState(StatesGroup):
    user_id = State()
    description = State()
    role = State()