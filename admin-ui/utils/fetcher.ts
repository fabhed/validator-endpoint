import axios from "axios";

// Fetcher function for use with SWR
const fetcher = (url: string) => axios.get(url).then((res) => res.data);

export default fetcher;
