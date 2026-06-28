import zoneinfo

from typing import Annotated, Dict, Type, get_args, get_origin, List
from aiogram.filters import CommandObject
from datetime import datetime, timezone
from pydantic.fields import FieldInfo
from pydantic import BaseModel
from typing import Optional
from html import escape

from domain.objects import entities, types


COMMAND_ARGUMENTS_ERROR = '<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> Ошибка! Команда требует аргументов.\n\n<code>{0}</code>'
COMMAND_ARGUMENTS_COUNT_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Неверное число аргументов.\n\n<code>{0}</code>'
COMMAND_ARGUMENTS_VALIDATION_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Ошибка валидации!\n\n<code>{0}</code>'
USER_NOT_ALLOWED_TO_ACTION = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы не имеете прав на выполнение этого действия.'
SENDER_CHAT_NOT_ALLOWED = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Бот недоступен при отправке сообщений '
    "от имени канала или анонимно. Отправьте команду от своего аккаунта."
)
VIOLATIONS_OTHER_USER_FORBIDDEN = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Просмотр нарушений другого пользователя доступен только модераторам и администраторам.'
BAN_USER_SUCCESS = '<tg-emoji emoji-id="5282796481156262136">🔒</tg-emoji> Пользователь {0} заблокирован до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>'
BAN_USER_WITHOUT_EXPIRES_AT_SUCCESS = '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Пользователь {0} заблокирован\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>'
USER_NOT_FOUND = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пользователь {0} не найден.'
)
CHECK_USER_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Введите реквизит, @username или Telegram ID пользователя, чтобы проверить его репутацию.'
REPLY_MESSAGE_OR_SEARCH_REQUIRED = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> В команде <code>/check</code> нужно указать реквизит, @username или Telegram ID пользователя или ответить на сообщение пользователя, чтобы проверить его репутацию.'
UNBAN_USER_SUCCESS = '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Пользователь {0} разблокирован.'
MUTE_USER_SUCCESS = '<tg-emoji emoji-id="5282796481156262136">🔒</tg-emoji> Пользователь {0} замьючен до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>'
MUTE_USER_WITHOUT_EXPIRES_AT_SUCCESS = '<tg-emoji emoji-id="5282796481156262136">🔒</tg-emoji> Пользователь {0} замьючен\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>'
DEAL_USER_NOT_FOUND = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пользователь {0} не найден. Вероятно, он не общался с ботом.'
UNMUTE_USER_SUCCESS = (
    '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Пользователь {0} размьючен.'
)
DEAL_NOT_PENDING = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Сделка не находится в состоянии выполнения.'
USER_IS_NOT_PARTICIPANT = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы не являетесь участником этой сделки.'
EXTERNAL_DEAL_NOT_BLOCKED = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> <b>Действие недоступно</b>. '
    "Разрешить или закрыть можно только сделку в статусе «истекла» или «спор»."
)
REVIEW_DELETE_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Вы уверены, что хотите удалить отзыв?'
REVIEW_DELETE_COMMENT_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите причину удаления отзыва (до 1024 символов).'
WARN_USER_SUCCESS = '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Пользователь {0} предупрежден до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>'
WARN_USER_WITHOUT_EXPIRES_AT_SUCCESS = '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Пользователь {0} предупрежден\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>'
REPORT_ACCUSED_USER_ID_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Введите ID пользователя, которого вы хотите обвинить в нарушении.'
CANNOT_USE_ACTION_ON_USER = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы не можете использовать это действие на этом пользователе.'
EXTERNAL_DEAL_FIRST_ROLE_MESSAGE = (
    '<tg-emoji emoji-id="5336966966630459544">🛡️</tg-emoji> <b>Регистрация сделки</b>\n\n'
    "Бот <b>не переводит деньги</b> — он фиксирует условия и закрепляет "
    "<b>сумму доверенности</b> за сделкой. Если во время сделки будет подтверждено мошенничество, "
    "пострадавшая сторона может рассчитывать на возмещение в пределах этой суммы.\n\n"
    "<b>Как это работает</b>\n"
    "1. Вы заполняете данные, создаётся <b>черновик</b>\n"
    "2. Участник с доверенностью <b>принимает</b> или отклоняет сделку\n"
    "3. После принятия сумма блокируется до завершения, отмены или решения администрации\n\n"
    '<tg-emoji emoji-id="5335062818649586072">👤</tg-emoji> Выберите <b>вашу роль</b> в сделке.\n'
    "Посредником может быть только <b>гарант</b>."
)
EXTERNAL_DEAL_SELLER_MESSAGE = (
    '<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> <b>Продавец</b>\n\n'
    "Введите @username или Telegram ID человека, который <b>продаёт</b> товар или услугу.\n\n"
    '<tg-emoji emoji-id="5334669777602389618">⌨️</tg-emoji> <i>У участника должен быть диалог с ботом — '
    "попросите его написать /start.</i>"
)
EXTERNAL_DEAL_BUYER_MESSAGE = (
    '<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> <b>Покупатель</b>\n\n'
    "Введите @username или Telegram ID человека, который <b>покупает</b>.\n\n"
    '<tg-emoji emoji-id="5334669777602389618">⌨️</tg-emoji> <i>У участника должен быть диалог с ботом — '
    "попросите его написать /start.</i>"
)
EXTERNAL_DEAL_SECOND_PARTICIPANT_MESSAGE = (
    '<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> <b>Второй участник</b>\n\n'
    "Введите @username или Telegram ID второго участника сделки "
    "(продавца, если вы покупатель, или наоборот).\n\n"
    '<tg-emoji emoji-id="5334669777602389618">⌨️</tg-emoji> <i>У участника должен быть диалог с ботом.</i>'
)
EXTERNAL_DEAL_PAYMENT_MESSAGE = (
    '<tg-emoji emoji-id="5282858672282705921">⚪</tg-emoji> <b>Оплата посреднику</b>\n\n'
    "Укажите условия оплаты за услугу посредника (конкретная сумма или предмет) — "
    "<b>до 255 символов</b>.\n\n"
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> <i>Обсудите оплату с посредником заранее. '
    "Можно пропустить, если посредника нет или оплата не предусмотрена.</i>"
)
DEAL_USER_NOT_GUARANTOR = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> <b>Нет участника с доверенностью</b>\n\n'
    "Среди указанных участников нет гаранта или депозитчика с доверенностью. "
    "Проверьте карточки через /check или пригласите гаранта."
)
EXTERNAL_DEAL_DESCRIPTION_MESSAGE = (
    '<tg-emoji emoji-id="5334669777602389618">⌨️</tg-emoji> <b>Описание сделки</b>\n\n'
    "Опишите, <b>что продаётся / покупается</b>, на каких условиях и что считается "
    "выполнением обязательств — <b>до 255 символов</b>.\n\n"
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <i>Чем точнее описание, '
    "тем проще разобрать спор, если он возникнет.</i>"
)
EXTERNAL_DEAL_AMOUNT_MESSAGE = (
    '<tg-emoji emoji-id="5280764411869438260">💎</tg-emoji> <b>Сумма сделки</b>\n\n'
    "Доступно для покрытия: <b>{0}</b> из {1}.\n\n"
    "Введите <b>полную стоимость сделки</b> в рублях.\n\n"
    '<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> Если сумма сделки больше доступной '
    "доверенности, при мошенничестве будет возмещена <b>только доступная часть</b> — "
    "стороны должны это понимать.\n\n"
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <i>Сумма должна соответствовать '
    "реальной стоимости, иначе гарант может отклонить сделку.</i>"
)
EXTERNAL_DEAL_WITHOUT_WARRANTY_REPUTATION_USER = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> <b>Нет участника с доверенностью</b>\n\n'
    "Среди участников нет гаранта или депозитчика. Сделку нельзя продолжить.\n\n"
    "Проверьте собеседников через /check или добавьте гаранта / посредника."
)
EXTERNAL_DEAL_AGENT_MESSAGE = (
    '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> <b>Посредник-гарант</b>\n\n'
    "Введите @username или Telegram ID <b>гаранта</b>, который будет посредником.\n\n"
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> <i>Необязательно — пропустите, '
    "если доверенность есть у продавца или покупателя.</i>\n\n"
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Депозитчик <b>не может</b> быть посредником.'
)
EXTERNAL_DEAL_ERROR_MESSAGE = (
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <b>Черновик создан</b>, '
    "но не удалось отправить его держателю доверенности.\n\n"
    "Обратитесь к администрации через /report."
)
EXTERNAL_DEAL_STARTED_MESSAGE = (
    '<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> <b>Сделка начата</b>\n\n'
    "Доверенность закреплена. Для завершения или отмены нужно "
    "<b>подтверждение и продавца, и покупателя</b>."
)
EXTERNAL_DEAL_DELETED_MESSAGE = (
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Черновик сделки удалён.'
)
EXTERNAL_DEAL_STATUS_CHANGED_MESSAGE = (
    '<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> Статус активной сделки изменён.'
)
REVIEW_ALREADY_EXISTS = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы уже оставляли отзыв на этого пользователя, один пользователь может оставить только один отзыв на другого пользователя.'
ACCESS_DENIED = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> У вас нет доступа к этому действию.'
STATE_VALIDATION_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Ошибка введённого значения, попробуйте ещё раз.'
SET_SETTING_SUCCESS = '<tg-emoji emoji-id="5280806004332730789">⚙️</tg-emoji> Настройка <b>{0}</b> установлена.'
UNWARN_USER_SUCCESS = '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Предупреждение стало неактивным.'
OBJECT_NOT_FOUND = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Запрашиваемый объект не найден.'
OBJECT_ALREADY_EXISTS = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Объект с такими данными уже существует.'
ADD_MODERATOR_SUCCESS = '<tg-emoji emoji-id="5280572564270260024">✈️</tg-emoji> Пользователь {0} стал модератором.'
REMOVE_MODERATOR_SUCCESS = '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Пользователь {0} стал обычным пользователем.'
SUBSCRIPTION_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы не подписаны на каналы, необходимые для использования бота. Пожалуйста, подпишитесь на каналы и попробуйте снова.'
START_MESSAGE = (
    '<tg-emoji emoji-id="5283186855028761775">👏</tg-emoji> <b>Добро пожаловать!</b>\n\n'
    "Я — бот <b>Женяши</b>. Помогаю проверять людей на безопасность перед сделкой: "
    "гарантов, депозитчиков, скамеров и обычных участников.\n\n"
    "<b>Быстрая проверка в любом чате</b>\n"
    "Введите <code>@{bot_username} (@username / Telegram ID / реквизит)</code>, "
    "выберите результат и отправьте карточку репутации собеседнику или используйте команду "
    "<code>/check (реквизит, @username, Telegram ID)</code> в любом чате с ботом\n\n"
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Полный список команд — <code>/help</code>\n\n'
    '<tg-emoji emoji-id="5280548821691046193">🌐</tg-emoji> Новости и объявления — в нашем канале.\n\n'
    '<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> <i>При использовании бота вы соглашаетесь с '
    '<a href="https://docs.google.com/document/d/e/2PACX-1vTvjrD2GuDtUTV8mQ7VsZRnf0QnL90fBS4Nvk7LP7hBvLDXwTHtKhTAkHlm0E0NjehSFjMC4wz93X-l/pub">пользовательским соглашением</a></i>'
)
REVIEW_DELETED = (
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Отзыв успешно удален.'
)
HELP_MESSAGE = (
    '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> <b>Справка по командам</b>\n\n'
    "<b>Основные команды</b>\n"
    '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <code>/check (реквизит, @username, Telegram ID)</code> — узнать репутацию пользователя\n'
    '<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> <code>t.me/{bot_username}?start=check_username</code> — проверка по ссылке (username или Telegram ID)\n'
    '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> <code>/me</code> — посмотреть свою репутацию\n'
    '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji> <code>/review (@username, Telegram ID)</code> — оставить отзыв о пользователе\n'
    '<tg-emoji emoji-id="5282962236829115303">⚠️</tg-emoji> <code>/scam</code> — подать жалобу на скамера с доказательствами\n'
    '<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> <code>/reputation</code> — подать заявку на статус чистого пользователя\n'
    '<tg-emoji emoji-id="5283186855028761775">👏</tg-emoji> <code>/deal</code> — зарегистрировать сделку с закреплением доверенности\n'
    '<tg-emoji emoji-id="5280572564270260024">✈️</tg-emoji> <code>/report</code> — обратиться по нарушению, разбану или с вопросом\n\n'
    '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji> <code>/myreviews</code> — посмотреть оставленные отзывы\n'
    "<b>Inline-режим</b>\n"
    "В любом чате: <code>@{bot_username} @username</code> — проверка без перехода в бота.\n\n"
    "Стремитесь к максимальной безопасности — проверяйте собеседника перед сделкой.\n\n"
    '<tg-emoji emoji-id="5280806004332730789">⚙️</tg-emoji> Технические вопросы и предложения — @imcatboy'
)
USER_IS_SELF = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы не можете оставить отзыв на самого себя.'
REPORT_TYPE_MESSAGE = (
    '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Выберите тип обращения.'
)
REPORT_REASON_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите причину обращения (до 1024 символов).'
REPORT_ATTACHMENTS_MESSAGE = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Прикрепите фото или видео до 40 МБ. '
    "Можно отправлять несколькими сообщениями."
)
REVIEW_MESSAGE_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите сообщение для отзыва (до 255 символов).'
REVIEW_SUCCESS = (
    '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji> Отзыв успешно оставлен.'
)
USER_NOT_HAS_REPUTATION_USER = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Указанный пользователь не имеет положительной репутации, что обязательно для получения отзыва.'
REVIEW_RATING_MESSAGE = (
    '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Выберите оценку от 1 до 5.'
)
REPORT_ATTACHMENTS_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пожалуйста, отправьте фото или видео.'
REPORT_USERNAME_NOT_FOUND = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пользователь {0} не найден. Попробуйте ввести его ID.'
REPORT_USERNAME_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Я ранее не видел этого пользователя. Введите его username, если есть, иначе пропустите.'
THROTTLE_ERROR = (
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Пожалуйста, не спамьте.'
)
REPORT_SUCCESS = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Отправлено успешно. В случае ответа вам будет отправлено уведомление.'
REPORT_WITH_ATTACHMENTS_SUCCESS = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Отправлено успешно с {0} медиа. В случае ответа вам будет отправлено уведомление.'
STATE_CANCELLED = (
    '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Действие отменено.'
)
REPORT_ALREADY_PENDING = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вы уже имеете незавершенное обращение. Пожалуйста, дождитесь его обработки.'
USERNAME_OR_REPLY_TO_USER_REQUIRED = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Имя пользователя или ответ на сообщение является обязательным.'
USER_IS_SCAMMER = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пользователь является скамером.'
USER_IS_NOT_GUARANTOR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пользователь не является гарантом.'
NOT_ENOUGH_AMOUNT = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> У пользователя недостаточно свободных средств по доверенности.'
DEAL_NOT_DRAFT = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> <b>Сделка уже начата</b>\n\n'
    "Принять или отклонить можно только черновик."
)
SET_REPUTATION_ROLE_MESSAGE = (
    '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Выберите роль пользователя.'
)
DISCLAIMER_MESSAGE = '<tg-emoji emoji-id="5282962236829115303">⚠️</tg-emoji> <b>ВАЖНО!</b> <i>Не доверяйте сообщениям бота, которые не были вызваны вами лично, так как они могут быть подделаны.</i>'
SET_REPUTATION_DESCRIPTION_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите описание для репутации (до 255 символов).'
REPORT_COMMENT_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите комментарий к обращению (до 1024 символов).'
REPUTATION_REQUEST_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Введите описание, которое будет отображаться в карточке репутации (до 255 символов).'
REPUTATION_REQUEST_SUCCESS = '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Запрос на репутацию успешно отправлен.'
REPUTATION_REQUEST_EXISTS = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> У вас уже есть незавершенный запрос на репутацию. Пожалуйста, дождитесь его обработки.'
REPUTATION_REQUEST_ACCEPTED = '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Ваш запрос на репутацию принят.'
REPUTATION_REQUEST_REJECTED = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Ваш запрос на репутацию отклонен.\n\n<b>Причина</b>\n<blockquote>{0}</blockquote>'
REPUTATION_REQUEST_COMMENT_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите комментарий к запросу на репутацию (до 1024 символов).'
REPUTATION_REQUEST_COMMENT_SUCCESS = '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Комментарий успешно отправлен.'
REPORT_STATUS_UPDATED = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Статус обращения успешно изменен.'
ADD_BAN_WORD_SUCCESS = '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Слово <b>{0}</b> успешно добавлено в список запрещённых.'
REMOVE_BAN_WORD_SUCCESS = '<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Слово <b>{0}</b> успешно удалено из списка запрещённых.'
BAN_WORD_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> {0} использовал запрещённое слово <tg-spoiler>{1}</tg-spoiler>.'
VIOLATIONS_COUNT_OTHER_USER_FORBIDDEN = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Просмотр статистики нарушений только других модераторов и администраторов.'
UNKNOWN_ERROR = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Произошла неизвестная ошибка. Пожалуйста, сообщите об этом администрации.'
SCAM_REPORT_DESCRIPTION_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите описание жалобы, в случае принятия жалобы эта информация будет опубликована в карточке скамера (до 1024 символов).'
SCAM_REPORT_CONTACT_INFO_MESSAGE = '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Введите всю контактную информацию, которую вы можете предоставить о скамере (до 255 символов).'
SCAM_REPORT_COUNT_MESSAGE = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> У вас уже есть несколько жалоб на скам. Пожалуйста, дождитесь их рассмотрения.'
SCAM_REPORT_ATTACHMENTS_MESSAGE = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Прикрепите фото или видео до 40 МБ с доказательствами. '
    "Можно отправлять несколькими сообщениями."
)
ATTACHMENTS_RECEIVED = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Добавлено <b>{0}</b>. '
    "Всего <b>{1}</b> из {2}."
)
ATTACHMENTS_DUPLICATES_SUFFIX = " (<b>{0}</b> уже были добавлены)"
ATTACHMENTS_DUPLICATES_ONLY = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Все <b>{0}</b> файлов уже в списке. '
    "Всего <b>{1}</b>."
)
ATTACHMENTS_LIMIT = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Максимум <b>{0}</b> файлов. '
    "Нажмите «Готово» или «Очистить»."
)
ATTACHMENTS_CLEARED = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Список вложений очищен. '
    "Отправьте фото или видео."
)
ATTACHMENTS_PREVIEW_CAPTION = (
    '<tg-emoji emoji-id="5282823947472118926">📎</tg-emoji> Превью <b>{0}</b> файлов'
)
ATTACHMENTS_PREVIEW_EMPTY = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Нет файлов для просмотра.'
)
ATTACHMENTS_DONE_EMPTY = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Сначала прикрепите хотя бы один файл.'
ATTACHMENTS_UNAVAILABLE = (
    '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Вложения недоступны.'
)
ATTACHMENTS_SKIP_FORBIDDEN = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пропуск недоступен — вы уже добавили файлы.'
PLEASE_WAIT_MESSAGE = (
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Пожалуйста, подождите...'
)
ATTACHMENTS_PREVIEW_LOADING = (
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Отправляю превью...'
)
REPORT_SUBMITTING = (
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Отправляю обращение...'
)
SCAM_REPORT_SUBMITTING = (
    '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Отправляю жалобу...'
)
CHAT_NOT_FOUND = '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> У одного из пользователей с ботом не начат или заблокирован чат.'
TRACKER_ADDED = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Трекер на пользователя {0} успешно добавлен.'
TRACKER_REMOVED = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Трекер на пользователя {0} успешно удален.'
TRACKER_MESSAGE = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Новое <a href="{0}">сообщение</a> от пользователя {1}.'
MODERATORS_MENTIONED = (
    '<tg-emoji emoji-id="5280572564270260024">✈️</tg-emoji> Отчёт отправлен модераторам.'
)
MANY_REPUTATION_USERS = '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Найдено несколько пользователей. Выберите пользователя из списка.'
VIOLATIONS = {
    types.ViolationType.WARN: '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Предупреждение',
    types.ViolationType.MUTE: '<tg-emoji emoji-id="5282796481156262136">🔒</tg-emoji> Мьют',
    types.ViolationType.BAN: '<tg-emoji emoji-id="5282796481156262136">🔒</tg-emoji> Бан',
}
USER_ROLES = {
    types.UserRole.ADMIN: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Админ',
    types.UserRole.MODERATOR: '<tg-emoji emoji-id="5280572564270260024">✈️</tg-emoji> Модератор',
    types.UserRole.USER: '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Пользователь',
}
CHAT_ACTIONS = {
    types.ChatAction.UNMUTE: '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Размьют',
    types.ChatAction.UNWARN: '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Снятие предупреждения',
    types.ChatAction.UNBAN: '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Снятие бана',
}
REPORT_TYPES = {
    types.ReportType.UNBAN: '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Снятие нарушения',
    types.ReportType.VIOLATION: '<tg-emoji emoji-id="5283215884712716244">🚫</tg-emoji> Нарушение',
    types.ReportType.FEEDBACK: '<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Обратная связь',
    types.ReportType.OTHER: '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Другое',
}
REPORT_STATUSES = {
    types.ReportStatus.PENDING: '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Ожидает рассмотрения',
    types.ReportStatus.APPROVED: '<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Принято',
    types.ReportStatus.REJECTED: '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Отклонено',
    types.ReportStatus.CANCELLED: '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Отменено',
}
REPUTATION_ROLES = {
    types.UserReputationRole.SCAMMER: '<tg-emoji emoji-id="5282962236829115303">⚠️</tg-emoji> Скамер',
    types.UserReputationRole.GUARANTOR: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Гарант',
    types.UserReputationRole.BIG_GUARANTOR: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Большой гарант',
    types.UserReputationRole.SMALL_GUARANTOR: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Младший гарант',
    types.UserReputationRole.DEPOSITOR: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Депозитчик',
    types.UserReputationRole.ADMIN: '<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Админ',
    types.UserReputationRole.CLEAN_USER: '<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Чистый пользователь',
}
INLINE_REPUTATION_ROLES = {
    types.UserReputationRole.SCAMMER: "Скамер",
    types.UserReputationRole.GUARANTOR: "Гарант",
    types.UserReputationRole.BIG_GUARANTOR: "Большой гарант",
    types.UserReputationRole.SMALL_GUARANTOR: "Младший гарант",
    types.UserReputationRole.DEPOSITOR: "Депозитчик",
    types.UserReputationRole.ADMIN: "Админ",
    types.UserReputationRole.CLEAN_USER: "Чистый пользователь",
}
CHAT_EVENTS = {
    types.ChatEvent.JOIN: '<tg-emoji emoji-id="5283186855028761775">👏</tg-emoji> Вход',
    types.ChatEvent.LEAVE: '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Выход',
    types.ChatEvent.BAN_WORD: '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Запрещённое слово',
}
DEAL_STATUSES = {
    types.DealStatus.DRAFT: '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Черновик',
    types.DealStatus.PENDING: '<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> Выполняется',
    types.DealStatus.EXPIRED: '<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Истекла',
    types.DealStatus.COMPLETED: '<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Завершена',
    types.DealStatus.CANCELLED: '<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Отменена',
    types.DealStatus.REJECTED: '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Спор (жалоба)',
}
DEAL_CONDITIONS = {
    types.DealCondition.ACCEPTED: '<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Закончил сделку',
    types.DealCondition.COMPLAINT: '<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Подал жалобу',
    types.DealCondition.CANCELLED: '<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Отменил сделку',
}
HOMOGLYPHS = str.maketrans("ayBkKMnoPpCcTyXxeE", "ауВкКМноРрСсТуХхеЕ")


