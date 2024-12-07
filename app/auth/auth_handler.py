import shortuuid


def create_access_token(user_id: str) -> str:
    return str(user_id) + shortuuid.uuid()
