import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";

export default function QueryTokensCounter() {
  const current = useDocTasksCurrentStore();

  const tokensCounterVisible =
    (current.vdb_query_seconds ||
      current.llm_query_seconds ||
      current.llm_tokens_sent ||
      current.llm_tokens_received) !== null;
  function secondsOrNA(seconds: number | null) {
    if (seconds === null) return "N/A";
    return `${seconds} sec`;
  }
  const tokensCounterText = `VectorDB/LLM time: ${secondsOrNA(
    current.vdb_query_seconds
  )} / ${secondsOrNA(current.llm_query_seconds)} Tokens Sent/Recv: ${
    current.llm_tokens_sent || "N/A"
  }/${current.llm_tokens_received || "N/A"}`;
  return (
    <small
      className="m-0 fw-bold"
      style={{ visibility: tokensCounterVisible ? "visible" : "hidden" }}
    >
      {tokensCounterText}
    </small>
  );
}
