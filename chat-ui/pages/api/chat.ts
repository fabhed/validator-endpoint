import {
  DEFAULT_SYSTEM_PROMPT,
  VALIDATOR_ENDPOINT_BASE_URL,
} from '@/utils/app/const';

import { ChatBody, Message } from '@/types/chat';

export const config = {
  runtime: 'edge',
};

export class ValidatorEndpointError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidatorEndpointError';
  }
}

const handler = async (req: Request): Promise<Response> => {
  try {
    const { messages, key, prompt } = (await req.json()) as ChatBody;

    let messagesToSend: Message[] = [];

    for (let i = messages.length - 1; i >= 0; i--) {
      const message = messages[i];
      messagesToSend = [message, ...messagesToSend];
    }

    const url = VALIDATOR_ENDPOINT_BASE_URL + '/conversation';
    const body = {
      messages: [
        {
          role: 'system',
          content: prompt || DEFAULT_SYSTEM_PROMPT,
        },
        ...messages,
      ],
      top_n: 1,
    };
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${key}`,
      },
      method: 'POST',
      body: JSON.stringify(body),
    });

    if (res.status !== 200) {
      const json = await res.json();
      throw new ValidatorEndpointError(json?.detail || 'Unknown error');
    }
    const text = await res.text();
    return new Response(text);
  } catch (error) {
    console.error(error);
    if (error instanceof ValidatorEndpointError) {
      return new Response('Error', { status: 500, statusText: error.message });
    } else {
      return new Response('Error', { status: 500 });
    }
  }
};

export default handler;
