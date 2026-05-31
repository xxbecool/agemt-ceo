"""
Dependency injection for FastAPI routes.
Provides: JWT authentication, RBAC role checks, DB session.
"""
from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import verify_token
from models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate the JWT access token and return the corresponding User object.
    Raises HTTP 401 if the token is invalid or the user is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token, "access")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# Annotated dependency type for route handlers
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """
    Factory that returns a FastAPI dependency checking the current user's role.
    Usage: router.get("/admin", dependencies=[Depends(require_roles(UserRole.CEO, UserRole.ADMIN))])
    """
    async def _check(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return _check


# Pre-built RBAC dependencies
RequireCEO = Depends(
    require_roles(UserRole.CEO, UserRole.ADMIN)
)

RequireManager = Depends(
    require_roles(
        UserRole.CEO,
        UserRole.ADMIN,
        UserRole.OPERATIONS_MANAGER,
        UserRole.SALES_MANAGER,
    )
)

RequireAnalyst = Depends(
    require_roles(
        UserRole.CEO,
        UserRole.ADMIN,
        UserRole.OPERATIONS_MANAGER,
        UserRole.SALES_MANAGER,
        UserRole.ANALYST,
    )
)
