import { createResettableStore } from "../../../api/createResettableStore";
import {
  ChatApiError,
  chatRequest,
  chatStreamMessage,
} from "../../../api/chatClient";
import type {
  ChatConversation,
  ChatConversationDetail,
  ChatMessage,
  ChatOptions,
} from "../models";

interface ChatState {
  // collections and LLMs of the user's group
  options: ChatOptions | null;
  optionsError: string;
  loadOptions: () => Promise<void>;

  // sidebar
  conversations: ChatConversation[];
  loadConversations: () => Promise<void>;
  renameConversation: (conv_id: number, title: string) => Promise<void>;
  deleteConversation: (conv_id: number) => Promise<void>;

  // the open conversation; null while composing a new chat
  conv: ChatConversation | null;
  messages: ChatMessage[];
  loadingConv: boolean;
  openConversation: (conv_id: number) => Promise<boolean>;
  newChat: () => void;

  // choices for the next message
  draftGvdbsId: number | null; // collection of a chat not yet started
  setDraftGvdbsId: (gvdbs_id: number) => void;
  gllmsId: number | null; // LLM for the next turn
  setGllmsId: (gllms_id: number) => void;

  // the answer being written
  streaming: boolean;
  pendingUser: string | null; // the message just sent, until stored rows arrive
  streamText: string;
  statusText: string;
  sendError: string;
  clearSendError: () => void;
  send: (
    text: string,
    onCreated: (conv_id: number) => void,
  ) => Promise<boolean>;
  stop: () => void;
}

// Kept outside the store: an AbortController is not state to render from.
let abortController: AbortController | null = null;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function errorText(e: unknown): string {
  if (e instanceof ChatApiError) return e.message;
  return "Unexpected error";
}

export const useChatStore = createResettableStore<ChatState>((set, get) => ({
  options: null,
  optionsError: "",
  loadOptions: async () => {
    try {
      const options = await chatRequest<ChatOptions>("GET", "/options");
      set({ options, optionsError: "" });
      // defaults for a new chat
      if (get().draftGvdbsId === null && options.collections.length)
        set({ draftGvdbsId: options.collections[0].gvdbs_id });
      if (get().gllmsId === null && options.llms.length) {
        const usable = options.llms.find((m) => m.gllms_status !== "danger");
        set({ gllmsId: (usable || options.llms[0]).gllms_id });
      }
    } catch (e) {
      set({ optionsError: errorText(e) });
    }
  },

  conversations: [],
  loadConversations: async () => {
    try {
      const conversations = await chatRequest<ChatConversation[]>(
        "GET",
        "/conversations",
      );
      set({ conversations });
    } catch {
      /* the sidebar keeps what it has; the page shows optionsError if the service is down */
    }
  },
  renameConversation: async (conv_id, title) => {
    const updated = await chatRequest<ChatConversation>(
      "PATCH",
      `/conversations/${conv_id}`,
      { title },
    );
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.conv_id === conv_id ? updated : c,
      ),
      conv: state.conv?.conv_id === conv_id ? updated : state.conv,
    }));
  },
  deleteConversation: async (conv_id) => {
    await chatRequest("DELETE", `/conversations/${conv_id}`);
    set((state) => ({
      conversations: state.conversations.filter((c) => c.conv_id !== conv_id),
    }));
  },

  conv: null,
  messages: [],
  loadingConv: false,
  openConversation: async (conv_id) => {
    set({ loadingConv: true, sendError: "" });
    try {
      const detail = await chatRequest<ChatConversationDetail>(
        "GET",
        `/conversations/${conv_id}`,
      );
      const { messages, ...conv } = detail;
      set({ conv, messages, loadingConv: false });
      // continue with the LLM this conversation last used, if still offered
      const llms = get().options?.llms || [];
      if (llms.some((m) => m.gllms_id === conv.gllms_id))
        set({ gllmsId: conv.gllms_id });
      return true;
    } catch {
      set({ loadingConv: false });
      return false;
    }
  },
  newChat: () => set({ conv: null, messages: [], sendError: "" }),

  draftGvdbsId: null,
  setDraftGvdbsId: (gvdbs_id) => set({ draftGvdbsId: gvdbs_id }),
  gllmsId: null,
  setGllmsId: (gllms_id) => set({ gllmsId: gllms_id }),

  streaming: false,
  pendingUser: null,
  streamText: "",
  statusText: "",
  sendError: "",
  clearSendError: () => set({ sendError: "" }),

  send: async (text, onCreated) => {
    const content = text.trim();
    const { gllmsId, draftGvdbsId, streaming } = get();
    if (!content || streaming) return false;
    if (!gllmsId) {
      set({ sendError: "Choose an LLM" });
      return false;
    }
    set({ sendError: "" });

    // The first message of a new chat creates the conversation; its
    // collection is fixed from here on.
    let conv = get().conv;
    if (!conv) {
      if (!draftGvdbsId) {
        set({ sendError: "Choose a document collection" });
        return false;
      }
      try {
        conv = await chatRequest<ChatConversation>("POST", "/conversations", {
          gvdbs_id: draftGvdbsId,
          gllms_id: gllmsId,
        });
      } catch (e) {
        set({ sendError: errorText(e) });
        return false;
      }
      set((state) => ({
        conv,
        messages: [],
        conversations: [conv as ChatConversation, ...state.conversations],
      }));
      onCreated(conv.conv_id);
    }
    const conv_id = conv.conv_id;

    abortController = new AbortController();
    const controller = abortController;
    set({
      streaming: true,
      pendingUser: content,
      streamText: "",
      statusText: "",
    });
    let refused = false;
    try {
      await chatStreamMessage(
        conv_id,
        content,
        gllmsId,
        {
          onStatus: (statusText) => set({ statusText }),
          onToken: (t) =>
            set((state) => ({ streamText: state.streamText + t })),
          onDone: () => {},
          onError: () => {}, // the stored error message is shown after the reload below
        },
        controller.signal,
      );
    } catch (e) {
      // Refused before anything was stored (busy, LLM not ready, ...), or the
      // connection failed. Stored rows, if any, still arrive with the reload.
      refused = true;
      set({ sendError: errorText(e) });
    }

    // Replace the provisional bubbles with the stored rows. After a stop the
    // service saves the partial answer a moment after the stream closes, so
    // wait until the answer row is there.
    const wasStopped = controller.signal.aborted;
    for (let attempt = 0; attempt < 5; attempt++) {
      if (wasStopped) await sleep(700);
      try {
        const detail = await chatRequest<ChatConversationDetail>(
          "GET",
          `/conversations/${conv_id}`,
        );
        const last = detail.messages[detail.messages.length - 1];
        const settled = refused || !last || last.role === "assistant";
        if (settled || attempt === 4) {
          if (get().conv?.conv_id === conv_id) {
            const { messages, ...fresh } = detail;
            set({ conv: fresh, messages });
          }
          break;
        }
      } catch {
        break;
      }
      if (!wasStopped) await sleep(700);
    }
    if (abortController === controller) abortController = null;
    set({ streaming: false, pendingUser: null, streamText: "", statusText: "" });
    get().loadConversations(); // title and order may have changed
    return !refused;
  },

  stop: () => {
    abortController?.abort();
  },
}));
