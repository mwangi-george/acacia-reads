from graphene import ObjectType, List, Field, String, Int
from sqlalchemy import select

from app.db import SessionLocal, Book, User
from app.db.enumerated_types import BookCategory
from app.gql.types import BookObject
from app.utils.utils import logged_in_user


class BookQuery(ObjectType):
    """
    GraphQL query class for fetching books and categories.

    Queries:
        book (BookObject):
            - Fetch a single book by its unique book_id.

        books (List[BookObject]):
            - Fetch a paginated list of books with optional category filters.
            - Supports offset (`start`) and limit (`limit`) pagination.

        book_categories (List[str]):
            - Fetch all available book categories from the BookCategory enum.
    """

    # Single book query
    book = Field(
        BookObject,
        book_id=String(required=True, description="Unique book identifier"),
        description="Fetch a single book by its unique book_id."
    )

    # Multiple books query
    books = List(
        BookObject,
        start=Int(default_value=0, description="Starting offset for pagination."),
        limit=Int(default_value=10, description="Maximum number of results to return."),
        category=List(String, description="Optional list of book categories to filter by."),
        description="Fetch a list of books with pagination and category filtering."
    )

    # Book categories query
    book_categories = List(
        String,
        description="Fetch a list of all available book categories."
    )

    @staticmethod
    @logged_in_user
    async def resolve_book_categories(self, info, current_user: User):
        """
        Resolver for fetching all available book categories.

        Returns:
            list[str]: A list of category names defined in the BookCategory enum.
        """
        return [category.value for category in BookCategory]

    @staticmethod
    @logged_in_user
    async def resolve_book(root, info, book_id: str, current_user: User):
        """
        Resolver for fetching a single book by ID.

        Args:
            root (Object): Root of the GraphQL query.
            info (Object): Information about the GraphQL query.
            book_id (str): Unique identifier of the book.
            current_user (User): Current user browsing the book.

        Returns:
            Book | None: A Book object if found, otherwise None.
        """
        async with SessionLocal() as session:
            db_book = await session.execute(
                select(Book).where(Book.book_id == book_id)
            )
            return db_book.unique().scalars().one_or_none()

    @staticmethod
    @logged_in_user
    async def resolve_books(root, info, current_user: User, start: int, limit: int, category: list[str] | None = None):
        """
        Resolver for fetching a paginated list of books with optional category filters.

        Args:
            root (Root): Root object.
            info (object): Internal info object.
            current_user (User): Current user browsing the books.
            start (int): Pagination offset (default 0).
            limit (int): Pagination limit (default 10).
            category (list[str] | None): Optional list of categories to filter books by.

        Returns:
            list[Book]: A list of Book objects.
        """
        async with SessionLocal() as session:
            query = select(Book).offset(start).limit(limit)

            # Apply category filter if provided
            if category:
                query = query.where(Book.category.in_(category))

            db_books = await session.execute(query)
            return db_books.unique().scalars().all()
