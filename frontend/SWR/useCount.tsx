import useSWR from "swr";
import fetcher from "../utils/fetcher";

interface CommonFilters {
  key?: string;
  responder_hotkey?: string;
  is_api_success?: boolean;
  is_success?: boolean;
  start?: number;
  end?: number;
  unique_api_keys?: boolean;
}

export const useCount = (filters: CommonFilters) => {
  const queryString = Object.keys(filters)
    .map(
      (key) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(
          filters[key as keyof CommonFilters] || ""
        )}`
    )
    .join("&");

  const {
    data: countData,
    error,
    isLoading,
  } = useSWR(`/admin/logs/count?${queryString}`, fetcher);

  return {
    count: countData?.count,
    isLoading: isLoading,
    error,
  };
};