def _usage_label_for_field(name: str, field_info: FieldInfo) -> str:
    if field_info.description:
        return field_info.description

    ann = field_info.annotation
    nested = _description_from_annotation(ann)
    return nested if nested is not None else name


def _description_from_annotation(annotation: object) -> str | None:
    if annotation is None or annotation is type(None):
        return None

    origin = get_origin(annotation)

    if origin is Annotated:
        args = get_args(annotation)

        for meta in args[1:]:
            if isinstance(meta, FieldInfo) and meta.description:
                return meta.description

        if args:
            return _description_from_annotation(args[0])

        return None

    if origin is not None:
        for arg in get_args(annotation):
            if arg is type(None):
                continue

            found = _description_from_annotation(arg)

            if found is not None:
                return found

    return None


def format_reputation_user(
    reputation: entities.ReputationUserWithRelationsEntity,
) -> str:
    display_parts = []

    for user in reputation.users:
        if user.usernames:
            display_parts.extend(
                [f"@{username.username}" for username in user.usernames]
            )
        else:
            display_parts.append(str(user.telegram_id))

    return " ".join(display_parts)


def format_from_user(username: Optional[str], telegram_id: int) -> str:
    if username:
        return f"@{username} [<code>{telegram_id}</code>]"

    return f"<code>{telegram_id}</code>"


