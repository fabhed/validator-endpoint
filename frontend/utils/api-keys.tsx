export function generateCurlCommand({
  prompt,
  apiKey,
  url,
  uids,
  top_n,
}: {
  prompt: string;
  apiKey: string;
  url: string;
  uids?: number[];
  top_n?: number;
}) {
  const body = {
    messages: [{ role: "user", content: prompt }],
    uids,
    top_n,
  };
  const curlCommand = `curl ${url}/chat \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Endpoint-Version: 2023-05-19" \\
  -d '${JSON.stringify(body, undefined, " ")}'`;
  return curlCommand;
}
