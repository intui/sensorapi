import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

// Use environment variable for GraphQL endpoint, with fallbacks for development
const getGraphQLEndpoint = () => {
  // In production (Vercel), use relative path to same domain
  if (import.meta.env.PROD) {
    return '/graphql';
  }
  
  // In development, use production API endpoint
  const endpoint = import.meta.env.VITE_GRAPHQL_ENDPOINT || 'https://sensorapi-two.vercel.app/graphql';
  console.log('GraphQL endpoint:', endpoint);
  console.log('Environment variables:', import.meta.env);
  return endpoint;
};

const httpLink = createHttpLink({
  uri: getGraphQLEndpoint(),
  fetchOptions: {
    mode: 'cors',
    credentials: 'omit',
  },
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