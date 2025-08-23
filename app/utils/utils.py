from functools import wraps
from typing import Callable

import jwt
from datetime import datetime, timezone, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from graphql import GraphQLError
from loguru import logger
from sqlalchemy import select

from app.db import User, SessionLocal
from app.db.enumerated_types import UserRole
from app.settings.config import TOKEN_EXPIRY_IN_MINUTES, JWT_SECRET_KEY, JWT_ALGORITHM


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using Argon2.

    This function creates a new instance of `PasswordHasher` (from the argon2 library)
    and uses it to securely hash the given plain-text password.

    Args:
        password (str): The plain-text password to be hashed.

    Returns:
        str: A secure hashed password string that can be stored in the database.
    """
    hasher = PasswordHasher()
    return hasher.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verify a plain-text password against its hashed version.

    This function compares the provided plain-text password with the hashed password
    using Argon2's secure verification method.

    Args:
        hashed_password (str): The previously stored hashed password.
        plain_password (str): The plain-text password provided by the user.

    Returns:
        bool: True if the password is correct, otherwise raises an error.

    Raises:
        GraphQLError: If the password verification fails (incorrect password).

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password(hashed, "mypassword123")
        True

        >>> verify_password(hashed, "wrongpassword")
        GraphQLError: Incorrect password
    """
    hasher = PasswordHasher()
    try:
        # Verify will raise VerifyMismatchError if the password does not match
        hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        raise GraphQLError("Incorrect password")


def generate_access_token(email: str) -> str:
    """
    Generate a JWT access token for a user.

    This function generates a JSON Web Token (JWT) containing the user's email as
    the subject (`sub`) and an expiration time (`exp`). The token is signed using
    the configured secret key and algorithm.

    Args:
        email (str): The user's email address, used as the subject in the token.

    Returns:
        str: A signed JWT string that can be returned to the client for authentication.

    Raises:
        GraphQLError: If token generation fails for any reason.

    Example:
        >>> token = generate_access_token("user@example.com")
        >>> print(token)  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_IN_MINUTES),
    }

    try:
        # Encode the payload into a JWT using the secret and algorithm
        token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"Failed to generate access token: {str(e)}")
        raise GraphQLError("Failed to generate access token")



async def get_authenticated_user(context: dict) -> User:
    """
    Retrieve the currently authenticated user from the request context.

    This function extracts the JWT token from the `Authorization` header,
    verifies it, decodes its payload, and fetches the corresponding user
    from the database.

    Args:
        context (dict): GraphQL context dictionary. Must contain a `request` object
                        with an `Authorization` header in the format:
                        "Bearer <token>".

    Returns:
        User: The authenticated user object retrieved from the database.

    Raises:
        GraphQLError:
            - If the `Authorization` header is missing or malformed.
            - If the token is invalid or expired.
            - If the user cannot be found in the database.
    """
    # Extract request object and Authorization header
    request_object = context.get("request")
    auth_header = request_object.headers.get("Authorization") if request_object else None

    if not auth_header:
        raise GraphQLError("Missing authentication token")

    # Split header into scheme and token
    token_parts = auth_header.split(" ")

    # Ensure header follows "Bearer <token>" format
    if token_parts[0] != "Bearer" or len(token_parts) != 2:
        raise GraphQLError("Invalid authentication header format")

    raw_token = token_parts[1]

    try:
        # Decode the JWT payload
        payload = jwt.decode(
            jwt=raw_token,
            key=JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],  # Must be a list, not a string
        )

        # Extract user identifier (email from the "sub" claim)
        user_email = payload.get("sub")
        if not user_email:
            raise GraphQLError("Invalid token: subject missing")

        # Query database for user
        async with SessionLocal() as session:  # SessionLocal should yield AsyncSession
            result = await session.execute(select(User).where(User.email == user_email))
            user = result.unique().scalars().one_or_none()

            if not user:
                raise GraphQLError("Could not authenticate user")

            return user

    except jwt.ExpiredSignatureError:
        # Token is valid but expired
        raise GraphQLError("Authentication token has expired")
    except jwt.InvalidTokenError:
        # Any other token decoding/validation error
        raise GraphQLError("Could not authenticate user")


def logged_in_user(func: Callable) -> Callable:
    """
    Decorator that ensures the caller is an authenticated user.

    This decorator checks for a valid JWT token in the request context,
    using `get_authenticated_user`. If authentication fails, it raises
    a GraphQL error. Otherwise, it proceeds to call the wrapped resolver.

    Args:
        func (Callable): The resolver function to wrap.

    Returns:
        Callable: The wrapped function, which only executes if the user is authenticated.

    Example:
        @logged_in_user
        async def resolve_profile(root, info, **kwargs):
            return {"message": "Welcome!"}
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        info = args[1]  # GraphQL resolver signature: (root, info, **kwargs)

        # Ensure user is authenticated (raises error if not)
        await get_authenticated_user(info.context)

        # Continue with the original resolver
        return await func(*args, **kwargs)

    return wrapper


def admin_user(func: Callable) -> Callable:
    """
    Decorator that ensures the caller is an authenticated admin user.

    This decorator checks for a valid JWT token in the request context,
    verifies the associated user's role, and only allows access if the user
    is an admin. Non-admin users will receive a GraphQL authorization error.

    Args:
        func (Callable): The resolver function to wrap.

    Returns:
        Callable: The wrapped function, which only executes if the user is an admin.

    Raises:
        GraphQLError: If the user is not authenticated or not an admin.

    Example:
        @admin_user
        async def resolve_manage_users(root, info, **kwargs):
            return {"status": "You are an admin!"}
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        info = args[1]  # GraphQL resolver signature: (root, info, **kwargs)

        # Ensure user is authenticated
        user = await get_authenticated_user(info.context)

        # Check if user has admin role
        if user.role != UserRole.ADMIN:
            raise GraphQLError("You are not authorized to perform this action")

        # Continue with the original resolver
        return await func(*args, **kwargs)

    return wrapper