export interface ChatCollection {
  gvdbs_id: number;
  gvdbs_name: string;
  gvdbs_status: string;
  // filter schema of the collection (JSON string; "{}" when it has none)
  gvdbs_retr_filters: string;
}

export interface ChatLLM {
  gllms_id: number;
  gllms_name: string;
  gllms_status: string;
}

export interface ChatOptions {
  collections: ChatCollection[];
  llms: ChatLLM[];
}

export interface ChatFilterValue {
  rf_field_id: string;
  values_list: string[];
  short_title?: string;
}

export interface ChatFilters {
  global_not_value?: boolean | null;
  values: ChatFilterValue[];
}

export interface ChatConversation {
  conv_id: number;
  title: string;
  gvdbs_id: number;
  gllms_id: number;
  filters: ChatFilters | null;
  created_at: string;
  updated_at: string;
}

export type ChatMessageStatus = "complete" | "stopped" | "error";

export interface ChatMessage {
  msg_id: number;
  seqn: number;
  role: "user" | "assistant";
  content: string;
  status: ChatMessageStatus;
  gllms_id: number | null;
  retrieval_query: string | null;
  tokens_in: number | null;
  tokens_out: number | null;
  seconds: number | null;
  created_at: string;
}

export interface ChatConversationDetail extends ChatConversation {
  messages: ChatMessage[];
}
