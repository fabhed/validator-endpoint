import React, { useState } from 'react';
import toast from 'react-hot-toast';

import Button from '@/components/Button';

import { Input } from './Input';
import { RadioButton } from './RadioButton';

const strToArr = (str: string) =>
  str.length
    ? str
        .replace(/^,+|,+$/g, '')
        .split(',')
        .map(Number)
    : undefined;

function generateCurlCommand({
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
    messages: [{ role: 'user', content: prompt }],
    uids,
    top_n,
  };
  const curlCommand = `curl ${url}/chat \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Endpoint-Version: 2023-05-19" \\
  -d '${JSON.stringify(body, undefined, ' ')}'`;
  return curlCommand;
}

interface APIKeyOperationsProps {
  prompt: string;
  url: string;
  apiKeys: any[];
}

export const APIKeyOperations = ({
  prompt: initialPrompt,
  url,
  apiKeys,
}: APIKeyOperationsProps) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [uids, setUids] = useState('');
  const [top_n, setTopN] = useState(1);
  const [selection, setSelection] = useState('unspecified');
  const [apiKey, setApiKey] = useState('');

  const handleCopyCurl = () => {
    const curlCommand = generateCurlCommand({
      prompt,
      apiKey,
      url,
      uids: selection === 'uids' ? strToArr(uids) : undefined,
      top_n: selection === 'topN' ? top_n : undefined,
    });
    navigator.clipboard.writeText(curlCommand);
    toast.success('Curl command copied to clipboard!');
  };

  return (
    <>
      {!modalVisible ? (
        <Button onClick={() => setModalVisible(true)}>
          Generate curl snippet
        </Button>
      ) : (
        <Button onClick={() => setModalVisible(false)}>
          Close request generator
        </Button>
      )}

      {modalVisible && (
        <div>
          <h2 className="text-2xl">
            Generate a curl snippet to make a request to the API
          </h2>
          <div className="mb-2">
            <label>
              Prompt:
              <Input
                type="text"
                placeholder="Prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </label>
          </div>
          {/* select apiKey */}
          <div className="mb-2">
            <label>
              API Key:
              <select
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full flex-1 rounded-md border border-neutral-600 bg-[#202123] px-4 py-3 pr-10 text-[14px] leading-3 text-white"
                disabled={apiKeys.length === 0}
              >
                {apiKeys.map((apiKey) => (
                  <option key={apiKey.api_key} value={apiKey.api_key}>
                    {`${apiKey.name} (${apiKey.api_key_hint})`}
                  </option>
                ))}
              </select>
            </label>
            {apiKeys.length === 0 && (
              <div className="text-red-500">No API keys found</div>
            )}
          </div>
          <fieldset className="flex gap-2">
            <legend>Query strategy</legend>

            <RadioButton
              label="Top miners"
              id="radio-topN"
              name="query-strategy"
              value="topN"
              checked={selection === 'topN'}
              onChange={(e) => setSelection(e.target.value)}
            />

            <RadioButton
              label="Specific UIDs"
              id="radio-uids"
              name="query-strategy"
              value="uids"
              checked={selection === 'uids'}
              onChange={(e) => setSelection(e.target.value)}
            />

            <RadioButton
              label="Unspecified"
              id="radio-unspecified"
              name="query-strategy"
              value="unspecified"
              checked={selection === 'unspecified'}
              onChange={(e) => setSelection(e.target.value)}
            />
          </fieldset>
          {selection === 'uids' && (
            <Input
              type="text"
              placeholder="UIDs (comma-separated)"
              value={uids}
              onChange={(e) => setUids(e.target.value)}
            />
          )}
          {selection === 'topN' && (
            <Input
              type="number"
              min="1"
              placeholder="Top miners"
              value={top_n}
              onChange={(e) =>
                e.target.value && setTopN(Number(e.target.value))
              }
            />
          )}
          <pre className="relative overflow-auto bg-gray-800 text-white p-4 rounded shadow-md font-mono text-sm my-2">
            {generateCurlCommand({
              prompt,
              apiKey,
              url,
              uids: selection === 'uids' ? strToArr(uids) : undefined,
              top_n: selection === 'topN' ? top_n : undefined,
            })}
            <Button onClick={handleCopyCurl} className="absolute right-1 top-1">
              Copy
            </Button>
          </pre>
        </div>
      )}
    </>
  );
};