def format_user_handle(user: entities.UserEntity) -> str:
    if user.usernames:
        return f"{", ".join([f"@{username.username}" for username in user.usernames])} [<code>{user.telegram_id}</code>]"

    return f"<code>{user.telegram_id}</code>"


def format_date(date: datetime) -> str:
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    moscow_timezone = zoneinfo.ZoneInfo("Europe/Moscow")
    return date.astimezone(moscow_timezone).strftime("%d.%m.%Y %H:%M")


def format_contact_info(contact_info: str) -> str:
    return " ".join(
        [f"<code>{word}</code>" for word in escape(contact_info).split(" ")]
    )


def get_command_usage(command: CommandObject, model: Type[BaseModel]) -> str:
    fields = []

    for name, field_info in model.model_fields.items():
        if field_info.is_required():
            fields.append(f"[{_usage_label_for_field(name, field_info)}]")
        else:
            fields.append(f"({_usage_label_for_field(name, field_info)})")

    return f"/{command.command} {' '.join(fields)}"


def get_count_word(
    count: int, first_word: str, second_word: str, third_word: str
) -> str:
    abs_count = abs(count)

    hundred_remainder = abs_count % 100
    ten_remainder = abs_count % 10

    if 11 <= hundred_remainder <= 14:
        return third_word

    if ten_remainder == 1:
        return first_word

    if 2 <= ten_remainder <= 4:
        return second_word

    return third_word


