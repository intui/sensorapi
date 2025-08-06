"""
Main GraphQL schema combining all queries and mutations.
"""
import strawberry

from app.graphql.resolvers import Mutation, Query

# Create the main GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
