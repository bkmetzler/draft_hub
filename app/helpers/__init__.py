from typing import Any


def truthy(data: Any) -> bool:
    if data:
        return True
    return False


def falsy(data: Any) -> bool:
    return not truthy(data)
