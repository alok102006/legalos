from fastapi import HTTPException, status

class LegalOSException(HTTPException):
    """Base exception for LegalOS app."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(LegalOSException):
    """400 Bad Request."""
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundException(LegalOSException):
    """404 Not Found."""
    def __init__(self, detail: str = "Resource Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(LegalOSException):
    """401 Unauthorized."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(LegalOSException):
    """403 Forbidden."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InternalServerException(LegalOSException):
    """500 Internal Server Error."""
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
