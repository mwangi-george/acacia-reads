from graphene import Mutation, String, Float, Int, Field, List
from graphql import GraphQLError
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal, Book, Author
from app.gql.types import BookObject
from app.utils.utils import admin_user
from app.gql.book.schemas import AddBookSchema, UpdateBookSchema


class AddBook(Mutation):
    """
    GraphQL mutation for adding a new book.

    This mutation can only be executed by admin users.

    Arguments:
    - title (str): Mandatory title of the book.
    - description (str | None): Optional description of the book.
    - isbn (str): Mandatory International Standard Book Number (ISBN).
    - price (float): Mandatory price of the book in US dollars.
    - category (str): Mandatory category/genre of the book.
    - stock_count (int): Mandatory number of copies available in stock.
    - author_ids (list[str]): Mandatory list of authors.

    Returns:
        - book (BookObject): The newly created book object.

    Raises:
        GraphQLError:
            - if the arguments are invalid.
            - If an error occurs during the mutation.
    """

    class Arguments:
        """Input arguments accepted by the mutation"""
        title = String(required=True, description="The title of the book.")
        description = String(required=False, description="The description of the book.")
        isbn = String(required=True, description="The ISBN of the book.")
        price = Float(required=True, description="The price of the book in USD")
        category = String(required=True, description="The category of the book.")
        stock_count = Int(required=True, description="The number of copies available in stock.")
        author_ids = List(String, required=True, description="List of author IDs")

    # mutation response
    book = Field(BookObject, description="The newly created book object.")

    @staticmethod
    @admin_user
    async def mutate(root, info, **kwargs):
        """
        Handles the validation of the input data & creation of a new book.

        Raises:
            GraphQLError: If validation fails or database operation encounters an error.

        Returns:
            AddBook: Mutation response containing the created Book object.
           """

        # Validate input data using AddBookSchema.
        try:
            validated_data = AddBookSchema(**kwargs).model_dump(exclude_none=True, exclude_unset=True)
        except ValidationError as e:
            raise GraphQLError(f'Validation error: {str(e)}')

        async with SessionLocal() as session:

            # Check if book with given isbn exists
            db_book = await session.execute(select(Book).where(Book.isbn == validated_data["isbn"]))
            if db_book.unique().scalars().first():
                raise GraphQLError(f'Book with this isbn already exists.')

            # Fetch existing authors
            db_authors = await session.execute(select(Author).where(Author.author_id.in_(kwargs["author_ids"])))
            authors = db_authors.unique().scalars().all()

            if not authors:
                raise Exception("At least one valid author_id must be provided")

            # Create a new Book instance and populate it with validated data.
            book = Book()
            book.authors = authors
            for key, value in validated_data.items():
                if hasattr(book, key):
                    setattr(book, key, value)

            session.add(book)
            try:
                # Persist the book into the database
                await session.commit()
                await session.refresh(book)

                return AddBook(book=book)
            except IntegrityError as e:
                logger.error(f'IntegrityError: {str(e)}')
                await session.rollback()
                raise GraphQLError(f'A database error occurred, please contact support.')
            except Exception as e:
                logger.error(f'GraphQL error: {str(e)}')
                await session.rollback()
                raise GraphQLError(f"Unexpected error occurred while adding book.")


class UpdateBook(Mutation):
    """
     GraphQL mutation for updating an existing book record.

    This mutation allows administrators to update details of a book. Only the
    fields provided will be updated, and validation is performed before
    committing changes to the database.

    Attributes:
        - book_id (str): Mandatory unique identifier of the book to update.
        - title (str, optional): Updated title of the book.
        - description (str, optional): Updated description of the book.
        - isbn (str, optional): Updated ISBN of the book.
        - price (float, optional): Updated price of the book in USD.
        - category (str, optional): Updated category of the book.
        - stock_count (int, optional): Updated number of copies in stock.
        - author_ids (list[str], optional): Updated list of authors.

    Returns:
        - book (BookObject): The updated book object.

    Raises:
        - GraphQLError:
            - If validation fails
            - If no with the given ID exists
            - If database operation encounters an error.
    """
    class Arguments:
        """Input arguments accepted by the mutation"""
        book_id = String(required=True, description="Mandatory unique identifier of the book.")
        title = String(description="Optional title of the book.")
        description = String(description="Optional description of the book.")
        isbn = String(description="Optional ISBN of the book.")
        price = Float(description="Optional price of the book in US dollars.")
        category = String(description="Optional category of the book.")
        stock_count = Int(description="Optional number of copies available in stock.")
        author_ids = List(String, description="List of author IDs")

    book = Field(BookObject, description="The updated book object.")

    @staticmethod
    @admin_user
    async def mutate(root, info, book_id, **kwargs):
        """Perform the update operation for an existing book."""

        # Validate input fields using the `UpdateBookSchema`
        try:
            validated_data = UpdateBookSchema(**kwargs).model_dump(exclude_none=True)
        except ValidationError as e:
            raise GraphQLError(f'Validation error: {str(e)}')

        async with SessionLocal() as session:
            # Retrieve the book from the database by book_id
            db_result = await session.execute(select(Book).where(Book.book_id == book_id))
            existing_book = db_result.unique().scalars().first()

            if not existing_book:
                # Fail if none exists
                raise GraphQLError(f'Book with ID {book_id} does not exist.')

            # Update author ids if provided
            if "author_ids" in validated_data.keys():
                # Fetch existing authors
                db_authors = await session.execute(select(Author).where(Author.author_id.in_(validated_data["author_ids"])))
                authors = db_authors.unique().scalars().all()

                if not authors:
                    raise Exception("At least one valid author_id must be provided")

                # Update book data
                existing_book.authors = authors

            # Update other fields
            for key, value in validated_data.items():
                #  Apply only the validated fields provided in the request.
                if hasattr(existing_book, key):
                    setattr(existing_book, key, value)

            try:
                # Commit changes and return the updated book.
                await session.commit()
                await session.refresh(existing_book)

                return UpdateBook(book=existing_book)

            except IntegrityError as e:
                # Likely due to duplicate ISBN or category constraint violations
                logger.error(f'IntegrityError: {str(e)}')
                await session.rollback()
                raise GraphQLError(f"A database error occurred while updating book, please contact support.")
            except Exception as e:
                # Catch-all for unexpected issues
                logger.error(f'GraphQL error: {str(e)}')
                await session.rollback()
                raise GraphQLError(f"Unexpected error occurred while updating book.")




