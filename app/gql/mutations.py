from graphene import ObjectType

# Import mutation classes for different domains (Users, Authors, Books, Orders)
from app.gql.author.mutations import AddAuthor, UpdateAuthor, DeleteAuthor
from app.gql.book.mutations import AddBook, UpdateBook
from app.gql.order.mutations import AddOrder, UpdateOrder
from app.gql.user.mutations import AddUser, UpdateUser, LoginUser, DeleteUser


class Mutation(ObjectType):
    """
    Root GraphQL Mutation class.

    This class aggregates all available GraphQL mutations for the system,
    exposing them as mutation fields that clients can execute.

    The mutations are grouped into the following domains:

    - **User Management**: Create, update, authenticate, and delete users.
    - **Author Management**: Manage author records (add, update, delete).
    - **Book Management**: Manage book records (add, update).
    - **Order Management**: Manage book orders (add, update).

    Each mutation is defined as a GraphQL `Field` that maps to a specific
    mutation class implementation.
    """

    # --------------------------
    # User Management Mutations
    # --------------------------
    add_user = AddUser.Field(description="Register a new user in the system")
    login_user = LoginUser.Field(description="Authenticate an existing user and return a token")
    update_user = UpdateUser.Field(description="Update details of an existing user")
    delete_user = DeleteUser.Field(description="Delete an existing user from the system")

    # --------------------------
    # Author Management Mutations
    # --------------------------
    add_author = AddAuthor.Field(description="Add a new author record")
    update_author = UpdateAuthor.Field(description="Update details of an existing author")
    delete_author = DeleteAuthor.Field(description="Remove an author record from the system")

    # --------------------------
    # Book Management Mutations
    # --------------------------
    add_book = AddBook.Field(description="Add a new book record")
    update_book = UpdateBook.Field(description="Update details of an existing book")

    # --------------------------
    # Order Management Mutations
    # --------------------------
    add_order = AddOrder.Field(description="Create a new order for books")
    update_order = UpdateOrder.Field(description="Update details of an existing order")
