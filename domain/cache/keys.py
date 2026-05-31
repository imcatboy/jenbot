from domain.objects import entities


NAMESPACE = "jenbot:v1"
USER_PREFIX = "user"
MODERATION_PREFIX = "moderation"
MEDIA_PREFIX = "media"


def get_key(key: str) -> str:
    return f"{NAMESPACE}:{key}"


def get_user_key(key: str) -> str:
    return get_key(f"{USER_PREFIX}:{key}")


def get_user_by_id_key(user_id: int) -> str:
    return get_user_key(f"id:{user_id}")


def get_user_by_telegram_id_key(telegram_id: int) -> str:
    return get_user_key(f"telegram_id:{telegram_id}")


def get_profile_key(user_id: int) -> str:
    return get_user_key(f"profile:{user_id}")


def get_marketplace_user_key(user_id: int) -> str:
    return get_user_key(f"marketplace_user:{user_id}")


def get_reputation_user_key(user_id: int) -> str:
    return get_user_key(f"reputation_user:{user_id}")


def get_auth_key(hash: str) -> str:
    return get_key(f"auth:{hash}")


def get_user_keys(user: entities.UserEntity) -> list[str]:
    return [
        get_user_by_id_key(user.id),
        get_user_by_telegram_id_key(user.telegram_id),
        get_profile_key(user.id),
        get_marketplace_user_key(user.id),
        get_reputation_user_key(user.id),
    ]


def get_moderation_key(key: str) -> str:
    return get_key(f"{MODERATION_PREFIX}:{key}")


def get_trackers_key(user_id: int) -> str:
    return get_moderation_key(f"trackers:{user_id}")


def get_tracker_message_key(tracker_id: int) -> str:
    return get_moderation_key(f"tracker_message:{tracker_id}")


def get_media_key(key: str) -> str:
    return get_key(f"{MEDIA_PREFIX}:{key}")


def get_telegram_file_key(name: str) -> str:
    return get_media_key(f"telegram_file:{name}")
