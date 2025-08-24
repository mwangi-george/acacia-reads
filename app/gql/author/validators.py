from pydantic import BaseModel, Field, EmailStr



class AddAuthorSchema(BaseModel):
    """
    Schema for validating input when adding an author.

    Attributes:
        first_name (str): Mandatory first name of the author.
            - Must be at least 1 character and at most 50 characters.
        last_name (str): Mandatory last name of the author.
            - Must be at least 1 character and at most 50 characters.
        email (str): Mandatory email of the author.
            - Must be a valid email format.
            - Must be between 1 and 60 characters.
        bio (str | None): Optional  bio of the author.
            - Must be at least 1 character and at most 1000 characters.
    """
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mandatory first name of the author.",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mandatory last name of the author.",
    )
    email: EmailStr = Field(
        ...,
        min_length=1,
        max_length=60,
        description="Mandatory email of the author.",
    )
    bio: str | None = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Optional biography of the author (1–1000 characters)."
    )



class UpdateAuthorSchema(BaseModel):
    """
    Schema for validating input when updating an author.

    Attributes:
        first_name (str | None): Optional first name of the author.
            - Must be at least 1 character and at most 50 characters.
        last_name (str | None): Optional last name of the author.
            - Must be at least 1 character and at most 50 characters.
        email (EmailStr | None): Optional email of the author.
            - Must be a valid email format.
            - Must be between 1 and 60 characters.
        bio (str | None): Optional bio of the author.
            - Must be at least 1 character and at most 1000 characters.
    """
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Optional first name of the author (1–50 characters)."
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Optional last name of the author (1–50 characters)."
    )
    email: EmailStr | None = Field(
        default=None,
        min_length=1,
        max_length=60,
        description="Optional email of the author (must be valid and ≤ 60 chars)."
    )
    bio: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
        description="Optional biography of the author (1–1000 characters)."
    )

