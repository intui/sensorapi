import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

// Use environment variable for GraphQL endpoint, with fallbacks for development
const getGraphQLEndpoint = () => {
  // In production (Vercel), use relative path to same domain
  if (import.meta.env.PROD) {
    return '/graphql';
  }
  
  // In development, check for custom endpoint or use WSL2 network interface
  return import.meta.env.VITE_GRAPHQL_ENDPOINT || 'http://172.27.241.121:8000/graphql';
};

const httpLink = createHttpLink({
  uri: getGraphQLEndpoint(),
});

export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache({
    addTypename: false, // Disable automatic __typename field
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
    mutate: {
      errorPolicy: 'all',
    },
  },
});