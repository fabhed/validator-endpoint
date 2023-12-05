import "../public/antd.min.css";
import "../styles/globals.css";
import type { AppProps } from "next/app";
import withTheme from "../theme";

import axios from "axios";
import Layout from "../layout";
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';

// Set the API base URL from the environment variable


axios.defaults.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;
const AUTH0_DOMAIN = process.env.NEXT_PUBLIC_AUTH0_DOMAIN || '';
const AUTH0_CLIENT_ID = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || '';



if (!AUTH0_CLIENT_ID || !AUTH0_DOMAIN) {
  throw new Error(
    'Please define AUTH0_CLIENT_ID and AUTH0_DOMAIN in your .env.local file',
  );
}

export default function App({ Component, pageProps }: AppProps) {
  return withTheme(
    <Layout>
      <Auth0Provider
        domain={AUTH0_DOMAIN}
        clientId={AUTH0_CLIENT_ID}
        authorizationParams={{
          redirect_uri:
            process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI ||
            'http://localhost:3000',
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,

        }}
        cacheLocation="localstorage"
      >
        <AuthProviderSetup>
          <Component {...pageProps} />
        </AuthProviderSetup>
      </Auth0Provider>
    </Layout>
  );
}

const AuthProviderSetup = ({ children }) => {
  const { getAccessTokenSilently, isAuthenticated, loginWithRedirect } = useAuth0();

  const fetchAccessToken = async () => {
    if (isAuthenticated) {
      try {
        const { access_token } = await getAccessTokenSilently({
          detailedResponse: true,
        });
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      } catch (error) {
        console.error('Error fetching access token:', error);
      }
    }
  };

  // Fetch access token on component mount
  fetchAccessToken();

  return <>{children}</>;
};
