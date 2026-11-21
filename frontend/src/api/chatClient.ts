import { API_URL } from "./apiURL";
import { useLoggedUserStore } from "../stores/useLoggedUserStore";

// The chat service is a separate process. Behind the reverse proxy it shares
// the web app's origin; in a local run the web app reports the port it listens
// on (users/me -> chat_service_port) and the browser calls it directly.
function chatBaseURL(): string {
  const port = useLoggedUserStore.getState().chat_service_port;
  if (port)
    return `${window.location.protocol}//${window.location.hostname}:${port}${API_URL}/chat`;
  return `${API_URL}/chat`;
}

export class ChatApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function errorFrom(res: Response): Promise<ChatApiError> {
  let detail = `HTTP ${res.status}`;
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") detail = body.detail;
  } catch {
    /* no JSON body */
  }
  return new ChatApiError(res.status, detail);
}

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.replace("/");
    throw new ChatApiError(401, "Not logged in");
  }
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    Accept: "application/json",
  };
}

export async function chatRequest<T>(
  method: "GET" | "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(chatBaseURL() + path, {
      method,
      headers: authHeaders(),
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ChatApiError(0, "The chat service cannot be reached");
  }
  if (res.status === 401) {
    window.location.replace("/");
    throw new ChatApiError(401, "Not logged in");
  }
  if (!res.ok) throw await errorFrom(res);
  return (await res.json()) as T;
}

export interface ChatDoneEvent {
  msg_id: number;
  status: string;
  retrieval_query: string | null;
  tokens_in: number | null;
  tokens_out: number | null;
  seconds: number | null;
  title: string | null;
}

export interface ChatStreamHandlers {
  onStatus: (text: string) => void;
  onToken: (text: string) => void;
  onDone: (data: ChatDoneEvent) => void;
  onError: (text: string) => void;
}

// Send a message and read the answer as it is written (server-sent events
// over fetch: EventSource cannot send the Authorization header).
// Aborting `signal` closes the stream, which is how an answer is stopped.
export async function chatStreamMessage(
  conv_id: number,
  content: string,
  gllms_id: number,
  handlers: ChatStreamHandlers,
  signal: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${chatBaseURL()}/conversations/${conv_id}/messages`, {
      method: "POST",
      headers: { ...authHeaders(), Accept: "text/event-stream" },
      body: JSON.stringify({ content, gllms_id }),
      signal,
    });
  } catch (e) {
    if (signal.aborted) return;
    throw new ChatApiError(0, "The chat service cannot be reached");
  }
  if (!res.ok || !res.body) throw await errorFrom(res);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const dispatch = (block: string) => {
    let event = "";
    let data = "";
    for (const line of block.split("\n")) {
      if (line.startsWith("event: ")) event = line.slice(7).trim();
      else if (line.startsWith("data: ")) data += line.slice(6);
    }
    if (!event || !data) return;
    const parsed = JSON.parse(data);
    if (event === "status") handlers.onStatus(parsed.text);
    else if (event === "token") handlers.onToken(parsed.t);
    else if (event === "done") handlers.onDone(parsed);
    else if (event === "error") handlers.onError(parsed.text);
  };
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let end = buffer.indexOf("\n\n");
      while (end !== -1) {
        dispatch(buffer.slice(0, end));
        buffer = buffer.slice(end + 2);
        end = buffer.indexOf("\n\n");
      }
    }
  } catch (e) {
    if (signal.aborted) return; // stopped by the user
    throw new ChatApiError(0, "The connection to the chat service was lost");
  }
}
