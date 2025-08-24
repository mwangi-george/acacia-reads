from graphene import ObjectType

from app.gql.book.queries import BookQuery
from app.gql.user.queries import UserQuery
from app.gql.author.queries import AuthorQuery



class Query(UserQuery, AuthorQuery, BookQuery, ObjectType):
    pass