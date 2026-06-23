CHECK_START_PREFIX = "check_"


def parse_check_start_payload(payload: str | None) -> str | None:
    if not payload or not payload.startswith(CHECK_START_PREFIX):
        return None

    search = payload[len(CHECK_START_PREFIX) :]
    if len(search) < 3 or len(search) > 100:
        return None

    return search


def build_check_start_payload(search: str) -> str | None:
    normalized = search.strip().lstrip("@")
    if len(normalized) < 3 or len(normalized) > 100:
        return None

    payload = f"{CHECK_START_PREFIX}{normalized}"
    if len(payload) > 64:
        return None

    return payload
