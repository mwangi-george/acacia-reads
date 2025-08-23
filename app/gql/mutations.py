from graphene import ObjectType
from app.gql.user.mutations import AddUser, UpdateUser


class Mutation(ObjectType):
    """
    GraphQL Mutation.

    Contains all the GraphQL mutation operations for users, books, authors, & orders
    """
    add_user = AddUser.Field()
    update_user = UpdateUser.Field()