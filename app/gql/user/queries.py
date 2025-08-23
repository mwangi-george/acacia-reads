
from graphene import ObjectType, String, Field, List, Int
from sqlalchemy import select, func

from app.db import SessionLocal, User
from app.gql.types import UserObject
from app.utils.utils import admin_user



class UserList(ObjectType):
    """
    GraphQL object type for paginated user results.
    """
    users = List(UserObject, description="List of users for the current page")
    total_count = Int(description="Total number of users available in the system")



class UserQueries(ObjectType):
    """
    GraphQL queries for retrieving user information.

    Queries:
      - `user`: Fetch a single user by ID.
      - `users`: Fetch a paginated list of users with total count metadata.

    All queries are restricted to admin users only, via the `@admin_user` decorator.
    """

    # Query to fetch a single user by ID
    user = Field(
        UserObject,
        user_id=String(required=True, description="Unique identifier of the user"),
        description="Retrieve a single user by ID (admin-only)."
    )

    # Query to fetch a paginated list of users with total count
    users = Field(
        UserList,
        start=Int(default_value=0, description="Offset for pagination"),
        limit=Int(default_value=10, description="Maximum number of users to return"),
        description="Retrieve a paginated list of users along with total count (admin-only)."
    )

    @staticmethod
    @admin_user
    async def resolve_user(root, info, user_id: str) -> UserObject:
        """
        Resolver for fetching a single user by ID.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            return result.unique().scalars().one_or_none()

    @staticmethod
    @admin_user
    async def resolve_users(root, info, start: int = 0, limit: int = 10) -> UserList:
        """
        Resolver for fetching a paginated list of users and total count.

        Args:
            root: GraphQL root object (unused).
            info: GraphQL request info (includes context with authentication).
            start (int, optional): Pagination offset (default=0).
            limit (int, optional): Maximum number of users to return (default=10).

        Returns:
            UserList: Contains the list of users and the total count.
        """
        async with SessionLocal() as session:
            # Get paginated results
            result = await session.execute(
                select(User).offset(start).limit(limit)
            )
            users = result.unique().scalars().all()

            # Get total count of all users
            total_count_result = await session.execute(select(func.count(User.user_id)))
            total_count = total_count_result.scalar_one()

            return UserList(users=users, total_count=total_count)