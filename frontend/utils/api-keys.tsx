export function generateCurlCommand({ prompt, apiKey, url }) {
  const curlCommand = `curl ${url}/chat \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Endpoint-Version: 2023-05-19" \\
  -d '{ "messages": [{"role": "user", "content": "${prompt}"}] }'`;
  return curlCommand;
}
