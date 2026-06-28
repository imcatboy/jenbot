from aiogram.fsm.state import State, StatesGroup


class ReportState(StatesGroup):
    reason = State()
    attachments = State()
    accused_user_id = State()
    username = State()


class AdminReportState(StatesGroup):
    report_status = State()


class ScamReportState(StatesGroup):
    description = State()
    contact_info = State()
    attachments = State()


class AnswerScamReportState(StatesGroup):
    comment = State()


class ReviewState(StatesGroup):
    rating = State()
    message = State()


class ExternalDealState(StatesGroup):
    buyer_id = State()
    seller_id = State()
    second_participant_id = State()
    agent_id = State()
    deal_amount = State()
    payment = State()
    description = State()


class ReputationRequestState(StatesGroup):
    about = State()


class ReputationRequestDeclineState(StatesGroup):
    comment = State()


class CheckState(StatesGroup):
    search = State()


class ReviewDeleteState(StatesGroup):
    comment = State()