def get_ban_user_success_message(
    user: entities.UserEntity,
    expires_at: Optional[datetime],
    reason: str,
) -> str:
    if expires_at:
        return BAN_USER_SUCCESS.format(
            format_user_handle(user),
            format_date(expires_at),
            escape(reason),
        )
    else:
        return BAN_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            format_user_handle(user), escape(reason)
        )


def get_mute_user_success_message(
    user: entities.UserEntity,
    expires_at: Optional[datetime],
    reason: str,
) -> str:
    if expires_at:
        return MUTE_USER_SUCCESS.format(
            format_user_handle(user),
            format_date(expires_at),
            escape(reason),
        )
    else:
        return MUTE_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            format_user_handle(user), escape(reason)
        )


def get_warn_user_success_message(
    user: entities.UserEntity,
    expires_at: Optional[datetime],
    reason: str,
) -> str:
    if expires_at:
        return WARN_USER_SUCCESS.format(
            format_user_handle(user),
            format_date(expires_at),
            escape(reason),
        )
    else:
        return WARN_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            format_user_handle(user), escape(reason)
        )


def get_violations_message(
    violations: List[entities.ChatViolationWithUserEntity],
) -> str:
    message = (
        '<tg-emoji emoji-id="5283215884712716244">🔨</tg-emoji> <b>Нарушения</b>\n\n'
    )
    active_violations = [violation for violation in violations if violation.is_active]
    inactive_violations = [
        violation for violation in violations if not violation.is_active
    ]

    if active_violations:
        message += '<tg-emoji emoji-id="5280622076653245714">🟢</tg-emoji> <b>Активные нарушения</b>\n'

    for violation in active_violations:
        message += f'<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> #<code>{violation.id}</code> <b>{VIOLATIONS[violation.type]}</b>\n'
        message += f"<blockquote>"
        message += f"{escape(violation.reason)}\n"
        message += f"Выдан {format_user_handle(violation.applied_by_user)}\n"
        message += f"От {format_date(violation.created_at)}"

        if violation.expires_at:
            message += f"\nДо {format_date(violation.expires_at)}"

        message += "</blockquote>\n\n"

    if inactive_violations:
        message += '<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> <b>Неактивные нарушения</b>\n'

    for violation in inactive_violations:
        message += f'<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> #<code>{violation.id}</code> <b>{VIOLATIONS[violation.type]}</b>\n'
        message += f"<blockquote>"
        message += f"{escape(violation.reason)}\n"
        message += f"Выдан {format_user_handle(violation.applied_by_user)}\n"
        message += f"От {format_date(violation.created_at)}"

        if violation.expires_at:
            message += f"\nДо {format_date(violation.expires_at)}"

        message += "</blockquote>\n\n"

    if not violations:
        message += "<i>Нет нарушений</i>"

    return message


