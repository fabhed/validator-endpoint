// API Key In Database
interface ApiKeyInDB {
  id: number;
  api_key: string;
  api_key_hint: string;
  name: string;
  request_count: number;
  valid_until: number;
  credits: number;
  enabled: boolean;
  rate_limits: string;
  created_at: number;
  updated_at: number;
}

// Message
interface Message {
  role: "user" | "system" | "assistant";
  content: string;
}

// Body for Chat Post
interface BodyChatChatPost {
  uid: number;
  messages: Message[];
}

// Body for creating API Key
interface BodyCreateApiKeyAdminApiKeysPost {
  name: string;
  valid_until: number;
  credits: number;
  enabled: boolean;
}

// Body for editing API Key
interface BodyEditApiKeyAdminApiKeysQueryPatch {
  api_key_hint: string;
  name: string;
  request_count: number;
  valid_until: string;
  credits: number;
  enabled: boolean;
}

// Chat Response
interface ChatResponse {
  choices: ResponseMessage[];
}

// Config Value
interface ConfigValue {
  key: string;
  value: string;
}

// HTTP Validation Error
interface HTTPValidationError {
  detail: ValidationError[];
}

// Log Entry
export interface RequestLogEntry {
  api_key: string;
  timestamp: number;
  responder_hotkey: string;
}

// Rate Limit Entry
export interface RateLimitEntry {
  times: number;
  seconds: number;
}

// Response Message
interface ResponseMessage {
  index: number;
  responder_hotkey: string;
  message: Message;
}

// Validation Error
interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export {};
