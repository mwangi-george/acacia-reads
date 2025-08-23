from graphene import Mutation, String, Field
from sqlalchemy import select
from graphql import GraphQLError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.db import User, SessionLocal
from app.db.enumerated_types import UserRole
from app.gql.types import UserObject
from app.utils.utils import (
    hash_password, logged_in_user, admin_user,
    verify_password, generate_access_token,
)


class AddUser(Mutation):
    """GraphQL mutation for creating a new user.

    This mutation allows adding a new user to the database with the following fields:
        - name
        - email
        - password

    By default, a new user will have the `USER` role. Only admins can update their role.
    """

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
                    hashed_password=hash_password(password)
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                return AddUser(user=new_user)
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(f"Error adding user: {str(e)}")
                raise GraphQLError("Unexpected error occurred while adding user")


class UpdateUser(Mutation):
    """
    GraphQL Mutation for updating a user.

    This mutation allows updating an existing user's details, including:
        - Name
        - Email
        - Password (hashed before saving)
    """

    class Arguments:
        user_id = String(required=True)
        name = String()
        email = String()
        password = String()

    user = Field(lambda: UserObject)

    @staticmethod
    @logged_in_user
    async def mutate(root, info, user_id, name = None, email = None, password = None):
        """
        Resolver function for the mutation.

        Handles fetching the user, applying updates, committing the transaction,
        and returning the updated user object.
        """
        async with SessionLocal() as session:
            try:
                # Fetch user
                result = await session.execute(select(User).where(User.user_id == user_id))
                existing_user = result.unique().scalars().one_or_none()
                if not existing_user:
                    raise GraphQLError(f"User with id {user_id} does not exist")

                # Apply updates
                if name:
                    existing_user.name = name
                if email:
                    existing_user.email = email
                if password:
                    existing_user.hashed_password = hash_password(password)

                # Save changes
                await session.commit()
                await session.refresh(existing_user)

                return UpdateUser(user=existing_user)
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(f"Error updating user: {str(e)}")
                raise GraphQLError("Unexpected error occurred while updating user")


class LoginUser(Mutation):
    """
    GraphQL mutation for authenticating a user and issuing an access token.

    This mutation verifies the provided email and password against the database,
    and if valid, returns a JWT token that can be used for authenticated requests.
    """
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    token = String(description="JWT access token if login is successful.")

    @staticmethod
    async def mutate(root, info, email, password):
        """
        Handle the login process: validate user credentials and issue token.

        Args:
            root (Object): Root of the mutation
            info (Object): Information about the mutation
            email (str): User's email address.
            password (str): Raw user password.
        """
        async with SessionLocal() as session:
            # Fetch user by email
            db_result = await session.execute(select(User).where(User.email == email))
            user = db_result.unique().scalars().one_or_none()

            if not user:
                # Fail if no user found with the given email
                raise GraphQLError("User not found")

            # Verify password (raises GraphQLError if incorrect)
            verify_password(user.hashed_password, password)

            # Generate access token tied to user identity
            token = generate_access_token(user.email)

            # Return instance of this mutation with token in response
            return LoginUser(token=token)


class DeleteUser(Mutation):
    """
    GraphQL mutation for deleting a user.

    This mutation allows the adminstrator to delete a user from the database.
    All information about the user e.g. books, orders etc. is also deleted.
    """

    class Arguments:
        user_id = String(required=True)

    user = Field(lambda: UserObject)

    @staticmethod
    @admin_user
    async def mutate(root, info, user_id):
        """
        Handle the deletion of the user from the database.

        Args:
            root (Object): Root of the mutation
            info (Object): Information about the mutation
            user_id (str): Unique user's identifier in the database.
        """

        async with SessionLocal() as session:

            # Fetch user from database
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.unique().scalars().one_or_none()

            if not user:
                # Fail if no user is found with the given id
                raise GraphQLError("User not found")

            if user.role == UserRole.ADMIN:
                raise GraphQLError("Administrator user cannot be deleted")

            # delete & sync changes in db
            await session.delete(user)
            await session.commit()

            # return instance of the mutation
            return DeleteUser(user=user)