def get_audit_message(violation: entities.ChatViolationWithUserEntity) -> str:
    message = f"<b>{VIOLATIONS[violation.type]}</b>\n\n"
    message += f"Выдан: {format_user_handle(violation.applied_by_user)}\n"

    if violation.telegram_chat_id:
        message += f"В чате: <code>{violation.telegram_chat_id}</code>\n"

    message += f"Пользователь: {format_user_handle(violation.user)}\n"
    message += f"От: {format_date(violation.created_at)}"

    if violation.expires_at:
        message += f"\nДо: {format_date(violation.expires_at)}"

    message += f"\n\n<blockquote>{escape(violation.reason)}</blockquote>"

    return message


def get_action_audit_message(
    action: types.ChatAction,
    user: entities.UserEntity,
    applied_by_user: entities.UserEntity,
    violation_id: Optional[int] = None,
) -> str:
    message = f"<b>{CHAT_ACTIONS[action]}</b>\n\n"
    message += f"Пользователь: {format_user_handle(user)}\n"
    message += f"Выполнил: {format_user_handle(applied_by_user)}\n"

    if violation_id:
        message += f"Нарушение: <code>{violation_id}</code>"

    return message


def get_event_audit_message(
    event: types.ChatEvent,
    user: entities.UserEntity,
    telegram_chat_id: int,
    comment: Optional[str] = None,
) -> str:
    message = f"<b>{CHAT_EVENTS[event]}</b>\n\n"
    message += f"Пользователь: {format_user_handle(user)}\n"
    message += f"В чате: <code>{telegram_chat_id}</code>\n"

    if comment:
        message += f"\n<b>Комментарий:</b>"
        message += f"<blockquote>{escape(comment)}</blockquote>"

    return message


