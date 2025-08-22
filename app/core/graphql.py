from fastapi import FastAPI
from graphene import Schema
from starlette_graphene3 import GraphQLApp, make_playground_handler

# GraphQl schema - queries & mutations
gql_schema = Schema()


def mount_graphql(app_instance: FastAPI, endpoint: str = "/graphql") -> None:
    """
    Mounts a GraphQL endpoint to a FastAPI instance.

    Args:
        app_instance (FastAPI): The FastAPI application instance.
        endpoint (str): Path for the GraphQL API.
    """
    app_instance.mount(
        path=endpoint,
        app=GraphQLApp(
            schema=gql_schema,
            on_get=make_playground_handler(),
        ),
    )
