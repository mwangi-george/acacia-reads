from graphene import ObjectType

from app.gql.user.queries import UserQuery
from app.gql.author.queries import AuthorQuery

class Query(UserQuery, AuthorQuery, ObjectType):
    pass