def get_moderators_message(moderators: List[entities.UserEntity]) -> str:
    message = (
        '<tg-emoji emoji-id="5280572564270260024">✈️</tg-emoji> <b>Модераторы</b>\n\n'
    )

    for moderator in moderators:
        if moderator.usernames:
            message += f"@{moderator.usernames[0].username} "

    return message


def get_report_message(report: entities.ReportWithUserEntity) -> str:
    message = f"<b>{REPORT_TYPES[report.type]}</b>\n\n"
    message += f"Статус: <b>{REPORT_STATUSES[report.status]}</b>\n"
    message += f"Пользователь: {format_user_handle(report.user)}\n"

    if report.accused_user:
        message += f"Обвиняемый: {format_user_handle(report.accused_user)}\n"
    if report.applied_by_user:
        message += f"Изменил статус: {format_user_handle(report.applied_by_user)}\n"

    message += f"Дата: {format_date(report.created_at)}\n"

    if report.created_at != report.updated_at:
        message += f"Обновлено: {format_date(report.updated_at)}\n"

    message += "\n<b>Причина:</b>\n"
    message += f"<blockquote>{escape(report.reason)}</blockquote>\n\n"

    if report.admin_comment:
        message += "<b>Комментарий:</b>\n"
        message += f"<blockquote>{escape(report.admin_comment)}</blockquote>\n\n"

    return message


def get_scam_report_message(scam_report: entities.ScamReportWithRelationsEntity) -> str:
    message = f"#<code>{scam_report.id}</code> <b>Жалоба на скамера</b>\n\n"
    message += f"Статус: <b>{REPORT_STATUSES[scam_report.status]}</b>\n"
    message += f"От пользователя: {format_user_handle(scam_report.user)}\n"
    message += f"Дата жалобы: {format_date(scam_report.created_at)}\n\n"
    message += f"<b>Описание</b>\n"
    message += f"<blockquote>{escape(scam_report.description)}</blockquote>\n\n"

    if scam_report.contact_info:
        message += f"<b>Контактная информация</b>\n"
        message += f"<blockquote>{format_contact_info(scam_report.contact_info)}</blockquote>\n\n"

    if scam_report.comment:
        message += f"<b>Комментарий модератора</b>\n"
        message += f"<blockquote>{escape(scam_report.comment)}</blockquote>\n\n"

    if scam_report.applied_by_user:
        message += f"Обработал: {format_user_handle(scam_report.applied_by_user)}"

    return message


def get_check_success_message(
    reputation: entities.ReputationUserWithRelationsEntity,
) -> str:
    message = f"<b>{REPUTATION_ROLES[reputation.role]}</b>\n\n"

    for user in reputation.users:
        message += f'<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> {format_user_handle(user)}\n'

    if reputation.user_details:
        message += f'\n<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> <b>Реквизиты</b>\n'

    for detail in reputation.user_details:
        if not detail.is_public:
            continue

        message += f'<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <b>{detail.name}</b>: <code>{detail.value}</code>\n'

    if reputation.description:
        message += (
            f'\n<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> <b>Описание</b>\n'
        )
        message += f"<blockquote>{escape(reputation.description)}</blockquote>\n\n"

    if reputation.role != types.UserReputationRole.SCAMMER:
        if reputation.about:
            message += f'\n<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> <b>Комментарий пользователя</b>\n'
            message += f"<blockquote>{escape(reputation.about)}</blockquote>\n\n"

        if reputation.amount > 0:
            message += f'<tg-emoji emoji-id="5283212259760315829">🔎</tg-emoji> Имеет доверенность на сумму <b>{reputation.amount}</b> {get_count_word(reputation.amount, "рубль", "рубля", "рублей")}\n'
        if reputation.review_count > 0:
            message += f'<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji> Имеет <b>{reputation.review_count}</b> {get_count_word(reputation.review_count, "отзыв", "отзыва", "отзывов")}\n'
        if reputation.applied_report_count > 0:
            message += f'<tg-emoji emoji-id="5283057370354719831">🛡️</tg-emoji> Опубликовано <b>{reputation.applied_report_count}</b> {get_count_word(reputation.applied_report_count, "жалоба", "жалобы", "жалоб")} на скам\n'

    if reputation.search_count > 0:
        message += f'<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Искали <b>{reputation.search_count}</b> {get_count_word(reputation.search_count, "раз", "раза", "раз")}\n'

    message += f"\n{DISCLAIMER_MESSAGE}"
    message += f'\n\n<tg-emoji emoji-id="5280834024699370557">📅</tg-emoji> <i>{format_date(datetime.now())}</i>'
    return message


