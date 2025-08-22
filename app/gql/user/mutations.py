from graphene import Mutation, String, Field
from sqlalchemy import select
from graphql import GraphQLError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.db import User, SessionLocal
from app.gql.types import UserObject



class AddUser(Mutation):
    """GraphQL mutation for creating a new user."""

    class Arguments:
        name = String(required=True)
        email = String(required=True)
        password = String(required=True)

    user = Field(lambda: UserObject)

    @staticmethod
    async def mutate(root, info, name, email, password):
        """
        Creates a new user if the email does not already exist.

        Args:
            root (Object): Root of the mutation
            info (Object): Information about the mutation
            name (str): User's full name.
            email (str): User's email address.
            password (str): Raw password (will be hashed before storing).

        Returns:
            AddUser: The mutation result containing the created user.

        Raises:
            GraphQLError: If the email already exists or on unexpected DB errors.
        """
        async with SessionLocal() as session:
            try:
                # Check if user already exists
                result = await session.execute(select(User).where(User.email == email))
                existing_user = result.unique().scalars().one_or_none()
                if existing_user:
                    raise GraphQLError(f"User with email {email} already exists")

                # Create new user with hashed password
                new_user = User(
                    name=name,
                    email=email,
                    hashed_password=password
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                return AddUser(user=new_user)

            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(f"Error adding user: {str(e)}")
                raise GraphQLError("Unexpected error occurred while adding user")
