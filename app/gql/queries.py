from graphene import ObjectType

from app.gql.user.queries import UserQueries

class Query(UserQueries, ObjectType):
    pass