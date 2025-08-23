
from graphene import ObjectType, String, Field, List, Int
from sqlalchemy import select

from app.db import SessionLocal, User
from app.gql.types import UserObject
from app.utils.utils import admin_user


class UserQueries(ObjectType):
    """
    GraphQL queries for retrieving user information.

    This class defines resolvers for:
      - Fetching a single user by `user_id`.
      - Fetching a paginated list of users.

    All queries are restricted to admin users only, via the `@admin_user` decorator.
    """

    # Query to fetch a single user by ID
    user = Field(
        UserObject,
        user_id=String(required=True, description="Unique identifier of the user"),
        description="Retrieve a single user by ID (admin-only)."
    )

    # Query to fetch a paginated list of users
    users = List(
        UserObject,
        start=Int(default_value=0, description="Offset for pagination"),
        limit=Int(default_value=10, description="Maximum number of users to return"),
        description="Retrieve a paginated list of users (admin-only)."
    )

    @staticmethod
    @admin_user
    async def resolve_user(root, info, user_id: str) -> UserObject:
        """
        Resolver for fetching a single user by ID.

        Args:
            root: GraphQL root object (unused here).
            info: GraphQL request info (includes context with authentication).
            user_id (str): The unique identifier of the user to fetch.

        Returns:
            UserObject | None: The user if found, otherwise None.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            return result.unique().scalars().one_or_none()

    @staticmethod
    @admin_user
    async def resolve_users(root, info, start: int = 0, limit: int = 10) -> list[UserObject]:
        """
        Resolver for fetching a paginated list of users.

        Args:
            root: GraphQL root object (unused here).
            info: GraphQL request info (includes context with authentication).
            start (int, optional): Pagination offset (default=0).
            limit (int, optional): Maximum number of users to return (default=10).

        Returns:
            list[UserObject]: A list of user objects.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(User).offset(start).limit(limit)
            )
            return result.unique().scalars().all()