from pydantic import BaseModel, Field


class OrderItemSchema(BaseModel):
    """
    Schema for validating input when adding a new order

    Attributes:
        - book_id (str): Mandatory id of the book.
        - quantity (int): Mandatory quantity of the book.
    """
    book_id: str = Field(..., max_length=22, min_length=22, description="The unique identifier of the book item to order")
    quantity: int = Field(..., gt=0, description="The number of items to order")



class OrderSchema(BaseModel):
    """
    Schema for validating the entire order payload
    """
    order_items: list[OrderItemSchema]