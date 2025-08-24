from pydantic import BaseModel, Field

from app.db.enumerated_types import BookCategory


class AddBookSchema(BaseModel):
    """
    Schema for validating input when adding a new book.

    Attributes:
        title (str): Mandatory title of the book.
            - Must be at least 1 character and at most 100 characters.
        description (str | None): Optional description of the book.
            - If provided, must be at least 1 character and at most 1000 characters.
        isbn (str): Mandatory International Standard Book Number (ISBN).
            - Must be at least 10 and at most 13 characters.
        price (float): Mandatory price of the book.
            - Must be greater than or equal to 0.
        category (BookCategory): Mandatory category of the book.
            - Must be a valid value from the BookCategory enum.
        stock_count (int): Mandatory stock count of the book.
            - Must be an integer greater than or equal to 0.
        author_ids (list[str]): Mandatory list of author identifiers.
            - Each identifier must exactly 22 characters.
    """

    title: str = Field(..., min_length=1, max_length=100, description="The title of the book.")
    description: str | None = Field(default=None, min_length=1, max_length=1000, description="The description of the book.")
    isbn: str = Field(..., min_length=10, max_length=13, description="The ISBN of the book.")
    price: float = Field(..., ge=0, description="The price of the book.")
    category: BookCategory = Field(..., description="The category of the book.")
    stock_count: int = Field(..., ge=0, description="The stock count of the book.")
    author_ids: list[str] = Field(..., description="A list of book's author identifiers.")


class UpdateBookSchema(BaseModel):
    """
    Schema for validating input when updating an existing book.

    Attributes:
        title (str | None): Optional new title of the book.
            - Must be at least 1 character and at most 100 characters.
        description (str | None): Optional new description of the book.
            - If provided, must be at least 1 character and at most 1000 characters.
        isbn (str | None): Optional new International Standard Book Number (ISBN).
            - Must be at least 10 and at most 13 characters.
        price (float | None): Optional new price of the book.
            - Must be greater than or equal to 0.
        category (BookCategory | None): Optional new category of the book.
            - Must be a valid value from the BookCategory enum.
        stock_count (int | None): Optional new stock count of the book.
            - Must be an integer greater than or equal to 0.
        author_ids (list[str]): Optional list of author identifiers.
            - Each identifier must exactly 22 characters.
    """

    title: str | None = Field(default=None, min_length=1, max_length=100, description="The title of the book.")
    description: str | None = Field(default=None, min_length=1, max_length=1000, description="The description of the book.")
    isbn: str | None = Field(default=None, min_length=10, max_length=13, description="The ISBN of the book.")
    price: float | None = Field(default=None, ge=0, description="The price of the book.")
    category: BookCategory | None = Field(default=None, description="The category of the book.")
    stock_count: int | None = Field(default=None, ge=0, description="The stock count of the book.")
    author_ids: list[str] | None = Field(default=None, description="A list of book's author identifiers.")
