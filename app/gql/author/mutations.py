from graphene import Mutation, String, Field, Boolean
from graphql import GraphQLError
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal, Author
from app.gql.author.validators import UpdateAuthorSchema, AddAuthorSchema
from app.gql.types import AuthorObject
from app.utils.utils import admin_user



class AddAuthor(Mutation):
    """
    GraphQL mutation for adding a new author.

    This mutation can only be executed by admin users. It checks whether an
    author with the given email already exists, and if not, creates a new
    author record in the database with the following fields:

    - first_name (str): First name of the author.
    - last_name (str): Last name of the author.
    - email (str): Email of the author (must be unique).
    - bio (str, optional): Short biography of the author.

    Returns:
        author (AuthorObject): The newly created author.

    Example GraphQL mutation:
        mutation {
            addAuthor(
                firstName: "Alice",
                lastName: "Walker",
                email: "alice@example.com",
                bio: "Award-winning author"
            ) {
                author {
                    firstName
                    lastName
                    email
                    bio
                }
            }
        }
    """

    class Arguments:
        first_name = String(required=True, description="First name of the author.")
        last_name = String(required=True, description="Last name of the author.")
        email = String(required=True, description="Email of the author (must be unique).")
        bio = String(description="Optional bio of the author.")

    # Field returned in mutation response
    author = Field(lambda: AuthorObject, description="The newly created author object.")

    @staticmethod
    @admin_user
    async def mutate(root, info, **kwargs):
        """
        Mutation resolver for adding a new author.

        Raises:
            GraphQLError: If the email already exists or if an unexpected error occurs.
        """
        # Validate inputs
        try:
            validated_data = AddAuthorSchema(**kwargs).model_dump(exclude_none=True)
        except ValidationError as e:
            raise GraphQLError(f"Validation error: {str(e)}")

        async with SessionLocal() as session:
            user_email = validated_data.get("email")

            # Check if author with given email already exists
            db_result = await session.execute(select(Author).where(Author.email == user_email))
            existing_author = db_result.unique().scalars().one_or_none()

            if existing_author:
                # Fail if email is already taken
                raise GraphQLError(f"Author with email {user_email} already exists")

            # Create new author instance
            new_author = Author()
            for field, value in validated_data.items():
                if hasattr(new_author, field):
                    setattr(new_author, field, value)

            # add record to db
            session.add(new_author)

            try:
                # Commit transaction to persist the new author
                await session.commit()

                # Refresh instance to get generated fields (e.g., ID)
                await session.refresh(new_author)

                return AddAuthor(author=new_author)

            except Exception as e:
                logger.error(f"Failed to add author: {str(e)}")
                await session.rollback()
                raise GraphQLError("Unexpected error occurred while adding author")



class UpdateAuthor(Mutation):
    """
    GraphQL Mutation for updating an existing author's details.

    This mutation allows an admin user to update the following author fields:
    - First name
    - Last name
    - Email (must remain unique)
    - Bio (optional descriptive text)

    The mutation requires the `author_id` to identify the target author.
    If the author does not exist, a `GraphQLError` is raised.

    Returns:
        author (AuthorObject): The newly updated author.
    """

    class Arguments:
        """ GraphQL input arguments for the mutation """
        author_id = String(required=True, description="The unique identifier of the author to update.")
        first_name = String(description="Optional new first name of the author.")
        last_name = String(description="Optional new last name of the author.")
        email = String(description="Optional new email address of the author (must be unique).")
        bio = String(description="Optional new bio/description of the author.")

    # Output field: returns the updated AuthorObject after a successful update
    author = Field(lambda: AuthorObject, description="The updated author object.")

    @staticmethod
    @admin_user
    async def mutate(root, info, author_id: str, **kwargs):
        """
        Executes the mutation to update an author's details.

        Returns:
            UpdateAuthor: An instance containing the updated `AuthorObject`.

        Raises:
            GraphQLError: If the author does not exist or if the update fails.
        """
        # Step 1: Validate inputs using Pydantic
        try:
            validated_data = UpdateAuthorSchema(**kwargs).model_dump(exclude_none=True)
        except Exception as e:
            raise GraphQLError(f"Validation error: {str(e)}")

        async with SessionLocal() as session:
            # Fetch the author by ID
            db_result = await session.execute(select(Author).where(Author.author_id == author_id))
            author = db_result.unique().scalars().one_or_none()

            if not author:
                # Fail if author not found
                raise GraphQLError(f"Author with id {author_id} does not exist")

            # Apply updates only if fields are provided
            for field, value in validated_data.items():
                if hasattr(author, field):
                    setattr(author, field, value)

            try:
                # Commit changes and refresh the author instance
                await session.commit()
                await session.refresh(author)

                # Return updated author object
                return UpdateAuthor(author=author)
            except IntegrityError as e:
                logger.error(f"Database error - Duplicate email: {str(e)}")
                raise GraphQLError(f"Integrity error: {kwargs.get("email")} is already taken.")

            except Exception as e:
                # Rollback in case of error and log the exception
                logger.error(f"Failed to update author: {str(e)}")
                await session.rollback()
                raise GraphQLError("Unexpected error occurred while updating author")


class DeleteAuthor(Mutation):
    """
    GraphQL Mutation to delete an author.

    This mutation allows administrators to delete an existing author
    from the database using the author's unique identifier.

    Arguments:
        - author_id (str): The unique identifier of the author to delete.

    Returns:
        - success (bool): Whether the author was deleted.
        - author (AuthorObject): The deleted author object if successful.

    Errors:
        - Raises `GraphQLError` if the author does not exist.
        - Raises `GraphQLError` if an unexpected error occurs during deletion.
    """
    class Arguments:
        author_id = String(required=True, description="The unique identifier of the author to delete.")

    # Field returned in the GraphQL response containing the deletion status
    success = Boolean(description="Deletion successful flag.")

    # Field returned in the GraphQL response containing the deleted author
    author = Field(lambda: AuthorObject, description="The deleted author object.")

    @staticmethod
    @admin_user
    async def mutate(root, info, author_id: str):
        """
        Handles the mutation logic for deleting an author.

        Returns:
            DeleteAuthor: An instance containing the deleted author.

        Raises:
            GraphQLError: If author is not found or an error occurs while deleting.
        """
        async with SessionLocal() as session:
            # Fetch the author from the database by ID
            db_result = await session.execute(select(Author).where(Author.author_id == author_id))
            author = db_result.unique().scalars().one_or_none()

            if not author:
                # Fail if author does not exist in the database
                raise GraphQLError(f"Author with id {author_id} does not exist")

            try:
                # Mark author for deletion
                await session.delete(author)

                # Commit transaction to persist changes
                await session.commit()
                return DeleteAuthor(success=True, author=author)
            except IntegrityError as i:
                await session.rollback()
                logger.error(f"Integrity error deleting author {author_id}: {str(i)}")
                raise GraphQLError("Cannot delete author due to related records.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error deleting author {author_id}: {e}")
                raise GraphQLError("Unexpected error occurred while deleting author.")