
from graphene import ObjectType, String, Field
from sqlalchemy import select

from app.db import SessionLocal, User
from app.gql.types import UserObject


class Query(ObjectType):
    user = Field(UserObject, user_id=String(required=True))

    @staticmethod
    async def resolve_user(root, info, user_id) -> UserObject:
        async with SessionLocal() as session:
            result = await session.execute(select(User).filter(User.user_id == user_id))
            return result.unique().scalars().one_or_none()