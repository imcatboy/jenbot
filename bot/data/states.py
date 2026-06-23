from aiogram.fsm.state import State, StatesGroup


class ReportState(StatesGroup):
    reason = State()
    attachments = State()
    type = State()
    accused_user_id = State()
    username = State()


class AdminReportState(StatesGroup):
    report_message_id = State()
    admin_comment = State()
    report_status = State()
    report_id = State()


class ScamReportState(StatesGroup):
    description = State()
    contact_info = State()
    attachments = State()


class AnswerScamReportState(StatesGroup):
    scam_report_message_id = State()
    comment = State()
    report_status = State()
    scam_report_id = State()


class ReviewState(StatesGroup):
    rating = State()
    message = State()
    user_id = State()


class ExternalDealState(StatesGroup):
    seller_id = State()
    agent_id = State()
    amount = State()
    description = State()


class ReputationRequestState(StatesGroup):
    about = State()


class ReputationRequestAcceptState(StatesGroup):
    id = State()
    comment = State()


class CheckState(StatesGroup):
    search = State()