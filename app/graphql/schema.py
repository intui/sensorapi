"""
Main GraphQL schema combining all queries and mutations.
"""
import strawberry

from app.graphql.resolvers import Query, Mutation

# Create the main GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
