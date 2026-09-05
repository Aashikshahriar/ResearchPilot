from fastapi import HTTPException, status


class APIError(HTTPException):
    """Structured application error rendered as {"error": {"code", "message"}}."""

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class NotFoundError(APIError):
    def __init__(self, code: str, message: str):
        super().__init__(status.HTTP_404_NOT_FOUND, code, message)


class ForbiddenError(APIError):
    def __init__(self, code: str = "FORBIDDEN", message: str = "You do not have access to this resource."):
        super().__init__(status.HTTP_403_FORBIDDEN, code, message)


class BadRequestError(APIError):
    def __init__(self, code: str, message: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, code, message)


class ConflictError(APIError):
    def __init__(self, code: str, message: str):
        super().__init__(status.HTTP_409_CONFLICT, code, message)


class UnauthorizedError(APIError):
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "Authentication required."):
        super().__init__(status.HTTP_401_UNAUTHORIZED, code, message)
