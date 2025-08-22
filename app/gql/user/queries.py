
from graphene import ObjectType, String, Field, List, Int
from sqlalchemy import select

from app.db import SessionLocal, User
from app.gql.types import UserObject


class UserQueries(ObjectType):
    user = Field(UserObject, user_id=String(required=True))
    users = List(UserObject, start=Int(), limit=Int())

    @staticmethod
    async def resolve_user(root, info, user_id) -> UserObject:
        async with SessionLocal() as session:
            result = await session.execute(select(User).filter(User.user_id == user_id))
            return result.unique().scalars().one_or_none()

    @staticmethod
    async def resolve_users(root, info, start = 0, limit = 10) -> list[UserObject]:
        async with SessionLocal() as session:
            result = await session.execute(select(User).offset(start).limit(limit))
            return result.unique().scalars().all()