// Example: GraphQL usage
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'https://api.example.com/graphql',
  cache: new InMemoryCache()
});

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
    }
  }
`;

client.query({
  query: GET_USERS
}).then(result => console.log(result));
