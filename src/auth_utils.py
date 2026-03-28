from typing import List, Optional, Tuple


def parse_bearer_parts(authorization: Optional[str]) -> Optional[List[str]]:
    """Parse `Authorization: Bearer ...` token into `:`-separated parts."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    return token.split(":")


def is_internal_bearer(parts: Optional[List[str]], internal_token: str) -> bool:
    """Whether parsed bearer parts match internal service token."""
    return bool(parts) and parts[0] == internal_token


def extract_user_password_session(
    parts: Optional[List[str]],
    *,
    default_session: str = "default",
) -> Optional[Tuple[str, str, str]]:
    """Extract user/password/session from parsed bearer parts."""
    if not parts or len(parts) < 2:
        return None
    user_id = parts[0]
    password = parts[1]
    session_id = parts[2] if len(parts) > 2 and parts[2] else default_session
    return user_id, password, session_id
