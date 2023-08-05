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

    const res = await fetch(VALIDATOR_ENDPOINT_BASE_URL + '/chat', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${key}`,
      },
      method: 'POST',
      body: JSON.stringify({
        messages: [
          {
            role: 'system',
            content: prompt || DEFAULT_SYSTEM_PROMPT,
          },
          ...messages,
        ],
        top_n: 1,
      }),
    });

    const json = await res.json();
    console.log(json);

    if (res.status !== 200) {
      throw new ValidatorEndpointError(json?.detail || 'Unknown error');
    }

    return new Response(json);
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
