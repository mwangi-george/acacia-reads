from graphene import Mutation, List, Field, InputObjectType, String, Int
from graphql import GraphQLError
from pydantic import ValidationError
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal, Order, User, OrderItem, Book
from app.gql.order.schemas import OrderSchema
from app.gql.types import OrderObject
from app.utils.utils import logged_in_user


class OrderItemInput(InputObjectType):
    """
    GraphQL input type for individual items in an order.

    Attributes:
        book_id (str): Unique identifier of the book being ordered.
        quantity (int): Quantity of the specified book.
    """
    book_id = String(required=True, description="ID of the book being ordered")
    quantity = Int(required=True, description="Quantity of the book ordered")


class AddOrder(Mutation):
    """
    GraphQL mutation for placing a new order.

    Workflow:
        1. Validate order items using Pydantic (`OrderSchema`).
        2. Ensure all requested books exist and stock is sufficient.
        3. Create an `Order` linked to the authenticated user.
        4. Deduct stock and insert `OrderItem` records.
        5. Commit the transaction atomically.

    Returns:
        order (OrderObject): The newly created order object.
    """

    class Arguments:
        order_items = List(
            OrderItemInput,
            required=True,
            description="List of order items with book_id and quantity."
        )

    order = Field(OrderObject, description="Details of the created order.")

    @staticmethod
    @logged_in_user
    async def mutate(root, info, order_items, current_user: User):
        """
        Mutation resolver to create a new order.

        Args:
            root: Root GraphQL object (not used here).
            info: GraphQL execution info.
            order_items (list[OrderItemInput]): Items requested in the order.
            current_user (User): Injected by `@logged_in_user` decorator.

        Raises:
            GraphQLError: If validation fails, stock is insufficient,
                          or database errors occur.

        Returns:
            AddOrder: Mutation response containing the created order.
        """
        # --- Step 1: Validate input using Pydantic schema ---
        try:
            validated_order_data = OrderSchema(order_items=order_items)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise GraphQLError(f"Validation error: {str(e)}")

        async with SessionLocal() as session:

            # --- Step 2: Fetch all requested books in bulk ---
            book_ids = [item.book_id for item in validated_order_data.order_items]
            result = await session.execute(select(Book).filter(Book.book_id.in_(book_ids)))
            books_map = {book.book_id: book for book in result.unique().scalars().all()}

            # --- Step 3: Validate stock availability ---
            for item in validated_order_data.order_items:
                book = books_map.get(item.book_id)
                if not book:
                    raise GraphQLError(f"Book with id {item.book_id} not found.")

                if book.stock_count < item.quantity:
                    raise GraphQLError(
                        f"Requested quantity {item.quantity} for book {item.book_id} "
                        f"exceeds available stock ({book.stock_count})."
                    )

            try:
                # --- Step 4: Create order header ---
                order = Order(user_id=current_user.user_id)
                session.add(order)
                await session.flush()  # ensures order_id is available

                # --- Step 5: Create order items & deduct stock ---
                for item in validated_order_data.order_items:
                    book = books_map[item.book_id]
                    order_item = OrderItem(
                        order_id=order.order_id,
                        book_id=item.book_id,
                        quantity=item.quantity,
                    )
                    session.add(order_item)
                    book.stock_count -= item.quantity

                # --- Step 6: Commit transaction ---
                await session.commit()
                await session.refresh(order)
                return AddOrder(order=order)

            except IntegrityError as e:
                logger.error(f"Integrity error while adding order: {str(e)}")
                await session.rollback()
                raise GraphQLError("Order could not be completed due to a database constraint error.")

            except Exception as e:
                logger.error(f"Unexpected error while adding order: {str(e)}")
                await session.rollback()
                raise GraphQLError("An unexpected error occurred while processing your order. Please try again.")

