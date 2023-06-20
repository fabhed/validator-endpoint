export function generateCurlCommand({
  prompt,
  apiKey,
  url,
  uid,
}: {
  prompt: string;
  apiKey: string;
  url: string;
  uid?: number;
}) {
  const body = { messages: [{ role: "user", content: prompt }], uid };
  const curlCommand = `curl ${url}/chat \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Endpoint-Version: 2023-05-19" \\
  -d '${JSON.stringify(body, undefined, " ")}'`;
  return curlCommand;
}
