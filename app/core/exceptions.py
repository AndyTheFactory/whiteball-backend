"""Custom application exceptions."""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
            },
        )


class AuthException(AppException):
    """Authentication exception."""
    
    def __init__(self, code: str = "AUTH_INVALID_CREDENTIALS", message: str = "Invalid credentials"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class NotFoundException(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateException(AppException):
    """Duplicate resource exception."""
    
    def __init__(self, resource: str = "Resource", field: str = ""):
        super().__init__(
            code=f"{resource.upper()}_DUPLICATE",
            message=f"A {resource.lower()} with this {field} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationException(AppException):
    """Validation exception."""
    
    def __init__(self, message: str):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )
