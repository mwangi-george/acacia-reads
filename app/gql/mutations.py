from graphene import ObjectType
from app.gql.user.mutations import AddUser


class Mutation(ObjectType):
    """
    GraphQL Mutation.

    Contains all the GraphQL mutation operations for users, books, authors, & orders
    """
    add_user = AddUser.Field()