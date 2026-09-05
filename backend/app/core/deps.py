from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError(message="Missing authentication token.")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise UnauthorizedError(code="INVALID_TOKEN", message="Invalid or expired token.")

    user = db.get(User, user_id)
    if user is None:
        raise UnauthorizedError(code="USER_NOT_FOUND", message="User no longer exists.")

    return user
