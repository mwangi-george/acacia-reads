from graphene import Field, String, List, Int
from sqlalchemy import select

from app.db import SessionLocal, Author
from app.gql.types import AuthorObject
from app.utils.utils import admin_user


class AuthorQuery:
    """
    GraphQL query definitions for fetching Author data.

    This class defines resolvers for:
    - Fetching a single author by ID.
    - Fetching a paginated list of authors.

    Security:
        Both resolvers are protected by the `@admin_user` decorator to
        ensure only authorized users can access the data.
    """

    # Single Author Query
    author = Field(
        AuthorObject,
        author_id=String(required=True, description="The unique identifier of the author."),
        description="Retrieve a single author by their unique identifier."
    )

    # Multiple Authors Query
    authors = List(
        AuthorObject,
        start=Int(default_value=0, description="The starting index for pagination (default: 0)."),
        limit=Int(default_value=10, description="The maximum number of authors to return (default: 10)."),
        description="Retrieve a list of authors with optional pagination."
    )

    @staticmethod
    @admin_user
    async def resolve_author(root, info, author_id: str):
        """
        Resolver for fetching a single author.

        Args:
            root: Root resolver object (not used here).
            info: GraphQL resolve info (context, request metadata).
            author_id (str): The unique identifier of the author.

        Returns:
            Author | None: The matching Author object if found, otherwise None.
        """
        async with SessionLocal() as session:
            db_result = await session.execute(
                select(Author).where(Author.author_id == author_id)
            )
            return db_result.unique().scalars().one_or_none()

    @staticmethod
    @admin_user
    async def resolve_authors(root, info, start: int = 0, limit: int = 10):
        """
        Resolver for fetching a list of authors with pagination.

        Args:
            root: Root resolver object (not used here).
            info: GraphQL resolve info (context, request metadata).
            start (int): The starting index for pagination (default: 0).
            limit (int): The maximum number of authors to return (default: 10).

        Returns:
            List[Author]: A list of Author objects within the given range.
        """
        async with SessionLocal() as session:
            db_result = await session.execute(
                select(Author).offset(start).limit(limit)
            )
            return db_result.unique().scalars().all()
