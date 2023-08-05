import "../public/antd.min.css";
import "../styles/globals.css";
import type { AppProps } from "next/app";
import withTheme from "../theme";

import axios from "axios";
import Layout from "../layout";

// Set the API base URL from the environment variable
axios.defaults.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function App({ Component, pageProps }: AppProps) {
  return withTheme(
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}