def get_check_error_message(search: Optional[str] = None) -> str:
    message = f'<b><tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Неизвестный пользователь</b>\n\n'

    if search:
        message += f'<tg-emoji emoji-id="5282959170222466892">➕</tg-emoji> Подходящей записи по запросу <i>{escape(search)}</i> не найдено.\n\n'
    else:
        message += '<tg-emoji emoji-id="5282953552405241953">📂</tg-emoji> Такой пользователь не найден.\n\n'

    message += f"{DISCLAIMER_MESSAGE}\n\n"
    message += f'<tg-emoji emoji-id="5280834024699370557">📅</tg-emoji> <i>{format_date(datetime.now())}</i>'
    return message


def get_report_updated_message(report: entities.ReportWithUserEntity) -> str:
    message = f"#<code>{report.id}</code> <b>{REPORT_TYPES[report.type]}</b>\n\n"
    message += f"<blockquote>{escape(report.reason)}</blockquote>\n\n"
    message += f"<b>{REPORT_STATUSES[report.status]}</b>\n\n"

    if report.admin_comment:
        message += "<b>Ответ администратора</b>\n"
        message += f"<blockquote>{escape(report.admin_comment)}</blockquote>\n\n"

    return message


def get_scam_report_updated_message(
    scam_report: entities.ScamReportWithRelationsEntity,
) -> str:
    message = f"#<code>{scam_report.id}</code> <b>Жалоба на скамера</b>\n\n"
    message += f"<blockquote>{escape(scam_report.description)}</blockquote>\n\n"
    message += f"<b>{REPORT_STATUSES[scam_report.status]}</b>\n\n"

    if scam_report.comment:
        message += "<b>Комментарий модератора</b>\n"
        message += f"<blockquote>{escape(scam_report.comment)}</blockquote>\n\n"

    return message


def get_violations_count_message(
    user: entities.UserEntity,
    violations_count: Dict[types.ViolationType, int],
    applied_scam_reports_count: int,
    start_date: Optional[datetime],
) -> str:
    message = f'<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <b>Статистика нарушений {format_user_handle(user)}</b>\n\n'

    for violation_type, count in violations_count.items():
        message += f"<b>{VIOLATIONS[violation_type]}</b>: {count} шт.\n"

    if applied_scam_reports_count > 0:
        message += f'\n<tg-emoji emoji-id="5282962236829115303">⚠️</tg-emoji> <b>Рассмотрено жалоб на скам</b>: {applied_scam_reports_count} шт.\n'

    if start_date:
        message += f'\n<tg-emoji emoji-id="5280834024699370557">📅</tg-emoji> От: {format_date(start_date)}'

    return message


def get_reviews_message(
    reputation_user: entities.ReputationUserWithRelationsEntity,
    reviews: List[entities.ReviewWithAuthorEntity],
) -> str:
    message = f'<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> <b>Отзывы {format_user_handle(reputation_user.users[0])}</b>\n\n'

    for review in reviews:
        message += f"{format_user_handle(review.author)}\n"

        if review.author.reputation_user:
            message += f"<b>{REPUTATION_ROLES[review.author.reputation_user.role]}</b> ({review.author.reputation_user.review_count} {get_count_word(review.author.reputation_user.review_count, "отзыв", "отзыва", "отзывов")})\n"

        message += f"<blockquote>{escape(review.message)}</blockquote>\n"
        message += f"{review.rating * '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>'}\n"
        message += f'<tg-emoji emoji-id="5280834024699370557">📅</tg-emoji> <i>{format_date(review.created_at)}</i>\n\n'

    if len(reviews) == 0:
        message += "<i>Нет отзывов</i>"

    return message


def get_my_reviews_message(
    reviews: List[entities.ReviewWithSubjectEntity],
) -> str:
    message = f'<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> <b>Оставленные отзывы</b>\n\n'

    for index, review in enumerate(reviews):
        message += f"{index + 1}. {format_user_handle(review.subject_user)}\n"
        message += f"<b>{REPUTATION_ROLES[review.subject_user.reputation_user.role]}</b> ({review.subject_user.reputation_user.review_count} {get_count_word(review.subject_user.reputation_user.review_count, "отзыв", "отзыва", "отзывов")})\n"
        message += f"<blockquote>{escape(review.message)}</blockquote>\n"
        message += f"{review.rating * '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>'}\n"
        message += f'<tg-emoji emoji-id="5280834024699370557">📅</tg-emoji> <i>{format_date(review.created_at)}</i>\n\n'

    if len(reviews) == 0:
        message += "<i>Нет отзывов</i>"

    return message


def get_new_review_message(
    review: entities.ReviewWithRelationsEntity,
    deleted_by_user: Optional[entities.UserEntity] = None,
) -> str:
    message = f'<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> <b>Новый отзыв от {format_user_handle(review.author)}</b>\n\n'
    message += f"{format_user_handle(review.subject_user)}\n"
    message += f"<b>{REPUTATION_ROLES[review.subject_user.reputation_user.role]}</b> ({review.subject_user.reputation_user.review_count} {get_count_word(review.subject_user.reputation_user.review_count, "отзыв", "отзыва", "отзывов")})\n"
    message += f"<blockquote>{escape(review.message)}</blockquote>\n"
    message += (
        f"{review.rating * '<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>'}"
    )

    if deleted_by_user:
        message += f"\n\n<b>Отзыв был удален {format_user_handle(deleted_by_user)}</b>"

    return message


def get_review_deleted_message(
    review: entities.ReviewWithRelationsEntity, reason: Optional[str] = None
) -> str:
    message = f'<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> Ваш отзыв на {format_user_handle(review.subject_user)} был удален.'

    if reason:
        message += f"\n\n<b>Причина</b>\n<blockquote>{reason}</blockquote>"

    return message


