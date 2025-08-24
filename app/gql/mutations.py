from graphene import ObjectType

from app.gql.author.mutations import AddAuthor, UpdateAuthor, DeleteAuthor
from app.gql.user.mutations import AddUser, UpdateUser, LoginUser, DeleteUser


class Mutation(ObjectType):
    """
    GraphQL Mutation.

    Contains all the GraphQL mutation operations for users, books, authors, & orders
    """
    add_user = AddUser.Field()
    update_user = UpdateUser.Field()
    login_user = LoginUser.Field()
    delete_user = DeleteUser.Field()

    add_author = AddAuthor.Field()
    update_author = UpdateAuthor.Field()
    delete_author = DeleteAuthor.Field()