def get_external_deal_message(deal: entities.ExternalDealWithRelationsEntity) -> str:
    message = f'<tg-emoji emoji-id="5283186855028761775">👏</tg-emoji> <b>Сделка #{deal.id}</b>\n\n'

    if deal.status == types.DealStatus.DRAFT:
        message += (
            '<tg-emoji emoji-id="5282953552405241953">🔎</tg-emoji> <b>Черновик</b> — '
            "ожидает подтверждения держателя доверенности.\n\n"
        )
    else:
        message += f"Статус: <b>{DEAL_STATUSES[deal.status]}</b>\n\n"

    message += "<b>Участники</b>\n"
    message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Продавец: {format_user_handle(deal.seller)}\n'
    message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Покупатель: {format_user_handle(deal.buyer)}\n'

    if deal.agent:
        message += f'<tg-emoji emoji-id="5335062818649586072">👤</tg-emoji> Посредник: {format_user_handle(deal.agent)}\n'

    message += "\n"

    if deal.status not in [types.DealStatus.DRAFT, types.DealStatus.PENDING]:
        if deal.seller_condition or deal.buyer_condition:
            message += "<b>Решения сторон</b>\n"
            if deal.seller_condition:
                message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Продавец: {DEAL_CONDITIONS[deal.seller_condition]}\n'
            if deal.buyer_condition:
                message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Покупатель: {DEAL_CONDITIONS[deal.buyer_condition]}\n'
            
            message += "\n"
    elif deal.status == types.DealStatus.PENDING:
        message += "<b>Решения сторон</b>\n"

        if deal.seller_condition:
            message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Продавец: {DEAL_CONDITIONS[deal.seller_condition]}\n'
        else:
            message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Продавец: <i>ещё не подтвердил</i>\n'
        
        if deal.buyer_condition:
            message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Покупатель: {DEAL_CONDITIONS[deal.buyer_condition]}\n'
        else:
            message += f'<tg-emoji emoji-id="5334734111917514054">👛</tg-emoji> Покупатель: <i>ещё не подтвердил</i>\n'
        
        message += "\n"

    message += "<b>Финансы</b>\n"
    message += (
        f'<tg-emoji emoji-id="5280764411869438260">💎</tg-emoji> Сумма сделки: <b>{deal.deal_amount}</b> '
        f'{get_count_word(deal.deal_amount, "рубль", "рубля", "рублей")}\n'
    )
    message += (
        f'<tg-emoji emoji-id="5280764411869438260">💎</tg-emoji> Закреплено доверенности: <b>{deal.refund_amount}</b> '
        f'{get_count_word(deal.refund_amount, "рубль", "рубля", "рублей")}\n'
    )

    if deal.deal_amount > deal.refund_amount:
        message += (
            '<tg-emoji emoji-id="5283081795833731867">🛡️</tg-emoji> <i>Покрытие меньше суммы сделки — '
            "при мошенничестве возмещение ограничено закреплённой суммой.</i>\n"
        )

    if deal.payment:
        message += f'<tg-emoji emoji-id="5282858672282705921">⚪</tg-emoji> Оплата посреднику: <i>{escape(deal.payment)}</i>\n'

    message += f'\n<tg-emoji emoji-id="5280764411869438260">💎</tg-emoji> Доверенность: {format_user_handle(deal.warranty_reputation_user.users[0])}\n'
    message += f'<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> Истекает: <b>{format_date(deal.expires_at)}</b>\n'
    message += f'<tg-emoji emoji-id="5335062818649586072">👤</tg-emoji> Создал: {format_user_handle(deal.created_by_user)}\n\n'

    message += "<b>Описание</b>\n"
    message += f"<blockquote>{escape(deal.description)}</blockquote>\n"

    if deal.status == types.DealStatus.DRAFT:
        message += (
            "\n<i>Держатель доверенности может принять или отклонить сделку. "
            "До принятия сумма не блокируется.</i>"
        )
    elif deal.status == types.DealStatus.PENDING:
        message += (
            "\n<i>Завершение — только когда оба подтвердят выполнение. "
            "Отмена — когда оба подтвердят отмену. Жалоба одной стороны останавливает сделку.</i>"
        )
    elif deal.status in [types.DealStatus.EXPIRED, types.DealStatus.REJECTED]:
        message += "\n<i>Сделка ожидает решения администрации. Доверенность остаётся заблокированной.</i>"

    return message


def get_external_deal_success_message(
    deal: entities.ExternalDealWithRelationsEntity,
) -> str:
    message = f'<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> <b>Черновик создан</b>\n\n'
    message += get_external_deal_message(deal)
    message += (
        '\n\n<tg-emoji emoji-id="5283269090767576749">⌛️</tg-emoji> <b>Что дальше?</b>\n'
        f"Держатель доверенности {format_user_handle(deal.warranty_reputation_user.users[0])} "
        "получит карточку с кнопками «Начать» или «Удалить».\n\n"
        "<i>Пока сделка не принята, доверенность не блокируется. "
        "Вы получите обновление, когда сделка начнётся.</i>"
    )
    return message


def get_reputation_request_message(
    reputation_request: entities.ReputationRequestWithUserEntity,
) -> str:
    message = f"<b>Запрос на репутацию</b>\n\n"
    message += f"<b>Статус</b>: {"Ожидает обработки" if reputation_request.is_active else "Обработан модератором"}\n"

    if reputation_request.applied_by_user:
        message += (
            f"Обработал: {format_user_handle(reputation_request.applied_by_user)}\n"
        )

    message += f"<b>Пользователь</b>: {format_user_handle(reputation_request.user)}\n\n"

    if reputation_request.about:
        message += f"<b>Описание</b>\n"
        message += f"<blockquote>{escape(reputation_request.about)}</blockquote>\n"

    return message


def get_user_info_message(
    user: entities.UserEntity,
    violations_count: Dict[types.ViolationType, int],
) -> str:
    message = f'<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> <b>Информация о пользователе</b>\n\n'
    message += f"<b>Пользователь</b>: {format_user_handle(user)}\n"
    message += f"<b>Роль</b>: {USER_ROLES[user.role]}\n"
    message += f"<b>Дата регистрации</b>: {format_date(user.created_at)}\n\n"

    if violations_count:
        message += f"<b>Нарушения</b>\n"

        for violation_type, count in violations_count.items():
            message += f"<b>{VIOLATIONS[violation_type]}</b>: {count} шт.\n"

    return message
